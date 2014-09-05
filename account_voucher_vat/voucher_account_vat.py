# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
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
from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import logging

class account_voucher_vat(osv.osv):
    _inherit = 'account.voucher'

    _columns = {
         'type':fields.selection([
            ('sale','Sale'),
            ('purchase','Purchase'),
            ('payment','Payment'),
            ('receipt','Receipt'),
            ('gen_vat','General Vat'),
        ],'Default Type', readonly=True, states={'draft':[('readonly',False)]}),
        }
    
    _defaults = {
        'type': 'gen_vat'
        }

    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        _logger = logging.getLogger(__name__)
        _logger.debug('FGF voucher start  %s ', line_total)
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        voucher_brw = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context)
        ctx = context.copy()
        ctx.update({'date': voucher_brw.date})
        for line in voucher_brw.line_ids:
            #create one move line per voucher line where amount is not 0.0
            if not line.amount:
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher_brw.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                currency_rate_difference = line.move_line_id.amount_residual - amount
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher_brw.journal_id.id,
                'period_id': voucher_brw.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher_brw.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher_brw.date
            }
            
            amount_net = line.amount_net
            if amount > 0:
                move_line['debit'] = amount_net or amount
            else:               
                move_line['credit'] = -amount_net or -amount
            tot_line += amount_net or amount
            
            if voucher_brw.tax_id and voucher_brw.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher_brw.tax_id.id,
                })
            _logger.debug('FGF voucher tot_line %s ', tot_line)                
            move_line_tax = {}
            if line.tax_id and line.voucher_id.type == ('gen_vat'):
                
                move_line.update({
                    'tax_code_id': line.tax_id.base_code_id.id,
                    'tax_amount' : amount_net,

                })
                
                move_line_tax = move_line.copy()
                debit_tax = credit_tax = 0
                if amount > 0:
                    debit_tax = line.amount_tax
                else:
                    credit_tax = -line.amount_tax
                move_line_tax.update({
                    'tax_code_id': line.tax_id.tax_code_id.id,
                    'tax_amount' : line.amount_tax,
                    'debit'      : debit_tax,
                    'credit'     : credit_tax,
                    'account_id' : line.tax_id.account_collected_id.id,
                })
                tot_line += debit_tax - credit_tax
                _logger.debug('FGF voucher tot_line tax %s ', tot_line)     
                

            #if move_line.get('account_tax_id', False):
                #tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                #if not (tax_data.base_code_id and tax_data.tax_code_id):
                    #raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                voucher_currency = voucher_brw.currency_id and voucher_brw.currency_id.id or voucher_brw.journal_id.company_id.currency_id.id
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency. 
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    elif line.move_line_id.currency_id.id == voucher_brw.payment_rate_currency_id.id:
                        # if the rate is specified on the voucher, we must use it
                        voucher_rate = currency_obj.browse(cr, uid, voucher_currency, context=ctx).rate
                        amount_currency = (move_line['debit'] - move_line['credit']) * voucher_brw.payment_rate * voucher_rate
                    else:
                        # otherwise we use the rates of the system (giving the voucher date in the context)
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled and line.move_line_id.currency_id.id == voucher_currency:
                    sign = voucher_brw.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            _logger.debug('FGF voucher move line %s ', move_line)
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]
            if move_line_tax:
                _logger.debug('FGF voucher move line tax %s ', move_line_tax)
                voucher_line_tax = move_line_obj.create(cr, uid, move_line_tax)
            
            

            if not currency_obj.is_zero(cr, uid, voucher_brw.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)

            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        _logger.debug('FGF voucher %s %s', tot_line, rec_lst_ids)

        return (tot_line, rec_lst_ids)

        

    def action_move_line_create(self, cr, uid, ids, context=None):
        res = super(account_voucher_vat, self).action_move_line_create(cr, uid, ids, context)
        aml_obj = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context):
            for line in voucher.move_id.line_id:
                if  line.debit == 0 and line.credit == 0:
                    aml_obj.unlink(cr, uid, [line.id])
        return res


account_voucher_vat()

class account_voucher_vat_line(osv.osv):
    _inherit = "account.voucher.line"
    _logger = logging.getLogger(__name__)
    _columns = {
        'debit': fields.float('Debit',  digits_compute=dp.get_precision('Account'),
            help="""Amount incl VAT"""),
        'credit': fields.float('Credit',  digits_compute=dp.get_precision('Account'),
            help="""Amount incl VAT"""),
        'tax_id': fields.many2one("account.tax","Tax",
            help="VAT for this line, only allowed if no partner specified"),
        'amount_net': fields.float('Amount Net',  digits_compute=dp.get_precision('Account'),
            help="""Amount Net"""),
        'amount_tax': fields.float('Amount Tax',  digits_compute=dp.get_precision('Account'),
            help="""Amount Tax"""),
    }
        
    # may be this is not needed
    def FIXME_onchange_partner_id(self, cr, uid, line_id, partner_id, type, currency_id,
            context={}):
        if not partner_id:
            return {}
        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')

        company_currency_id = res_users_obj.browse(cr, uid, user,
                context=context).company_id.currency_id.id

        if not currency_id:
            currency_id = company_currency_id

        part = self.pool.get('res.partner').browse(cr, uid, partner_id,
                context=context)

        # quick FIXME check what partner is defined in partner and override input
        if type == 'partner' :  # trigger runs from partner
            type = 'general'
            if not part.supplier and not part.customer :
                print 'Partner should be customer and/or supplier'

            if part.supplier == True and part.customer == True :
                #type = '' # manual entry necessary FIXME - currently general remains in this case visible - no way to get the select field empty
                type = 'general'
                print 'Wizard missing - User has to choose category'
            else:
                if part.supplier == True :
                    type = 'supplier'
                if part.customer == True :
                    type = 'customer'

        account_id = ''
        if type == 'supplier':
            account_id = part.property_account_payable.id
        if type == 'customer':
            account_id =  part.property_account_receivable.id

        balance = 0.0
        if account_id:
            cr.execute('SELECT sum(debit-credit) \
                FROM account_move_line \
                WHERE (reconcile_id is null) \
                    AND partner_id = %s \
                    AND account_id=%s', (partner_id, account_id))
            res = cr.fetchone()
            balance = res and res[0] or 0.0

            balance = res_currency_obj.compute(cr, uid, company_currency_id,
                currency_id, balance, context=context)

        return {'value': {'amount': balance, 'account_id': account_id,'type': type,
                 'tax_id':'', 'amount_tax':'', 'amount_net':'' }}

    def onchange_dc(self, cr, uid, ids, debit, credit):
        value = {}
        if debit:
            return {'value' : {'amount': debit-credit, 'credit':0}}
        else:
            return {'value' : {'amount': debit-credit, 'debit':0}}

    def onchange_voucher_tax(self, cr, uid, ids, tax_id, amount ,partner_id=None):
        result = {}
        amount_net = 0.0
        amount_tax = 0.0
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        self._logger.debug('prec `%s`', precision)
        if tax_id:
            if partner_id:
                #raise osv.except_osv(_('Error!'),
                #  _('VAT not allowed for moves lines with partner'))
                tax_id = ''
            else:
                tax_obj = self.pool.get('account.tax').browse(cr, uid,tax_id)
                if tax_obj.type == 'percent':  # and tax_obj.tax_group == 'vat': -- tax_group does not exist any more
                    amount_net = round(amount / (1 + tax_obj.amount), precision)
                    amount_tax = amount - amount_net
                else:
                    raise osv.except_osv(_('Error!'),
                       _('only tax group VAT with percentage supported'))
        result = {'value': {
            
            'amount_net': amount_net,
            'amount_tax': amount_tax,
            }
        }
        return result
    
    def onchange_amount(self, cr, uid, ids, tax_id, amount, partner_id, date, date_statement):
        result = {}
        value = {}
        if tax_id:
            result = self.onchange_tax(cr, uid, ids, tax_id, amount, partner_id)
            value = result.get('value') 
            self._logger.debug('r1 `%s` `%s`', result, value)
        
        if not date:
            # FIXME not nice
            #v2 = { 'value' : {'date': date_statement}}
            #v2a = v2.get('value')
            #v1.update(v2a)
            value['date']  =  date_statement
        self._logger.debug('r2 `%s`', value)
        return {'value' : value }
        
    def onchange_account(self, cr, uid, ids, account_id,tax_id, amount, partner_id):
        if not account_id: return {}
        result = {}
        account_obj = self.pool.get('account.account').browse(cr, uid,account_id)
        tax_id = ''
        if len(account_obj.tax_ids) == 1:
            self._logger.debug('tax_ids `%s`', account_obj.tax_ids)
            for tax_rec in account_obj.tax_ids:
                tax_id = tax_rec.id                
            result = {'value': {
                'tax_id': tax_id,
            }
            }
            if tax_id:
               result = self.onchange_tax(cr, uid, ids, tax_id, amount, partner_id)
        
        return result


    def onchange_tax(self, cr, uid, ids, tax_id, amount ,partner_id):
        result = {}
        amount_net = 0.0
        amount_tax = 0.0
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        self._logger.debug('prec `%s`', precision)
        if tax_id:
            if partner_id:
                #raise osv.except_osv(_('Error!'),
                #  _('VAT not allowed for moves lines with partner'))
                tax_id = ''
            else:
                tax_obj = self.pool.get('account.tax').browse(cr, uid,tax_id)
                if tax_obj.type == 'percent':  # and tax_obj.tax_group == 'vat': -- tax_group does not exist any more
                    amount_net = round(amount / (1 + tax_obj.amount), precision)
                    amount_tax = amount - amount_net
                else:
                    raise osv.except_osv(_('Error!'),
                       _('only tax group VAT with percentage supported'))
        result = {'value': {
            'tax_id': tax_id,
            'amount_net': amount_net,
            'amount_tax': amount_tax,
            }
        }
        return result
        
account_voucher_vat_line()
