# -*- coding: utf-8 -*-
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
from openerp.osv import fields,osv
import openerp.addons.one2many_sorted as one2many_sorted
import logging

#class chricar_stock_dispo_production(osv.osv):
#     _name = "stock.move"
class stock_move(osv.osv):
    _inherit = "stock.move"
    _selection_type = \
        [ ('sell','OK')
        , ('big','Big')
        , ('small','Small')
        , ('faulty','Faulty')
        , ('waste','Waste')
        ]
    _columns = \
        { 'category'             : fields.selection(_selection_type,'Category', size=16, readonly=True, states={'draft': [('readonly', False)]})
        , 'category_prod'        : fields.char('Category', size=16, readonly=True, states={'draft': [('readonly', False)]})
        , 'order_line_id'        : fields.many2one('sale.order.line','Sale Order Line', select=True, readonly=True, ondelete='restrict',)
        , 'sequence'             : fields.integer ('Sequence', size=16, )
        , 'product_packaging_id' : fields.many2one('product.product', 'Packaging', help='Product wich is used to store the main product', ondelete='restrict')
        , 'packaging_qty'        : fields.integer ('Packaging Qty')
        }
    _defaults = {'sequence' : lambda *a: 0}

    def on_change_dispo_product_qty \
        ( self, cr, uid, ids
        , category, name, quality, location_id=False, location_dest_id=False, location_big_id=False
        , location_small_id=False, location_faulty_id=False, location_waste_id=False, prodlot_id=False
        , product_packaging_id=False, product_id=False, product_uom=False, price_unit_id=False,product_qty=False):

        result ={}

        if quality and category == 'sell' and not name:
            name = quality

        if category == 'big':
            if not name:
                name = 'Übergröße'
            if location_big_id:
                location_dest_id = location_big_id
            else:
                location_dest_id = location_id

        if category == 'small':
            if not name:
                name = 'Untergröße'
            if location_small_id:
                location_dest_id = location_small_id
            else:
                location_dest_id = location_id

        if category == 'faulty':
            if not name:
                name = 'Mangelware'
            if location_faulty_id:
                location_dest_id = location_faulty_id
            else:
                location_dest_id = location_id

        if category == 'waste':
            if not name:
                name = 'Abfall'
            if location_waste_id:
                location_dest_id = location_waste_id
            else:
                location_dest_id = location_id
        # FIXME - must be calculated

        if not product_id:
            move_value_cost = 0.0
        else:
            product = self.pool.get('product.product').browse(cr, uid, [product_id])[0]
            if product:
                move_value_cost = round(product.standard_price * product_qty,2)

        result['name'] = name
        result['category'] = category
        result['category_prod'] = category
        result['location_id'] = location_id
        result['location_dest_id'] = location_dest_id
        result['prodlot_id'] = prodlot_id
        result['product_packaging_id'] = product_packaging_id
        result['product_id'] = product_id
        result['product_uom'] = product_uom
#        result['price_unit_id'] = price_unit_id
#        result['move_value_cost'] = move_value_cost
        return {'value':result}
stock_move()

# -----------------------------------------
# Sale Order modified
# -----------------------------------------
class sale_order(osv.osv):
    _inherit = "sale.order"

    def _product_names(self, cr, uid, ids, names=None, arg=False, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context):
            res[line.id] = False
            products = ''
            for move in line.order_line:
                if move.product_id.name:
                    if  ( len(products)  + len(move.product_id.name) ) <= 253.0 :
                        if len(products) == 0.0:
                            products = move.product_id.name
                        else:
                            products = products + ', ' + move.product_id.name
            res[line.id] = products
        return res

    _columns = \
        { 'order_line'    : fields.one2many
            ( 'sale.order.line'
            , 'order_id'
            , 'Order Lines'
            , readonly=True
            , states={'draft': [('readonly', False)], 'progress': [('readonly', False)]}
            )
        , 'product_names' : fields.function
            ( _product_names
            , method=True
            , type='char'
            , size=256
            , string='Products'
            , help="Shows ordered products"
            , readonly=True
            )
        }

sale_order()

# -----------------------------------------
# Sale Order Line modified
# -----------------------------------------

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _move_state(self, cr, uid, ids, names=None, arg=False, context=None):
        _logger = logging.getLogger(__name__)
        res = {}
        for line in self.browse(cr, uid, ids, context):
            _logger.debug('FGF move_state line %s' % (line))
            res[line.id] = False
            for move in line.stock_dispo_production_ids:
                _logger.debug('FGF move_state state %s' % (move.state))
                if move.state == 'draft':
                    res[line.id]  = True
        return res

    _states_mask = {'draft': [('readonly', False)], 'confirmed': [('readonly', False)]}
    _columns = \
        { 'quality'                          : fields.char
            ( 'Ordered Quality'
            , size=16
            , help="This will be copied to Quality for each sale line"
            , readonly=True
            , states=_states_mask
            )
        , 'location_product_id'              : fields.many2one
            ( 'stock.location'
            , 'Production Location'
            , help="Field where products were grown (AMA)"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'location_id'                      : fields.many2one
            ( 'stock.location'
            , 'Source Location'
            , help="Products will be taken from this location"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'location_dest_id'                 : fields.many2one
            ( 'stock.location'
            , 'Dest. Location'
            , help="Products will be shipped to this location"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'location_big_id'                  : fields.many2one
            ( 'stock.location'
            , 'Dest. Location Big'
            , help="Too big products will be moved to this location, defaults to source"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'location_small_id'                : fields.many2one
            ( 'stock.location'
            , 'Dest. Location Small'
            , help="Too small products will be moved to this location, defaults to source"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'location_faulty_id'               : fields.many2one
            ( 'stock.location'
            , 'Dest. Location Faulty'
            , help="Faulty products will be moved to this location, set default manually"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'location_waste_id'                : fields.many2one
            ( 'stock.location'
            , 'Dest. Location Waste'
            , help="Waste will be moved to this location, set default manually"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'trading_unit_owner_id'            : fields.many2one
            ( 'res.partner'
            ,'Owner of Trading Unit'
            , help="This will create appropriate text on picking, packing and labels"
            , readonly=True
            , states=_states_mask
            , ondelete='restrict'
            )
        , 'prodlot_id'                       : fields.many2one
            ( 'stock.production.lot'
            , 'Production Lot'
            , readonly=True
            , states=_states_mask
            , help="Production lot is used to track the production"
            , ondelete='restrict'
            )
        , 'stock_dispo_production_sale_ids'  : one2many_sorted.one2many_sorted
            ( 'stock.move'
            , 'order_line_id'
            , 'To Sell'
            , readonly=True
            , states=_states_mask
            , search=[('category', '=', 'sell')]
            , order  = 'id'
        #    , set={'category' : 'sell'}
            )
        , 'stock_dispo_production_small_ids' : one2many_sorted.one2many_sorted
            ( 'stock.move'
            , 'order_line_id'
            , 'To Small'
            , readonly=True
            , states=_states_mask
            , search=[('category', '=', 'small')]
            , order  = 'id'
        #    , set={'category' : 'small'}
            )
        , 'stock_dispo_production_big_ids'   : one2many_sorted.one2many_sorted
            ( 'stock.move'
            , 'order_line_id'
            , 'To Big'
            , readonly=True
            , states=_states_mask
            , search=[('category', '=', 'big')]
            , order  = 'id'
        #    , set={'category' : 'big'}
            )
        , 'stock_dispo_production_faulty_ids': one2many_sorted.one2many_sorted
            ( 'stock.move'
            , 'order_line_id'
            , 'Faulty'
            , readonly=True
            , states=_states_mask
            , search=[('category', '=', 'faulty')]
            , order  = 'id'
        #    , set={'category' : 'faulty'}
            )
        , 'stock_dispo_production_waste_ids' : one2many_sorted.one2many_sorted
            ( 'stock.move'
            , 'order_line_id'
            , 'Waste'
            , readonly=True
            , states=_states_mask
            , search=[('category', '=', 'waste')]
            , order  = 'id'
            )
        , 'stock_dispo_production_draft_ids' : one2many_sorted.one2many_sorted
            ( 'stock.move'
            , 'order_line_id'
            , 'Draft'
            , readonly=True
            , states=_states_mask
            , search=[('state', '=', 'draft')]
            , order  = 'id'
        #.    , set={'category' : 'waste'}
            )
        , 'stock_dispo_production_ids'       : fields.one2many
            ( 'stock.move'
            , 'order_line_id'
            , 'Dispo Production'
            , readonly=True
            , states=_states_mask
            )
        , 'product_packaging_id'             : fields.many2one
            ( 'product.product'
            , 'Packaging'
            , help='Product wich is used to store the main product'
            , ondelete='restrict'
            )
        , 'move_state'                       : fields.function
            ( _move_state
            , method=True
            , type='boolean'
            , string='Move State'
            , help="Returns true if some moves are not done"
            ,
            )
        }

    def move_action_done(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        for line in self.browse(cr, uid, ids, context):
            for move in line.stock_dispo_production_ids:
                #FIXME performance !
                if move.state !='done':
                    self._logger.debug('moves production to do `%s`', move.id)
                    move_obj.action_done(cr, uid, [move.id], context=context)

sale_order_line()

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'
    _columns = \
        { 'global_gap_number' : fields.char
            ( 'Global-Gap-Nr'
            , size=16
            , help="""GLOBALG.A.P introduced the GLOBALG.A.P number (GGN) to identify each legal entity regis-
tered (individual producers) in the GLOBALG.A.P database. This 13-digit number (e.g.
4049929000000) is unique and remains valid and attached to the legal entity as long as it exists.
It serves as search key on the GLOBALG.A.P website to validate certificates.
Remark:
We put it here, because
* it changes with every harvest and
* may overlap calendar years and harvests periods and
* is only necessary/valid for certain products
to avoid data entry for every Sales Order
 """
            )
        }
stock_production_lot()

#class stock_move(osv.osv):
#      _inherit = "stock.move"
#      _columns = {
#          'stock_dispo_production_ids': fields.one2many('stock.move','move_id','Dispo Production'),
#          'product_packaging_id' : fields.many2one('product.product', 'Default Packaging', help='Product wich is used to store the main product') ,
#          'packaging_qty'  : fields.integer ('Packaging Qty'),#
#
#      }
#stock_move()
