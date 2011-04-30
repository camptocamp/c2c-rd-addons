# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2010-04-02 15:01:02+02
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
import time
from osv import fields,osv
import pooler
import sys

#class chricar_stock_dispo_production(osv.osv):
#     _name = "stock.move"
class stock_move(osv.osv):     
     _inherit = "stock.move"

     _columns = {
#       'active'             : fields.boolean ('Active', readonly=True),
       'category_prod'           : fields.selection([
                                  ('sell','OK'),
                                  ('big','Big'),
                                  ('small','Small'),
                                  ('faulty','Faulty'),
                                  ('waste','Waste'),     ], 
                                  'Category Prod', size=16, required=True,readonly=True, states={'draft': [('readonly', False)]}),
       #'date_production'    : fields.datetime('Production Date', required=True,readonly=True, states={'draft': [('readonly', False)]}),
       #'location_id'        : fields.many2one('stock.location', 'Location',readonly=True, states={'draft': [('readonly', False)]}),
       #'location_dest_id'   : fields.many2one('stock.location', 'Dest. Location',readonly=True, states={'draft': [('readonly', False)]}),
       #'move_id'            : fields.many2one('stock.move','Picking Line', select=True,readonly=True,),
       #'name'               : fields.char    ('Quality', size=16 ,readonly=True, states={'draft': [('readonly', False)]}),
       'order_line_id'      : fields.many2one('sale.order.line','Sale Order Line', select=True, required=True,readonly=True,),
       #'quantity'           : fields.float   ('Quantity', required=True,readonly=True, states={'draft': [('readonly', False)]}),
       'sequence'           : fields.integer ('Sequence', size=16, ),
       #'state'              : fields.char    ('State', size=16, readonly=True),
       #'prodlot_id'         : fields.many2one('stock.production.lot', 'Production Lot', help="Production lot is used to track production"),
       'product_packaging_id' : fields.many2one('product.product', 'Packaging', help='Product wich is used to store the main product') ,
       'packaging_qty'      : fields.integer ('Packaging Qty'),


}
     _defaults = {

#       'active'            : lambda *a: True,
       #'state'             : lambda *a: 'draft',
#       'sequence'          : lambda *a: 0.0,
#       'date_planned'   : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),

}
     _order = 'date_planned'

     def on_change_dispo_product_qty(self, cr, uid, ids,category,name,quality,location_id=False,location_dest_id=False, location_big_id=False, \
                 location_small_id=False, location_faulty_id=False, location_waste_id=False, prodlot_id=False,  product_packaging_id=False, \
                 product_id=False, product_uom=False, price_unit_id=False):

        result ={}
        print >>sys.stderr, 'category ', category 
        if quality and category == 'sell' and not name:
            name = quality

        if category == 'big':
	    name = 'to big'
            if location_big_id:
                location_dest_id = location_big_id
            else:
                location_dest_id = location_id

        if category == 'small':
	    name = 'to small'
            if location_small_id:
                location_dest_id = location_small_id
            else:
                location_dest_id = location_id

        if category == 'faulty':
	    name = 'faulty'
            if location_faulty_id:
                location_dest_id = location_faulty_id
            else:
                location_dest_id = ''

        if category == 'waste':
	    name = 'waste'
            if location_waste_id:
                location_dest_id = location_waste_id
            else:
                location_dest_id = ''
        # FIXME - must be calculated
        move_value_cost = 0.0
        
        #category = 'small'
        result['name'] = name
        result['category_prod'] = category
        result['location_id'] = location_id
        result['location_dest_id'] = location_dest_id
        result['prodlot_id'] = prodlot_id
        result['product_packaging_id'] = product_packaging_id
        result['product_id'] = product_id
        result['product_uom'] = product_uom
        result['price_unit_id'] = price_unit_id
        result['move_value_cost'] = move_value_cost
        result['sequence'] = 0.0
        result['date_planned'] = time.strftime('%Y-%m-%d %H:%M:%S') 
        print >>sys.stderr, ' result on change ', result
        return {'value':result}
stock_move()

# -----------------------------------------
# Sale Order modified
# -----------------------------------------
class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', \
              readonly=True, states={'draft': [('readonly', False)],'progress': [('readonly', False)] } ),

    }

sale_order()

# -----------------------------------------
# Sale Order Line modified
# -----------------------------------------


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"


    class one2many_sale (fields.one2many):
        def get (self, cr, obj, ids, name, user = None, offset = 0, context = {}, values = {}):
            res = {}
            for id in ids : res[id] = []
            ids2 = obj.pool.get (self._obj).search \
                ( cr
                , user
                , [(self._fields_id, 'in', ids)
                , ('category_prod', '=', 'sell')]
                , limit = self._limit
                )
            for r in obj.pool.get (self._obj)._read_flat \
                (cr
                , user
                , ids2
                , [self._fields_id]
                , context = context
                , load = '_classic_write'
                ):
                res [r[self._fields_id]].append( r['id'] )
            return res
        # end def get
    # end class one2many_sale

    class one2many_small (fields.one2many):
        def get (self, cr, obj, ids, name, user = None, offset = 0, context = {}, values = {}):
            res = {}
            for id in ids : res[id] = []
            ids2 = obj.pool.get (self._obj).search \
                ( cr
                , user
                , [(self._fields_id, 'in', ids)
                , ('category_prod', '=', 'small')]
                , limit = self._limit
                )
            for r in obj.pool.get (self._obj)._read_flat \
                (cr
                , user
                , ids2
                , [self._fields_id]
                , context = context
                , load = '_classic_write'
                ):
                res [r[self._fields_id]].append( r['id'] )
            return res
        # end def get
    # end class one2many_small

    class one2many_big (fields.one2many):
        def get (self, cr, obj, ids, name, user = None, offset = 0, context = {}, values = {}):
            res = {}
            for id in ids : res[id] = []
            ids2 = obj.pool.get (self._obj).search \
                ( cr
                , user
                , [(self._fields_id, 'in', ids)
                , ('category_prod', '=', 'big')]
                , limit = self._limit
                )
            for r in obj.pool.get (self._obj)._read_flat \
                (cr
                , user
                , ids2
                , [self._fields_id]
                , context = context
                , load = '_classic_write'
                ):
                res [r[self._fields_id]].append( r['id'] )
            return res
        # end def get
    # end class one2many_big

    class one2many_faulty (fields.one2many):
        def get (self, cr, obj, ids, name, user = None, offset = 0, context = {}, values = {}):
            res = {}
            for id in ids : res[id] = []
            ids2 = obj.pool.get (self._obj).search \
                ( cr
                , user
                , [(self._fields_id, 'in', ids)
                , ('category_prod', '=', 'faulty')]
                , limit = self._limit
                )
            for r in obj.pool.get (self._obj)._read_flat \
                (cr
                , user
                , ids2
                , [self._fields_id]
                , context = context
                , load = '_classic_write'
                ):
                res [r[self._fields_id]].append( r['id'] )
            return res
        # end def get
    # end class one2many_faulty

    class one2many_waste (fields.one2many):
        def get (self, cr, obj, ids, name, user = None, offset = 0, context = {}, values = {}):
            res = {}
            for id in ids : res[id] = []
            ids2 = obj.pool.get (self._obj).search \
                ( cr
                , user
                , [(self._fields_id, 'in', ids)
                , ('category_prod', '=', 'waste')]
                , limit = self._limit
                )
            for r in obj.pool.get (self._obj)._read_flat \
                (cr
                , user
                , ids2
                , [self._fields_id]
                , context = context
                , load = '_classic_write'
                ):
                res [r[self._fields_id]].append( r['id'] )
            return res
        # end def get
    # end class one2many_waste



    _columns = {
       'quality'           : fields.char    ('Ordered Quality', size=16,help="This will be copied to Quality for each sale line", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }), 
       'location_product_id' : fields.many2one('stock.location', 'Production Location', help="Field where products were grown (AMA)", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'location_id'       : fields.many2one('stock.location', 'Source Location', help="Products will be taken from this location", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'location_dest_id'  : fields.many2one('stock.location', 'Dest. Location', help="Products will be shipped to this location", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'location_big_id'   : fields.many2one('stock.location', 'Dest. Location Big', help="To big products will be moved to this location, defaults to source", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'location_small_id' : fields.many2one('stock.location', 'Dest. Location Small', help="To small products will be moved to this location, defaults to source", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'location_faulty_id': fields.many2one('stock.location', 'Dest. Location Faulty', help="Faulty products will be moved to this location, set default manually", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'location_waste_id' : fields.many2one('stock.location', 'Dest. Location Waste', help="Waste will be moved to this location, set default manually", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'trading_unit_owner_id': fields.many2one('res.partner','Owner of Trading Unit', help="This will create appropriate text on picking, packing and labels", \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }, \
                       help="Production lot is used to track the production"),  
       'stock_dispo_production_sale_ids'  : one2many_sale('stock.move','order_line_id','To Sell', \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'stock_dispo_production_small_ids' : one2many_small('stock.move','order_line_id','To Small', \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'stock_dispo_production_big_ids'   : one2many_big('stock.move','order_line_id','To Big', \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'stock_dispo_production_faulty_ids': one2many_faulty('stock.move','order_line_id','Faulty', \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'stock_dispo_production_waste_ids' : one2many_waste('stock.move','order_line_id','Waste', \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'stock_dispo_production_ids': fields.one2many('stock.move','order_line_id','Dispo Production', \
                       readonly=True, states={'draft': [('readonly', False)],'confirmed': [('readonly', False)] }),
       'product_packaging_id' : fields.many2one('product.product', 'Packaging', help='Product wich is used to store the main product') ,
       
    }
sale_order_line()



#class stock_move(osv.osv):
#      _inherit = "stock.move"
#      _columns = {
#          'stock_dispo_production_ids': fields.one2many('stock.move','move_id','Dispo Production'),
#          'product_packaging_id' : fields.many2one('product.product', 'Default Packaging', help='Product wich is used to store the main product') ,
#          'packaging_qty'  : fields.integer ('Packaging Qty'),#
#
#      }
#stock_move()


