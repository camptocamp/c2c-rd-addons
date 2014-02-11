# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2010-04-03 21:47:30+02
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
import time
from openerp.osv import fields,osv
#import pooler
from mx.DateTime import now, DateTime, localtime
from openerp.tools.translate import _

class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
    'water_content'  : fields.float   ('Humidity', digits=(5,2)),
    'temperature'    : fields.float   ('Temperature', digits=(4,1)),
    'specific_weight': fields.float   ('Specific Weight', digits=(5,2)),
    'protein'        : fields.float   ('Protein', digits=(5,2)),
    'sample'         : fields.char    ('Sample Number', size=16),
    'aspirates'      : fields.boolean ('Aspirates'),
    'weighing_slip'  : fields.integer ('Weighing Slip Number'),
    'packaging_qty'  : fields.integer ('Packaging Qty'),
    'product_packaging_id' : fields.many2one('product.product', 'Packaging', help='Product which is used to store the main product') ,
    }

#_defaults = {
#        'location_id': lambda *a: '',
#        'location_dest_id': lambda *a: '',
#        'state': lambda *a: 'draft',
#        'priority': lambda *a: '1',
#        'product_qty': lambda *a: 0.0,
        #'date_planned': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        #'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
#        'date_planned': lambda *a: '',
#        'date': lambda *a: '',
#    }


    def onchange_harvest_product_qty(self, cr, uid, ids, product_qty, product_id, product_uom, date_planned,prodlot_id,location_src_id,location_dest_id,product_packaging_id):
        res = {}
        if product_id and product_qty and product_qty > 0.0:
            prod_obj    = self.pool.get('product.product').browse(cr, uid, product_id)
            pu_id = prod_obj.price_unit_id.id
            move_value = 0.0
            res = {'value' : {
             'product_id' : product_id,
             'date_expected' : time.strftime('%Y-%m-%d %H:%M:%S'),
             'date_planned' : date_planned,
             'date'         : time.strftime('%Y-%m-%d %H:%M:%S'),
             'product_uom' : product_uom,
             'location_id' : location_src_id,
             'location_dest_id' : location_dest_id,
             'price_unit_id' : pu_id,
             'price_unit' : prod_obj.standard_price * product_qty,
             'name' : _('Harvest'),
             'prodlot_id' : prodlot_id ,
             'product_packaging_id' : product_packaging_id,
               }
            }
            #raise osv.except_osv(_('Test Error 2'),
            #             _('Trigger Qty = %s',) % (product_qty))

        return res

stock_move()

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns = {
       'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', help="Production lot is used to adminster production lots"),
       'product_packaging': fields.many2one('product.packaging', 'Packaging'),
       'product_packaging_id' : fields.many2one('product.product', 'Packaging', help='Product wich is used to store the main product') ,
       'packaging_qty'  : fields.integer ('Packaging Qty'),
    }

    def button_post_moves(self, cr, uid, ids, *args):
        # ugly I know
        for mrp in self.browse(cr, uid, ids):
            for move in mrp.move_created_ids:
                self.pool.get('stock.move').action_done(cr, uid,  [move.id])




mrp_production()
