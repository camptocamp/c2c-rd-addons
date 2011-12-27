# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import wizard
from osv import osv, fields
from tools.translate import _

## Create an invoice based on selected timesheet lines
#

#
# TODO: check unit of measure !!!
#
class hr_timesheet_invoice_create(osv.osv_memory):

    _inherit = 'hr.timesheet.invoice.create'
    _columns = \
        { 'date_invoice' : fields.date
            ( 'Date Invoice'
            , help='The date of the invoice or emtpy will take the current day on validate'
            )
        , 'description'  : fields.char
            ( 'Prefix Invoice Text'
            , size=16
            , help='This text will be placed before the name of the analytic account instead of the current date'
            )
        , 'reference'    : fields.char
            ( 'Reference'
            , size=64
            , help='The reference on the invoice, usually the period of service'
            )
        }
    _defaults = {'description' : lambda *a: time.strftime('%d/%m/%Y')}

    def do_create(self, cr, uid, ids, context=None) :
        if context is None : context = {}
        mod_obj              = self.pool.get('ir.model.data')
        invoice_factor_obj   = self.pool.get('hr_timesheet_invoice.factor')
        res_partner_obj      = self.pool.get('res.partner')
        product_obj          = self.pool.get('product.product')
        pro_price_obj        = self.pool.get('product.pricelist')
        product_uom_obj      = self.pool.get('product.uom')
        act_obj              = self.pool.get('ir.actions.act_window')
        invoice_obj          = self.pool.get('account.invoice')
        invoice_line_obj     = self.pool.get('account.invoice.line')
        analytic_account_obj = self.pool.get('account.analytic.account')
        fiscal_pos_obj       = self.pool.get('account.fiscal.position')
        account_analytic_line_obj = self.pool.get('account.analytic.line')
        account_payment_term_obj  = self.pool.get('account.payment.term')

        invoices = []
        data = self.read(cr, uid, ids, [], context=context)[0]

        account_ids = \
            ( l.account_id.id 
                for l in account_analytic_line_obj.browse(cr, uid, context['active_ids'], context=context)
            )

        for account in analytic_account_obj.browse(cr, uid, list(set(account_ids)), context=context) :
            partner = account.partner_id
            if (not partner) or not (account.pricelist_id):
                raise osv.except_osv \
                    ( _('Analytic Account incomplete')
                    , _('Please fill in the Partner or Customer and Sale Pricelist fields in the Analytic Account:\n%s') 
                        % account.name
                    )
            if not partner.address:
                raise osv.except_osv \
                    ( _('Partner incomplete')
                    , _('Please fill in the Address field in the Partner: %s.') % (partner.name,)
                    )
            date_due = False
            if partner.property_payment_term:
                pterm_list = account_payment_term_obj.compute \
                    ( cr, uid
                    , partner.property_payment_term.id
                    , value=1
                    , date_ref=time.strftime('%Y-%m-%d')
                    )
                if pterm_list:
                    pterm_list = [line[0] for line in pterm_list]
                    pterm_list.sort()
                    date_due = pterm_list[-1]
            prefix = data['description'] or time.strftime('%d/%m/%Y')
                
            curr_invoice = \
                { 'name'               : prefix + ' - ' + account.name
                , 'date_invoice'       : data['date_invoice'] or False
                , 'reference'          : data['reference'] or False
                , 'partner_id'         : account.partner_id.id
                , 'address_contact_id' : res_partner_obj.address_get
                    (cr, uid, [account.partner_id.id], adr_pref=['contact'])['contact']
                , 'address_invoice_id' : res_partner_obj.address_get
                    (cr, uid, [account.partner_id.id], adr_pref=['invoice'])['invoice']
                , 'payment_term'       : partner.property_payment_term.id or False
                , 'account_id'         : partner.property_account_receivable.id
                , 'currency_id'        : account.pricelist_id.currency_id.id
                , 'date_due'           : date_due
                , 'fiscal_position'    : account.partner_id.property_account_position.id
                , 'state'              : 'draft'
                }
            last_invoice_id = invoice_obj.create(cr, uid, curr_invoice, context=context)
            invoices.append(last_invoice_id)

            context2 = context.copy()
            context2['lang'] = partner.lang
            cr.execute("SELECT product_id, to_invoice, sum(unit_amount) "
                    "FROM account_analytic_line as line "
                    "WHERE account_id=%s "
                        "AND id IN %s AND to_invoice IS NOT NULL "
                    "GROUP BY product_id, to_invoice", (account.id, tuple(context['active_ids']),))

            for product_id, factor_id, qty in cr.fetchall() :
                product = product_obj.browse(cr, uid, product_id, context2)
                if not product:
                    raise osv.except_osv(_('Error'), _('At least one line has no product !'))
                factor_name = ''
                factor = invoice_factor_obj.browse(cr, uid, factor_id, context2)

                if not data['product'] :
                    if factor.customer_name :
                        factor_name = product.name + ' - ' + factor.customer_name
                    else:
                        factor_name = product.name
                else:
                    factor_name = product_obj.name_get(cr, uid, [data['product']], context=context)[0][1]

                if account.pricelist_id :
                    pl = account.pricelist_id.id
                    price = pro_price_obj.price_get \
                        (cr,uid,[pl], data['product'] or product_id, qty or 1.0, account.partner_id.id)[pl]
                else:
                    price = 0.0

                taxes = product.taxes_id
                tax = fiscal_pos_obj.map_tax(cr, uid, account.partner_id.property_account_position, taxes)
                account_id = \
                    (   product.product_tmpl_id.property_account_income.id 
                     or product.categ_id.property_account_income_categ.id
                    )
                if not account_id:
                    raise wizard.except_wizard \
                        ( _("Error")
                        , _("""No income account defined for product: " %s" """) % product.name
                        )

                curr_line = \
                    { 'price_unit'          : price
                    , 'quantity'            : qty
                    , 'discount'            : factor.factor
                    , 'invoice_line_tax_id' : [(6, 0, tax )]
                    , 'invoice_id'          : last_invoice_id
                    , 'name'                : factor_name
                    , 'product_id'          : data['product'] or product_id
                    , 'invoice_line_tax_id' : [(6, 0, tax)]
                    , 'uos_id'              : product.uom_id.id
                    , 'account_id'          : account_id
                    , 'account_analytic_id' : account.id
                    }

                #
                # Compute for lines
                #
                cr.execute("SELECT * FROM account_analytic_line WHERE account_id = %s and id IN %s AND product_id=%s and to_invoice=%s ORDER BY account_analytic_line.date", (account.id, tuple(context['active_ids']), product_id, factor_id))

                line_ids = cr.dictfetchall()
                note = []
                for line in line_ids:
                    # set invoice_line_note
                    details = []
                    if data['date']:
                        details.append(line['date'])
                    if data['time']:
                        if line['product_uom_id']:
                            details.append("%s %s" % (line['unit_amount'], product_uom_obj.browse(cr, uid, [line['product_uom_id']],context2)[0].name))
                        else:
                            details.append("%s" % (line['unit_amount'], ))
                    if data['name']:
                        details.append(line['name'])
                    note.append(u' - '.join(map(lambda x: unicode(x) or '', details)))

                curr_line['note'] = "\n".join(map(lambda x: unicode(x) or '', note))
                invoice_line_obj.create(cr, uid, curr_line, context=context)
                aal_ids = account_analytic_line_obj.search \
                    (cr, uid, [('account_id','=', account.id), ('id', 'IN', tuple(context['active_ids']))])
                account_analytic_line_obj.write(cr, uid, aal_ids, {'invoice_id' : last_invoice_id})

            invoice_obj.button_reset_taxes(cr, uid, [last_invoice_id], context)

        mod_ids = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')], context=context)[0]
        res_id = mod_obj.read(cr, uid, mod_ids, ['res_id'], context=context)['res_id']
        act_win = act_obj.read(cr, uid, res_id, [], context=context)
        act_win['domain'] = [('id', 'in', invoices), ('type', '=', 'out_invoice')]
        act_win['name']   = _('Invoices')
        return act_win
    # end def do_create

    def do_create(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_obj = self.pool.get('account.analytic.line')
        mod_obj  = self.pool.get('ir.model.data')
        act_obj  = self.pool.get('ir.actions.act_window')
        inv_obj  = self.pool.get('account.invoice')

        inv_ids = line_obj.invoice_cost_create(cr, uid, context['active_ids'], data, context=context)
        for inv in inv_obj.browse(cr, uid, inv_ids) : 
            values = \
                { 'name'         : data['description'] + ' - ' + inv.invoice_line[0].account_analytic_id.name
                , 'date_invoice' : data['date_invoice'] or False
                , 'reference'    : data['reference'] or False
                }
            inv_obj.write(cr, uid, [inv.id], values)
        mod_ids = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')], context=context)[0]
        res_id = mod_obj.read(cr, uid, mod_ids, ['res_id'], context=context)['res_id']
        act_win = act_obj.read(cr, uid, res_id, [], context=context)
        act_win['domain'] = [('id','in',inv_ids),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win
    # end def do_create
hr_timesheet_invoice_create()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
