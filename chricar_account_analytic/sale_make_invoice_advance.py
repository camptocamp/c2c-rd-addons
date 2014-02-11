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
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    _logger = logging.getLogger(__name__)

    def create_invoices_wrong(self, cr, uid, ids, context=None):
        """
             NOT COMPATIBLE WITH V7

             To create invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs if we want more than one
             @param context: A standard dictionary

             @return:

        """
        list_inv = []
        obj_sale = self.pool.get('sale.order')
        obj_lines = self.pool.get('account.invoice.line')
        inv_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}


        for  sale_adv_obj in self.browse(cr, uid, ids, context=context):
            for sale in obj_sale.browse(cr, uid, context.get('active_ids', []), context=context):
                create_ids = []
                ids_inv = []
                if sale.order_policy == 'postpaid':
                    raise osv.except_osv(
                        _('Error'),
                        _("You cannot make an advance on a sales order \
                             that is defined as 'Automatic Invoice after delivery'."))
                val = obj_lines.product_id_change(cr, uid, [], sale_adv_obj.product_id.id,
                        uom = False, partner_id = sale.partner_id.id, fposition_id = sale.fiscal_position.id)

                self._logger.debug('advance val `%s`', val)
                product = self.pool.get('product.product').browse(cr, uid, sale_adv_obj.product_id.id, context)

                line_id = obj_lines.create(cr, uid, {
                    'name': val['value']['name'] or product.name ,
                    'account_id': product.property_account_income.id or product.categ_id.property_account_income_categ.id,
                    'price_unit': sale_adv_obj.amount,
                    'quantity': sale_adv_obj.qtty,
                    'discount': False,
                    'uos_id': val['value']['uos_id'],
                    'product_id': sale_adv_obj.product_id.id,
                    'invoice_line_tax_id': [(6, 0, val['value']['invoice_line_tax_id'])],
                    'account_analytic_id': sale.project_id.id or product.property_account_income.analytic_account_id.id \
                               or product.categ_id.property_account_income_categ.analytic_account_id.id or False,
                    #'note':'',
                })

                create_ids.append(line_id)
                inv = {
                    'name': sale.client_order_ref or sale.name,
                    'origin': sale.name,
                    'type': 'out_invoice',
                    'reference': False,
                    'account_id': sale.partner_id.property_account_receivable.id,
                    'partner_id': sale.partner_id.id,
                    'address_invoice_id': sale.partner_invoice_id.id,
                    'address_contact_id': sale.partner_id.id,
                    'invoice_line': [(6, 0, create_ids)],
                    'currency_id': sale.pricelist_id.currency_id.id,
                    'comment': '',
                    'payment_term': sale.payment_term.id,
                    'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id
                }

                inv_id = inv_obj.create(cr, uid, inv)
                inv_obj.button_reset_taxes(cr, uid, [inv_id], context=context)

                for inv in sale.invoice_ids:
                    ids_inv.append(inv.id)
                ids_inv.append(inv_id)
                obj_sale.write(cr, uid, sale.id, {'invoice_ids': [(6, 0, ids_inv)]})
                list_inv.append(inv_id)

        #
        # If invoice on picking: add the cost on the SO
        # If not, the advance will be deduced when generating the final invoice
        #
                if sale.order_policy == 'picking':
                    self.pool.get('sale.order.line').create(cr, uid, {
                        'order_id': sale.id,
                        'name': val['value']['name'],
                        'price_unit': -sale_adv_obj.amount,
                        'product_uom_qty': sale_adv_obj.qtty,
                        'product_uos_qty': sale_adv_obj.qtty,
                        'product_uos': val['value']['uos_id'],
                        'product_uom': val['value']['uos_id'],
                        'product_id': sale_adv_obj.product_id.id,
                        'discount': False,
                        'tax_id': [(6, 0, val['value']['invoice_line_tax_id'])],
                    }, context)

        context.update({'invoice_id':list_inv})

#        return {
#            'name': 'Open Invoice',
#            'view_type': 'form',
#            'view_mode': 'form',
#            'res_model': 'account.invoice',
#            'type': 'ir.actions.act_window',
#            'target': 'new',
#            'context': context
#        }

        return {
            'name': _('Advance Invoice'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.invoice',
            'res_id': invoice_ids[0],
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': "{'type': 'out_invoice'}",
            'type': 'ir.actions.act_window',
        }



sale_advance_payment_inv()
