# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

 
import netsvc
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _



class account_move(osv.osv):
    _inherit = "account.move"


def discount_post(self, cr, uid, ids, date, journal_id, amount_paid, reconcile_id, reconcile='full', context=None):
        """
        Returns a list of ids 
        result format: [id, ... ]

        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: move for wich the discount move has to be generated
        @param amount_paid negative for out payments, positive for in payments
        @param reconcile full or partial
        @param context: context arguments, like lang, time zone

        @return: List of acount_move_line ids which have to be reconciled
        """
        res = []
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = invoice_obj.search(cr, uid, [('move_id','in', ids)])
        if not invoice_ids:
           return res
        for invoice in invoice_obj(cr, uid, invoice_ids)
           if not invoice.payment_id or not invoice.payment_id.is_discount or invoice.residual = 0.0:
               return res
           else:
               inv_num = invoice.number
               if invoice.type in ['in_invoice','out_refund']:
                  to_pay = -invoice.residual
               else:
                  to_pay = invoice.residual
                 
               payment_obj = self.pool.get('account.payment.term')
               for pay_term_lines in payment_obj.browse(cr, uid, invoice.payment_id)
                   if invoice.payment_id.discount_expense_account_id 
                        account_deb = invoice.payment_id.discount_expense_account_id
                   if invoice.payment_id.discount_income_account_id
                        account_cred = invoice.payment_id.discount_income_account_id
         
        account_obj = self.pool.get('account.account')
        partner_account_ids = account_obj.search(cr, uid, [('type','in',['payable','receivable'])]

        open_partner_balance = 0.0

        move = self.read(cr, uid, ids, context)
        partner_id = move.partner_id.id
        for move_line in move:
            if move_line.account_id in partner_account_ids and not move_line.reconcile_id :
                open_partner_balance  += move_line.debit or 0.0 - move_line.credit or 0.0
                partner_account_id = move_line.account_id 
        if open_partner_balance == to_pay + amount_paid or reconcile = 'full':
            reconcile = 'full'
        else:
            reconcile = 'partial'
        # FIXME ratio for partial
        ratio = to_pay / open_partner_balance

        # we have to reverse the amounts 
        sql = "SELECT sum(debit)  as credit, 
                      sum(credit) as debit,
                      sum(-tax_amount) as tax_amount,
                      account_id,
                      analytic_account_id,
                      account_tax_id,
                      account_code_id
                 FROM account_move_line
                WHERE move_id = %d
                  AND account_id not in (%s)
                GROUP BY account_id, analytic_account_id, account_tax_id, tax_code_id" % (move.id, partner_account_ids)

        debit = 0.0
        credit= 0.0
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        move_obj = self.pool.get('account.move')
        move_vals = {
                'ref': inv.reference and inv.reference or inv.name,
                'journal_id': journal_id,
                'date': date,
                'period_id': period_id,
                'narration': _('Discount to ') + inv_num 
           }
        move_id = move_obj.create(cr, uid, move_vals, context=context)

        if amount_paid > 0.0: 
            account_id = account_deb
            partner_deb = 0.0
            partner_cred = abs(open_partner_balance)
        else:
            account_id = account_cred
            partner_deb = abs(open_partner_balance)
            partner_cred = 0.0

        val = {}
        cr.execute(sql)
        # create move lines (except partner)
        for lines in cr.fetchall(): 
             line_vals= {
                'journal_id': journal_id,
                'date': date,
                'period_id': period_id,
                'partner_id': partner_id,
                'name':  '',
                'debit': round(lines.debit * ratio ,prec),
                'credit': round(lines.credit * ratio ,prec),
                'move_id': move_id,
                'account_id': account_id,
             }            
             val.append(line_vals) 
             debit += round(lines.debit * ratio ,prec)
             credit += round(lines.credit * ratio ,prec)
            
            
        # create move line for partner
          
        line_vals= {
                'journal_id': journal_id,
                'date': date,
                'period_id': period_id,
                'partner_id': partner_id,
                'name':  '',
                'debit': partner_deb,
                'credit': partner_cred,
                'move_id': move_id,
                'account_id': partner_account_id,
                'reconcile_id': reconcile_id,
               }
        val.append(line_values) 
   
        # rounding errors
        if round(open_partner_balance,prec) != -round((debit-credit),prec):
            #FIXME - update biggest value
            a=1

        move_line_obj = self.pool.get('account.move.line')
        move_line_ids = move_obj.create(cr, uid, vals, context=context)


        # analytic lines 

account_move()
    
