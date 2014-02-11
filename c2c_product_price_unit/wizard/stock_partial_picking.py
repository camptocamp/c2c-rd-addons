# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP SA (<http://openerp.com>).
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
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import logging

class stock_partial_picking_line(osv.TransientModel):
    _inherit = "stock.partial.picking.line"

    _columns = {
      'cost_pu' : fields.float("Cost PU", help="PU Unit Cost for this product line"),
      'sale' : fields.float("Sale", help="Sale for this product line"),
      'cost_sale_pu' : fields.float("Sale PU", help="PU Unit Cost for this product line"),
      'cost_unit_pu' : fields.many2one('c2c_product.price_unit','Price Unit'),
      'cost_unit_sale_pu' : fields.many2one('c2c_product.price_unit','Price Unit Sale'),
      'move_type' : fields.char('Move Type',size=16),
    }

    def onchange_cost_pu(self, cr, uid, ids,field,cost_pu,cost_unit_pu):
        if cost_pu and cost_unit_pu:
            coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, cost_unit_pu)
            cost = cost_pu / coeff
            return {'value' : {field: cost }}
        return


class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    _logger = logging.getLogger(__name__)

    def _product_cost_for_average_update(self, cr, uid, move):
        res = super(stock_partial_picking,self)._product_cost_for_average_update(cr, uid, move )
        self._logger.debug('_product_cost_for_average_update `%s`', res)
        res.update({'cost_pu' : move.price_unit_pu or move.purchase_line_id.price_unit_pu or  move.product_id.standard_price, \
                'cost_unit_pu': move.price_unit_id.id or move.purchase_line_id.price_unit_id.id or move.product_id.price_unit_id.id})
        # FIXME - remove if
        #res.update({'cost' : move.purchase_line_id.price_unit or  move.product_id.standard_price })
        self._logger.debug('_product_cost_for_average_update `%s`', res)
        return res

    def _partial_move_for(self, cr, uid, move):
        res = super(stock_partial_picking,self)._partial_move_for(cr, uid, move)
        self._logger.debug('_partial_move_for (b) `%s`', res)
        self._logger.debug('move `%s`', move)
        res.update({'move_type': move.picking_id.type})
        if move.picking_id.type == 'out' : #and move.product_id.cost_method == 'average':
            res.update({'cost_sale_pu' : move.sale_line_id.price_unit_pu or  move.product_id.list_price, \
                'cost_unit_sale_pu': move.sale_line_id and move.sale_line_id.price_unit_id.id or move.product_id.price_unit_id.id,
                'sale' : move.sale_line_id.price_unit or  move.product_id.list_price})
        self._logger.debug('_partial_move_for (c `%s`', res)
        return res
