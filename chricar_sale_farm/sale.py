# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or

# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
# FGF 20160926 - store function was not defined correctl - hence values are calculated now on the fly - apparently no performance issue

import time
from osv import fields,osv
import netsvc
import logging


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _logger = logging.getLogger(__name__)

    def _invoiced_qty(self, cursor, user, ids, name, arg, context=None):
    #def _invoiced_qty(self, cursor, user, ids, context=None):
        res = {}
        _logger = logging.getLogger(__name__)
        _logger.info('FGF self.columnes %s' % (self._columns))
        _logger.info('FGF ids %s,name %s,arg %s' % (ids,name,arg))
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = 0
            if line.order_id.invoice_ids:
                for inv in line.order_id.invoice_ids:
                    for inv_line in inv.invoice_line:
                        if inv_line.product_id == line.product_id and inv_line.invoice_id.state != 'cancel':
                            res[line.id] += inv_line.quantity
        return res

    def _invoiced_amount(self, cursor, user, ids, name, arg, context=None):
    #def _invoiced_amount(self, cursor, user, ids, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = 0
            if line.order_id.invoice_ids:
                for inv in line.order_id.invoice_ids:
                    for inv_line in inv.invoice_line:
                        if inv_line.product_id == line.product_id and inv_line.invoice_id.state in ['open','paid']:
                            if inv_line.invoice_id.type == 'out_invoice' and inv_line.invoice_id.state != 'cancel': 
                                res[line.id] += inv_line.price_subtotal
                            else: 
                                res[line.id] -= inv_line.price_subtotal
        return res

    def _invoiced_price(self, cursor, user, ids, name, arg, context=None):
    #def _invoiced_price(self, cursor, user, ids, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            if line.invoiced_qty != 0:
                res[line.id] = line.invoiced_amount / line.invoiced_qty
            else:
                res[line.id] = 0
        return res

    def _delivered_qty(self, cursor, user, ids, name, arg, context=None):
    #def _delivered_qty(self, cursor, user, ids, context=None):
        res = {}
        _logger = logging.getLogger(__name__)
        _logger.info('FGF self.columnes %s' % (self._columns))
        _logger.info('FGF ids %s,name %s,arg %s' % (ids,name,arg))
        for line in self.browse(cursor, user, ids, context=context):
            _logger.info('FGF line %s' % (line))
            res[line.id] = 0
            if line.order_id and line.order_id.picking_ids:
                 for pick in line.order_id.picking_ids:
                    for pick_line in pick.move_lines:
                        if pick_line.product_id.id == line.product_id.id and pick_line.state == 'done':
                            if pick_line.location_dest_id.usage in['inventory', 'customer']:
                                res[line.id] += pick_line.product_qty
                            if pick_line.location_id.usage in['inventory', 'customer']:
                                res[line.id] -= pick_line.product_qty
        return res

    def _diff_qty(self, cursor, user, ids, name, arg, context=None):
    #def _diff_qty(self, cursor, user, ids, context=None):
        res = {}
        _logger = logging.getLogger(__name__)
        _logger.info('FGF diff_qty self.columnes %s' % (self._columns))
        _logger.info('FGF ids %s,name %s,arg %s' % (ids,name,arg))
        for line in self.browse(cursor, user, ids, context=context):
            if line.invoiced_qty - line.delivered_qty < 0:
                res[line.id] = line.invoiced_qty - line.delivered_qty
            else:
                res[line.id] = 0
        return res

    def _diff_percent(self, cursor, user, ids, name, arg, context=None):
    #def _diff_percent(self, cursor, user, ids, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            if  line.delivered_qty > 0 and line.diff_qty < 0:
                res[line.id] = line.diff_qty/line.delivered_qty*100
            else:
                res[line.id] = 0
        return res

    def _uninvoiced_amount(self, cursor, user, ids, name, arg, context=None):
    #def _uninvoiced_amount(self, cursor, user, ids, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = line.invoiced_price  * line.diff_qty
        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for il in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
          if il.invoice_id and il.invoice_id.id: 
            for inv in  self.pool.get('account.invoice').browse(cr, uid, [il.invoice_id.id], context=context):
                for so in self.pool.get('sale.order').browse(cr, uid, inv.sale_order_ids, context=context):
                    for sol in self.pool.get('sale.order.line').browse(cr, uid, so.order_line, context=context):
                        if il.product_id.id == sol.product_id.id:
                            result[il.id] = True
        return result.keys()

    def _get_order_line(self, cr, uid, ids, context=None):
        result = {}
        sale_line_id = []
        for il in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            for inv in  self.pool.get('account.line').browse(cr, uid, [il.invoice_id.id], context=context):
                for so in self.pool.get('sale.order').browse(cr, uid, [inv.sale_order_ids], context=context):
                    for sol in self.pool.get('sale.order.line').browse(cr, uid, [so.order_line], context=context):
                        if il.product_id.id == sol.product_id.id:
                            result[il.id] = True
          
        #for line in self.pool.get('sale.order.line').browse(cr, uid, sale_line_id , context=context):
        #    result[line.invoice_id.id] = True
        return result.keys()

    def _get_stock_move(self, cr, uid, ids, context=None):
        result = {}
        for move in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            result[move.order_line_id.id] = True
        return result.keys()



    _columns = {
#         'delivered_qty' : fields.function(_delivered_qty, string='Delivered QTY', type='float',
#                           store={
#                               'stock.move': (_get_stock_move, ['product_qty'], 10),
#                               'sale.order.line'    : (lambda self, cr, uid, ids, c={}: ids, ['delivered_qty'], 10),
#                                 }),
#         'invoiced_qty'  : fields.function(_invoiced_qty, string='Invoiced QTY', type='float',
#                           store={'account.invoice.line': (_get_invoice_line, ['quantity'], 10),
#                                  'sale.order.line'    : (lambda self, cr, uid, ids, c={}: ids, ['invoiced_qty'], 10),
#                                 }),
#         'diff_qty'      : fields.function(_diff_qty, string='Waste QTY', type='float', 
#                           store={ 'stock.move': (_get_stock_move, ['product_qty'], 10),
#                                   'account.invoice.line': (_get_invoice_line, ['quantity'], 10),
#                                   'sale.order.line'    : (lambda self, cr, uid, ids, c={}: ids, ['diff_qty'], 10), 
#                                 }),
#         'diff_percent'  : fields.function(_diff_percent, string='Diff %', type='float'),
#         'invoiced_amount':fields.function(_invoiced_amount, string='Invoiced Amount', type='float',
#                           store={'account.invoice.line': (_get_invoice_line, ['price_subtotal'], 10) , 
#                                  'sale.order.line'    : (lambda self, cr, uid, ids, c={}: ids, ['invoiced_amount'], 10),
#                                 }),
#         'uninvoiced_amount':fields.function(_uninvoiced_amount, string='Waste Value', type='float',
#                           store= {'sale.order.line'    : (lambda self, cr, uid, ids, c={}: ids, ['uninvoiced_amount'], 10),
#                                   'account.invoice.line': (_get_invoice_line, ['price_subtotal'], 10)
#                                  }),
         'delivered_qty' : fields.function(_delivered_qty, string='Delivered QTY', type='float',),
         'invoiced_qty'  : fields.function(_invoiced_qty, string='Invoiced QTY', type='float',),
         'diff_qty'      : fields.function(_diff_qty, string='Waste QTY', type='float',),
         'diff_percent'  : fields.function(_diff_percent, string='Diff %', type='float'),
         'invoiced_amount':fields.function(_invoiced_amount, string='Invoiced Amount', type='float',),
         'uninvoiced_amount':fields.function(_uninvoiced_amount, string='Waste Value', type='float',),

         'invoiced_price': fields.function(_invoiced_price, string='Invoiced Price', type='float'),
         'date_order'    : fields.related('order_id', 'date_order', type='date', string='Date Order', store=True),
         'state_order'   : fields.related('order_id', 'state', type='varchar', string='State Order'),
         'partner_shipping_id'    : fields.related('order_id', 'partner_shipping_p_id', type='many2one',relation='res.partner', string='Shipping Partner', store=True),
        }


sale_order_line()

