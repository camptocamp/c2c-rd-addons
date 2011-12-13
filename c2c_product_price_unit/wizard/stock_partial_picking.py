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

import time
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp


class stock_partial_picking_line(osv.TransientModel):
    _inherit = "stock.partial.picking.line"
   
    _columns = {
      'cost_pu' : fields.float("Cost PU", help="PU Unit Cost for this product line"),
      'cost_unit_pu' : fields.many2one('c2c_product.price_unit','Price Unit'),
    }

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"

    def _product_cost_for_average_update(self, cr, uid, move):
        res = super(stock_partial_picking,self)._product_cost_for_average_update(cr, uid, move )
        import sys
        print >> sys.stderr,'_product_cost_for_average_update',res 
        res.update({'cost_pu' : move.price_unit_pu or move.product_id.standard_price, 'cost_unit_pu': move.price_unit_id.id or  move.product_id.price_unit_id.id})
        print >> sys.stderr,'_product_cost_for_average_update',res 
        return res
