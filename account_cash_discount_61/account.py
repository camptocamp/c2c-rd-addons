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
from tools import float_round, float_is_zero, float_compare


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
       
        return res



    # this handles "pay invoice"    
    def action_move_line_create(self, cr, uid, ids, context=None):
        res = super(account_voucher,self).action_move_line_create(cr, uid, ids, context)
        self.reconcile_cash_discount(cr, uid, ids, context)
        return res        
    
    
    def reconcile_cash_discount(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        _logger.info('reconcile - action_move_line_create  voucher ids, context %s,%s' % (ids, context))
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        voucher_obj = self.pool.get('account.voucher')
        invoice_obj = self.pool.get('account.invoice')
        invoice_tax_obj = self.pool.get('account.invoice.tax')
        move_reconcile_obj = self.pool.get('account.move.reconcile')
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')

     
        for voucher in self.browse(cr, uid, ids):
            lines = move_line_obj.search(cr, uid, [('move_id','=', voucher.move_id.id)])

            _logger.info('reconcile - action_move_line_create  voucher lines %s' % (lines))
            reconcile_ids = []
            reconcile_base_id = ''
            write_off_debit = 0.0
            write_off_credit = 0.0
            partner_id = ''
            for line in move_line_obj.browse(cr, uid, lines):
                _logger.info('reconcile voucher reconcile_id, acc_id, partner_id %s,%s %s %s' % (line.reconcile_id.id, line.account_id.id, line.partner_id.id, line.name))
                
                # search move_ids which are reconciled
                
                if line.reconcile_id and line.reconcile_id.id not in reconcile_ids:
                    reconcile_ids.append(line.reconcile_id.id)
                    if not partner_id and line.partner_id:
                        partner_id = line.partner_id.id
                    if not reconcile_base_id: 
                        reconcile_base_id = line.reconcile_id.id
                    
                if line.is_write_off:
                    write_off_debit += line.debit
                    write_off_credit += line.credit
                    write_off_id = line.id        
            if not reconcile_ids:
                return True
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
            invoice_net = 0.0
            for invoice in invoice_obj.browse(cr, uid, invoice_ids):
                if invoice.payment_term.is_discount:
                    invoice_discount_ids.append(invoice.id)
                    invoice_total += invoice.amount_total
                    invoice_net += invoice.amount_untaxed
            tax_base_total = 0.0
            tax_total = 0.0
            invoice_tax_ids = invoice_tax_obj.search(cr, uid, [('invoice_id','in',invoice_ids)])
            for tax in invoice_tax_obj.browse(cr, uid, invoice_tax_ids):
                tax_base_total += tax.base_amount
                tax_total += tax.tax_amount
             
            if write_off_debit > 0:
                factor = write_off_debit / invoice_total
            else:
                factor = write_off_credit / invoice_total
            _logger.info('reconcile - compare: %s invoice_net= %s, factor : %s' % (invoice_net, tax_base_total, factor))
            #if not float_is_zero(invoice_net - tax_base_total, prec):
            #if round(invoice_net - tax_base_total, prec) != 0.00:
            #    _logger.info('reconcile - recalculate factor ')
            factor = factor * (tax_base_total / invoice_net)
            _logger.info('reconcile - recalculate factor %s' % factor)
                
            _logger.info('reconcile - invoice_discount_ids: %s invoice_total= %s, factor: %s' % (invoice_discount_ids, invoice_total, factor))
            
            invoice_discount_ids2 = ','.join([str(id) for id in invoice_discount_ids])
            # group 
            cr.execute("""
                      select tax_code_id, payment_term,
                       split_part(pi.value_reference,',',2)::int as discount_income_account_id,
                       split_part(pe.value_reference,',',2)::int as discount_expense_account_id,
                       t.account_id,
                       t.tax_code_id, t.base_code_id, 
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
                     group by 1,2,3,4,5,6,7""" % (factor, factor, invoice_discount_ids2))
            tax_moves = cr.dictfetchall()
            if not tax_moves:
                _logger.info('reconcile - no tax_lines: %s' % res)
                return True
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
                   'name' : _('Discount'),
                }

            for tax_move in tax_moves:
                #base
                mlt = ml
                if write_off_debit > 0.0:
                    mlt.update({
                       'debit' : tax_move['base_discount_amount'],
                       'account_id' : tax_move['discount_expense_account_id'],
                       'tax_code_id' : tax_move['base_code_id'],
                       'tax_amount' : tax_move['base_discount_amount'],
                    })
                    write_off_debit -= tax_move['base_discount_amount']
                else:
                    mlt.update({
                       'credit' : tax_move['base_discount_amount'],
                       'account_id' : tax_move['discount_income_account_id'],
                       'tax_code_id' : tax_move['base_code_id'],
                       'tax_amount' : tax_move['base_discount_amount'],
                    })
                    write_off_credit -= tax_move['base_discount_amount']
                _logger.info('reconcile - base credit: %s' % mlt)
                move_line_obj.create(cr, uid, mlt)
                # tax
                mlt = ml
                if write_off_debit > 0.0:
                    mlt.update({
                       'debit' : tax_move['tax_discount_amount'],
                       'account_id' : tax_move['account_id'],
                       'tax_code_id' : tax_move['tax_code_id'],
                       'tax_amount' : tax_move['tax_discount_amount'],
                    })
                    write_off_debit -= tax_move['tax_discount_amount']
                else:
                    mlt.update({
                       'credit' : tax_move['tax_discount_amount'],
                       'account_id' : tax_move['account_id'],
                       'tax_code_id' : tax_move['tax_code_id'],
                       'tax_amount' : tax_move['tax_discount_amount'],
                    })
                    write_off_credit -= tax_move['tax_discount_amount']
                move_line_obj.create(cr, uid, mlt)
                # remaining not taxable amount 
            if not float_is_zero(write_off_debit, prec):
                mlt = ml
                mlt.update({
                       'debit' : 'write_off_debit',
                       'account_id' : tax_move['discount_expense_account_id'],
                       'tax_code_id' : False,
                       'tax_amount' : False,
                    })
                move_line_obj.create(cr, uid, mlt)
            if not float_is_zero(write_off_credit, prec): 
                mlt = ml
                mlt.update({
                       'credit' : write_off_credit,
                       'account_id' : tax_move['discount_income_account_id'],
                       'tax_code_id' : False,
                       'tax_amount' : False,
                    })
                move_line_obj.create(cr, uid, mlt)
            
            move_line_obj.unlink(cr, uid,  [write_off_id])
            # set only ONE reconcile_id (instead of 2 or more)
            reconcile_lines_to_update = move_line_obj.search(cr, uid, [('reconcile_id','in',reconcile_ids),('reconcile_id','!=',reconcile_base_id)])
            move_line_obj.write(cr, uid, reconcile_lines_to_update,{'reconcile_id':reconcile_base_id})    
            # delete unused recocile lines
            reconcile_ids_to_delete = [] 
            for r_id in reconcile_ids:
                if r_id != reconcile_base_id:
                    reconcile_ids_to_delete.append(r_id)
            move_reconcile_obj.unlink(cr, uid, reconcile_ids_to_delete)
                
        return True 
        
        
account_voucher()

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    def reconcile(self, cr, uid, ids, type='auto', writeoff_acc_id=False, writeoff_period_id=False, writeoff_journal_id=False, context=None):
        _logger = logging.getLogger(__name__)
        lines_selected = []
        for l in  context.get('active_ids'):
            _logger.info('reconcile move_line lines_selected %s l %s' % (lines_selected, l))
            lines_selected.append(str(l))
        _logger.info('reconcile move_line lines_selected %s, context %s' % (lines_selected, context))
        res = super(account_move_line, self).reconcile(cr, uid, ids, type, writeoff_acc_id, writeoff_period_id, writeoff_journal_id, context)
        lines_ids_returned = context.get('active_ids')
        _logger.info('FGF reconcile  lines_selected %s, lines_ids_returned %s' % (lines_selected, lines_ids_returned))
        write_off_line_ids = []
        for line_id in lines_ids_returned:
            if str(line_id) not in lines_selected:
                write_off_line_ids.append(line_id)
        _logger.info('FGF reconcile move_line reconclie_id %s, write_off_line_ids %s, context %s' % (res, write_off_line_ids, context))

        return res


account_move_line()
    
