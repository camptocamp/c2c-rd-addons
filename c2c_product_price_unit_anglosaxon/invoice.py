# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
import logging 

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def move_line_get(self, cr, uid, invoice_id, context=None):
        _logger  = logging.getLogger(__name__)
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context) 
        stock_moves = {}
        #20140825 - added counter
        for pick in inv.picking_ids:
            for ml in pick.move_lines:
                if stock_moves.get(ml.product_id.id):
                    qty = stock_moves[ml.product_id.id][0]
                    cost = stock_moves[ml.product_id.id][1]
                    stock_moves[ml.product_id.id] = (ml.product_qty+qty, ml.move_value_cost+cost, stock_moves[ml.product_id.id][2]+1 )
                else:
                    stock_moves[ml.product_id.id] = (ml.product_qty, ml.move_value_cost,1)
        self._logger.debug('FGF anglo stock moves %s', stock_moves)
        
        res_orig = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context=context)
        self._logger.debug('FGF anglosaxon res_orig %s', res_orig)
        tax = {}
        for res_line in res_orig:
            self._logger.debug('FGF anglo stock res line orig %s', res_line)
            if res_line.get('product_id'):
                tax_amount = ''
                tax_code_id = ''
                if res_line.get('tax_amount'):
                    tax_amount = res_line['tax_amount']
                if res_line.get('tax_code_id'):
                    tax_code_id = res_line['tax_code_id']
                if tax_amount:
                    if tax.get(res_line['product_id']):
                        tax[res_line['product_id']] = (tax_amount + tax[res_line['product_id']][0], tax_code_id)
                    else:
                        tax[res_line['product_id']] = (tax_amount, tax_code_id)
                
        self._logger.debug('FGF anglo stock tax orig %s', tax)
          
        res= []
             
        for i_line in inv.invoice_line:
            self._logger.debug('FGF anglosaxon line data qty %s subtotal %s', i_line.quantity, i_line.price_subtotal)
            if not i_line.product_id or not stock_moves.get(i_line.product_id.id) :
                self._logger.debug('FGF anglosaxon pass 1')
                res = res_orig
               
            elif i_line.product_id.type != 'product':
                self._logger.debug('FGF anglosaxon pass 2')
                res = res_orig
                
            else:
                self._logger.debug('FGF stock_moves %s %s' % ( stock_moves, i_line.product_id.id ))
                smp = i_line.product_id.id
                self._logger.debug('FGF stock_moves %s' % (smp))
                if stock_moves[smp][2] > 1:
                    stock_line_amount = i_line.price_subtotal
                    stock_line_qty = i_line.quantity
                    amount_diff = 0
                    qty_diff = 0
                    c = stock_moves[smp][2] - 1 
                    p = stock_moves[smp][1] - i_line.price_subtotal
                    q = stock_moves[smp][0] - i_line.quantity
                    stock_moves[smp] = (c, p, q)
                    
                    t = tax[smp][0]
                    tc= tax[smp][1]
                    tax_amount = -i_line.price_subtotal
                    tax[smp] = ( t - i_line.price_subtotal, tc)
                else:
                    stock_line_amount = stock_moves[smp][1]
                    stock_line_qty = stock_moves[smp][0]
                    tax_amount = tax[smp][0]
                    amount_diff = i_line.price_subtotal - stock_line_amount
                    qty_diff = i_line.quantity - stock_moves[smp][0]
                
                self._logger.debug('FGF anglosaxon tax  %s', tax)
                
                self._logger.debug('FGF anglosaxon diff %s %s', qty_diff, amount_diff)
                
                if inv.type in ('out_invoice','in_refund') :
                    res = res_orig
                    # FIXME
                    # in_refund not working correctly - if no picking / stock_moves !?

                    
                    self._logger.debug('FGF anglosaxon must compute diff out %s %s', i_line.quantity, i_line.price_subtotal)

                    if inv.type == 'out_invoice' :
                        # debit account dacc will be the output account
                        # first check the product, if empty check the category
                        dacc = i_line.product_id.property_stock_account_output and i_line.product_id.property_stock_account_output.id
                        if not dacc:
                            dacc = i_line.product_id.categ_id.property_stock_account_output_categ and i_line.product_id.categ_id.property_stock_account_output_categ.id
                    else:
                        # = out_refund
                        # debit account dacc will be the input account
                        # first check the product, if empty check the category
                        dacc = i_line.product_id.property_stock_account_input and i_line.product_id.property_stock_account_input.id
                        if not dacc:
                            dacc = i_line.product_id.categ_id.property_stock_account_input_categ and i_line.product_id.categ_id.property_stock_account_input_categ.id
                    # in both cases the credit account cacc will be the expense account
                    # first check the product, if empty check the category
                    cacc = i_line.product_id.property_account_expense and i_line.product_id.property_account_expense.id
                    if not cacc:
                        cacc = i_line.product_id.categ_id.property_account_expense_categ and i_line.product_id.categ_id.property_account_expense_categ.id
                    
                    # this will only happen if the cost_price is changed between delivery and invoice
                    #res = []
                    for res_line in res_orig:
                        if res_line['product_id'] == smp :
                           if res_line['account_id'] == dacc and res_line['price_unit'] != stock_line_amount:
                               res_line['price_unit'] = stock_line_amount / stock_line_qty
                               res_line['price'] = res_line['price_unit'] * i_line.quantity
                           elif  res_line['account_id'] == cacc  and res_line['price_unit'] != -stock_line_amount:
                               res_line['price_unit'] = -stock_line_amount / stock_line_qty
                               res_line['price'] = res_line['price_unit'] * i_line.quantity
                        self._logger.debug('FGF res_line out  %s', res_line)
                    #    res.append(res_line)

                if inv.type in ('in_invoice','out_refund'):
                    
                    self._logger.debug('FGF anglosaxon must compute diff in %s %s', i_line.quantity, i_line.price_subtotal )
                    # get the price difference account at the product
                    acc = i_line.product_id.property_account_creditor_price_difference and i_line.product_id.property_account_creditor_price_difference.id
                    if not acc:
                        # if not found on the product get the price difference account at the category
                        acc = i_line.product_id.categ_id.property_account_creditor_price_difference_categ and i_line.product_id.categ_id.property_account_creditor_price_difference_categ.id
                    a = None
                    if inv.type == 'in_invoice':
                        # oa will be the stock input account
                        # first check the product, if empty check the category
                        oa = i_line.product_id.property_stock_account_input and i_line.product_id.property_stock_account_input.id
                        if not oa:
                            oa = i_line.product_id.categ_id.property_stock_account_input_categ and i_line.product_id.categ_id.property_stock_account_input_categ.id
                    else:
                        # = in_refund
                        # oa will be the stock output account
                        # first check the product, if empty check the category
                        oa = i_line.product_id.property_stock_account_output and i_line.product_id.property_stock_account_output.id
                        if not oa:
                            oa = i_line.product_id.categ_id.property_stock_account_output_categ and i_line.product_id.categ_id.property_stock_account_output_categ.id
                    if oa:
                        # get the fiscal position
                        fpos = i_line.invoice_id.fiscal_position or False
                        a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, oa)

                    if acc and a :
                        # stock input account
                        if stock_line_amount != 0:
                            res.append({
                                'type':'src',
                                'name': i_line.name[:64],
                                'price_unit': stock_line_amount / stock_line_qty, # i_line.product_id.standard_price,
                                'quantity':i_line.quantity,
                                'price': stock_line_amount,
                                'account_id': a,
                                'product_id':smp,
                                'uos_id':i_line.uos_id.id,
                                'account_analytic_id': False,
                                'taxes':i_line.invoice_line_tax_id,
                                'tax_amount': tax_amount,
                                'tax_code_id': tax[smp][1],
                                })
                        # price diff
                        if amount_diff != 0.0:
                            
                            self._logger.info('FGF qty_diff  %s', qty_diff)
                            if qty_diff and qty_diff != 0.0:
                                pu_diff = amount_diff / qty_diff
                            else:
                                pu_diff = amount_diff
                            
                            res.append({
                                'type':'src',
                                'name': i_line.name[:64],
                                'price_unit': pu_diff, #i_line.product_id.standard_price,
                                'quantity': i_line.quantity,
                                'price': amount_diff, #-1 * get_price(cr, uid, inv, company_currency, i_line),
                                'account_id': acc,
                                'product_id':smp,
                                'uos_id':i_line.uos_id.id,
                                'account_analytic_id': False,
                                'taxes':i_line.invoice_line_tax_id,
                                })




        self._logger.debug('FGF anglosaxon res %s', res)
        #raise osv.except_osv(_('Error'), _('TEST FGF Angosaxon'))
        return res
    
account_invoice_line()
