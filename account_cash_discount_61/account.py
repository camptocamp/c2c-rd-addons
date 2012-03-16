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
import logging

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    _columns = {
         'is_write_off' : fields.boolean('Is Write Off move line'), 
    }

account_move_line()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
 

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        res = super(account_voucher,self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None)
        _logger = logging.getLogger(__name__)
        _logger.info('reconcile - voucher writeoff A voucher_id, move_id: %s %s' % (voucher_id, move_id ))
        _logger.info('reconcile - voucher writeoff B context: %s' % context)
        res['is_write_off']=True
        _logger.info('reconcile - voucher writeoff: %s' % res)
        #  
       
        return res
       
    def action_move_line_create(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        voucher_obj = self.pool.get('account.voucher')
        invoice_obj = self.pool.get('account.invoice')
        
        _logger = logging.getLogger(__name__)
        _logger.info('reconcile - action_move_line_create  voucher ids, context %s,%s' % (ids, context))
        res = super(account_voucher,self).action_move_line_create(cr, uid, ids, context)
        _logger.info('reconcile - action_move_line_create  voucher res, context %s,%s' % (res, context))
         
        for voucher in self.browse(cr, uid, ids):
            lines = move_line_obj.search(cr, uid, [('move_id','=', voucher.move_id.id)])

            _logger.info('reconcile - action_move_line_create  voucher lines %s' % (lines))
            reconcile_ids = []
            write_off_debit = 0.0
            write_off_credit = 0.0
            for line in move_line_obj.browse(cr, uid, lines):
                _logger.info('reconcile voucher reconcile_id, acc_id, partner_id %s,%s %s %s' % (line.reconcile_id.id, line.account_id.id, line.partner_id.id, line.name))
                
                # search move_ids which are reconciled
                
                if line.reconcile_id and line.reconcile_id.id not in reconcile_ids:
                    reconcile_ids.append(line.reconcile_id.id)
                    partner_id = line.partner_id.id
                if line.is_write_off:
                    write_off_debit += line.debit
                    write_off_credit += line.credit
                    write_off_id = line.id        
            if not reconcile_ids:
                return res
            _logger.info('reconcile - partner_id, line_ids, reconcile_ids: %s %s %s' % (partner_id,lines, reconcile_ids))
            _logger.info('reconcile - writeoff deb/cred: %s/%s ' % (write_off_debit,write_off_credit))
            reconciled_move_line_ids = move_line_obj.search(cr, uid, [('move_id','!=',voucher.move_id.id),('partner_id','=', partner_id),('reconcile_id','in', reconcile_ids ) ])
            if not isinstance(reconciled_move_line_ids, list):
                reconciled_move_line_ids = [reconciled_move_line_ids]
            _logger.info('reconcile - reconcile_move_line_ids: %s' % (reconciled_move_line_ids))
            reconciled_move_ids = []
            for move in move_line_obj.browse(cr, uid, reconciled_move_line_ids):
                if move.move_id.id not in reconciled_move_ids:
                    reconciled_move_ids.append(move.move_id.id)
            if not isinstance(reconciled_move_ids, list):
                reconciled_move_ids = [reconciled_move_ids]
            _logger.info('reconcile - reconcile_move_ids: %s' % (reconciled_move_ids))
            # now we find the invoice(s)
            invoice_ids = invoice_obj.search(cr, uid, [('move_id','in', reconciled_move_ids)])
            if not isinstance(invoice_ids, list):
                invoice_ids = [invoice_ids]
            invoice_discount_ids = []    
            invoice_total = 0.0
            for invoice in invoice_obj.browse(cr, uid, invoice_ids):
                if invoice.payment_term.is_discount:
                    invoice_discount_ids.append(invoice.id)
                    invoice_total += invoice.amount_total
            if write_off_debit > 0:
                factor = write_off_debit / invoice_total
            else:
                factor = write_off_credit / invoice_total

            _logger.info('reconcile - invoice_discount_ids: %s invoice_total= %s, factor: %s' % (invoice_discount_ids, invoice_total, factor))
            
            invoice_discount_ids2 = ','.join([str(id) for id in invoice_discount_ids])
            # group 
            cr.execute("""
                      select tax_code_id, payment_term,
                       split_part(pi.value_reference,',',2)::int as discount_income_account_id,
                       split_part(pe.value_reference,',',2)::int as discount_expense_account_id,
                       t.account_id,
                       sum(base_amount) as base_amount, sum(tax_amount) as tax_amount,
                       sum(tax_amount) * %s as tax_discount_amount,
                       sum(base_amount) * %s as base_discount_amount
                      from account_invoice i,
                      account_invoice_tax t,
                      account_payment_term p,
                      account_payment_term_line pl,
                      ir_property pe,
                      ir_property pi
                     where i.id in (%s)
                       and t.invoice_id = i.id
                       and p.id = i.payment_term
                       and pl.payment_id = p.id
                       and pl.discount > 0
                       and pi.res_id = 'account.payment.term.line,'||pl.id and pi.name ='discount_income_account_id'
                       and pe.res_id = 'account.payment.term.line,'||pl.id and pe.name ='discount_expense_account_id'
                     group by 1,2,3,4,5""" % (factor, factor, invoice_discount_ids2))
            tax_moves = cr.dictfetchall()
            if not tax_moves:
                _logger.info('reconcile - no tax_lines: %s' % res)
                return res
            _logger.info('reconcile - tax_moves: %s' % tax_moves)
            tax_cum_amount=0.0
            # get interesting data from write off record, which later will be deleted
            for r_line in move_line_obj.browse(cr, uid, [write_off_id]):
                ml = {
                   'move_id' : r_line.move_id.id,
                   'journal_id' : r_line.journal_id.id,
                   'period_id' : r_line.period_id.id,
                   'date' : r_line.date ,
                   'name' : r_line.name,
                   'debit' : 0.0,
                   'credit' : 0.0,
                   'company_id' : r_line.company_id.id,
                }

            for tax_move in tax_moves:
                #base
                mlt = ml
                if write_off_debit > 0.0:
                    mlt.update({
                       'debit' : tax_move['base_discount_amount'],
                       'account_id' : tax_move['discount_expense_account_id']
                    })
                    write_off_debit -= tax_move['base_discount_amount']
                else:
                    mlt.update({
                       'credit' : tax_move['base_discount_amount'],
                       'account_id' : tax_move['discount_income_account_id']
                    })
                    write_off_credit -= tax_move['base_discount_amount']
                _logger.info('reconcile - base credit: %s' % mlt)
                move_line_obj.create(cr, uid, mlt)
                # tax
                mlt = ml
                if write_off_debit > 0.0:
                    mlt.update({
                       'debit' : tax_move['tax_discount_amount'],
                       'account_id' : tax_move['account_id']
                    })
                    write_off_debit -= tax_move['tax_discount_amount']
                else:
                    mlt.update({
                       'credit' : tax_move['tax_discount_amount'],
                       'account_id' : tax_move['account_id']
                    })
                    write_off_credit -= tax_move['tax_discount_amount']
                move_line_obj.create(cr, uid, mlt)
                # remaining not taxable amount 
            if write_off_debit > 0:
                mlt = ml
                mlt.update({
                       'debit' : 'write_off_debit',
                       'account_id' : tax_move['discount_expense_account_id']
                    })
                move_line_obj.create(cr, uid, mlt)
            if write_off_credit > 0: 
                mlt = ml
                mlt.update({
                       'credit' : write_off_credit,
                       'account_id' : tax_move['discount_income_account_id']
                    })
                move_line_obj.create(cr, uid, mlt)
            
            move_line_obj.unlink(cr, uid,  [write_off_id])
                


                
        return res
        
        
account_voucher()




    
