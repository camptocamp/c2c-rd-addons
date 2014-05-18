# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
import openerp.addons.decimal_precision as dp
import logging

class account_bank_statement(osv.osv):
    _inherit = "account.bank.statement"

    def create_move_from_st_line(self, cr, uid, st_line_id, company_currency_id, next_number, context=None):
        res = super(account_bank_statement, self).create_move_from_st_line( cr, uid, st_line_id, company_currency_id, next_number, context)

        res_currency_obj = self.pool.get('res.currency')
        account_move_obj = self.pool.get('account.move')
        account_journal_obj = self.pool.get('account.journal')
        account_move_line_obj = self.pool.get('account.move.line')
        account_bank_statement_line_obj = self.pool.get('account.bank.statement.line')
        st_line = account_bank_statement_line_obj.browse(cr, uid, st_line_id, context=context)
        st = st_line.statement_id

        amount_move = st_line.amount
        amount_tax = 0.0
        if st_line.tax_id and st_line.amount_tax != 0.0:
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
            if st_line.amount != round(st_line.amount_net + st_line.amount_tax, precision):
                raise osv.except_osv(_('Error !'),
                    _('VAT and Amount Net do not match Amount in line "%s"') % st_line.name)
            if st_line.partner_id:
                raise osv.except_osv(_('Error !'),
                    _('Lines "%s" with VAT must not have partner account ') % st_line.name)
            amount_net = res_currency_obj.compute(cr, uid, company_currency_id,
                         st.currency.id, st_line.amount_net, context=context)

            amount_tax = amount_move - amount_net

            # update amount to amount_net
            bank_debit_account_id = st_line.statement_id.journal_id.default_debit_account_id.id
            bank_credit_account_id = st_line.statement_id.journal_id.default_credit_account_id.id
            move_ids = account_move_line_obj.search(cr, uid, [('move_id','=',res),('account_id','not in',[bank_debit_account_id,bank_debit_account_id])])
            entry_posted = st_line.statement_id.journal_id.entry_posted
            entry_posted_reset = False
            if not entry_posted:
                # to disable the update check
                account_journal_obj.write(cr, uid, st_line.statement_id.journal_id.id, {'entry_posted':True})
                entry_posted_reset = True
            if not len(move_ids) == 1 :
                raise osv.except_osv(_('Error !'),
                _('must only find one move line %s"') % st_line.name)
            if amount_tax>0:
                account_move_line_obj.write(cr, uid, move_ids, {'credit':amount_net,'tax_amount': amount_net,'tax_code_id': st_line.tax_id.base_code_id.id})
            if amount_tax<0:
                account_move_line_obj.write(cr, uid, move_ids, {'debit':-amount_net,'tax_amount': amount_net,'tax_code_id': st_line.tax_id.base_code_id.id})
            if entry_posted_reset:
                account_journal_obj.write(cr, uid, st_line.statement_id.journal_id.id, {'entry_posted':False})

            # create tax line
            if amount_tax != 0:
                vals = {
                    'name': st_line.name,
                    'date': st_line.date,
                    'ref': st_line.ref,
                    'move_id': res,
                    'partner_id': ((st_line.partner_id) and st_line.partner_id.id) or False,
                    'account_id':  st_line.tax_id.account_collected_id.id,
                    'credit': ((amount_tax>0) and  amount_tax) or 0.0,
                    'debit' : ((amount_tax<0) and -amount_tax) or 0.0,
                    'statement_id': st.id,
                    'journal_id': st.journal_id.id,
                    'period_id': st.period_id.id,
                    'tax_amount': amount_tax,
                    'tax_code_id': st_line.tax_id.tax_code_id.id,
                    } 
                if st.currency.id != st.company_id.currency_id.id :
                    vals['currency_id'] = st.currency.id
                account_move_line_obj.create(cr, uid, vals,context=context)
 

        return res

account_bank_statement()

class account_bank_statement_line(osv.osv):
    _inherit = "account.bank.statement.line"
    _logger = logging.getLogger(__name__)
    _columns = {
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

    def onchange_amount_1(self, cr, uid, ids, tax_id, amount, partner_id, date, date_statement):
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

account_bank_statement_line()
