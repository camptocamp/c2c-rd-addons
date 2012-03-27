# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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
import logging

class stock_location(osv.osv):
    _inherit = 'stock.location'

    def name_get(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        _logger = logging.getLogger(__name__)
        res= super(stock_location, self).name_get(cr, uid, ids, context)
        _logger.info('FGF loc res %s' % (res))
        _logger.info('FGF loc context %s ' % (context))
        resd = dict(res)
        _logger.info('FGF loc d %s ' % (resd))
        res1 =[]
        if context.get('product_id'):
          for product in product_obj.browse(cr, uid, [context.get('product_id')]):
              uom_name = ' '+product.uom_id.name
              hide_null_location = False
              if product._columns.get('allow_negative_stock') and not product.allow_negative_stock:
                  hide_null_location = True
          for loc in self.browse(cr, uid, ids, context):
            qty = loc.stock_real
            qty_v = loc.stock_virtual
            _logger.info('FGF loc res %s %s %s' % (loc.id, qty, qty_v))
            #name_new = resd[loc.id] + '  [' + str(qty) +' '+ loc.product_id.uom_id.name+']'
            qty_str = str(qty)
            if qty_v != qty:
                qty_str += ' / ' + str(qty_v)
            name_new = resd[loc.id] + ' [ ' + qty_str + uom_name + ' ]'
            _logger.info('FGF loc name %s' % (name_new))
            l = (loc.id,name_new)
            if not(hide_null_location and qty == 0 and qty_v == 0): 
                 res1.append(l)
            _logger.info('FGF loc res1 %s' % (res1))
        else:
           res1 = res
        return res1
        
stock_location()
