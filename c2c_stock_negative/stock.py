# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

from openerp.osv import osv, fields
#import openerp.addons.decimal_precision as dp

import re
from openerp.tools.translate import _
import logging

#----------------------------------------------------------
#  Product Category
#----------------------------------------------------------

class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'allow_negative_stock' : fields.boolean('Allow Negative Stock', help="Allows negative stock quantities per location / lot for this category - use with care !"),
    }

product_category()


#----------------------------------------------------------
#  Product
#----------------------------------------------------------

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'allow_negative_stock' : fields.boolean('Allow Negative Stock', help="Allows negative stock quantities per location / lot for this category - use with care !"),
    }

product_template()


class stock_move(osv.osv):
    _inherit = 'stock.move'

    # FIXME - check does not raise error
    # allow_negative_stock is defined for product_template
    def _check_allow_negative_stock(self, cr, uid, ids, context=None):

        for move in self.browse(cr, uid, ids):
            do_check = True
            if move.product_id.allow_negative_stock or move.product_id.categ_id.allow_negative_stock:
                do_check = False
            if do_check:
                # name field = product qty
                cr.execute(
               "select product_id,location_id,prodlot_id,sum(name) as qty \
                   from chricar_stock_product_by_location_prodlot \
                  where product_id = %d \
                    and company_id = %d \
                  group by product_id, location_id,prodlot_id \
                 having sum(name) < 0" % ( move.product_id.id, move.company_id.id ))
                for check in  cr.fetchall():
                    product= self.pool.get('product.product').browse(cr,uid,[check[0]], context)[0].name
                    location = self.pool.get('stock.location').browse(cr,uid,[check[1]], context)[0].name
                    if check[2]:
                        lot = self.pool.get('stock.production.lot').browse(cr,uid,[check[2]], context)[0].name
                    else:
                        lot = ''
                    raise osv.except_osv(_('Error !'), _('negative quantity %s not llowed for product: %s, location: %s, lot: %s  !') % (check[3],product,location, lot ) )

        return True

    _constraints = [ (_check_allow_negative_stock, 'Error: Negative quantities for location and/or lots are not allowed for this product or product category', ['name']), ]


stock_move()


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    def name_get(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        res= super(stock_production_lot, self).name_get(cr, uid, ids, context)
        _logger.debug('FGF lot res negative %s' % (res))
        res1 = []
        if context.get('location_id'):
            lots_to_show = []
            for lot in self.browse(cr, uid, ids, context):
                if lot.product_id.allow_negative_stock or lot.stock_available != 0:
                    lots_to_show.append(lot.id)
            _logger.debug('FGF lot res negative to show %s' % (lots_to_show))
            if lots_to_show:
                for r in res:
                    _logger.debug('FGF lot res negative r %s,%s' % (r, res))
                    if r[0] in lots_to_show:
                        res1.append(r)
                        #_logger.debug('FGF lot res negative res 1%s' % (res1))
        else:
            res1 = res

        return res1

stock_production_lot()

class stock_location(osv.osv):
    _inherit = 'stock.location'

    def name_get(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        _logger = logging.getLogger(__name__)
        res= super(stock_location, self).name_get(cr, uid, ids, context)
        res1 = []
        if context.get('product_id'):
            loc_to_show = []
            for product in product_obj.browse(cr, uid, [context.get('product_id')]):
                if not product.allow_negative_stock:
                    for loc in self.browse(cr, uid, ids, context):
                        qty = loc.stock_real
                        qty_v = loc.stock_virtual
                        if qty != 0 or qty_v != 0:
                            loc_to_show.append(loc.id)
            if loc_to_show:
                for r in res:
                    _logger.debug('FGF loc res negative r %s,%s' % (r, res))
                    if r[0] in loc_to_show:
                        res1.append(r)
            else: # FIXME workaround
                res1 = res


        else:
            res1 = res
        return res1

stock_location()
