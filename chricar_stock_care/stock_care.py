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
import openerp.netsvc
from openerp.tools.misc import UpdateableStr, UpdateableDict

class stock_move(osv.osv):
    _inherit = "stock.move"

    _activity_values = [
                             ('dehumidify','Dehumidify'),
                             ('restore','Restore'),
                             ('aspirate','Aspirate'),
                             ('purify','Purify'),
                             ('check','Check'),
      ]

    #ACTIVITY_SELECTION = UpdateableDict()
    ACTIVITY_SELECTION = {
                             'dehumidify':'Dehumidify',
                             'restore':'Restore',
                             'ventilate':'Ventilate',
                             'aspirate':'Aspirate',
                             'purify':'Purify',
                             'check':'Check',
      }
    #ACTIVITY_SELECTION.__init__(_ACTIVITY_SELECTION)

    _columns = {
#       'activity'           : fields.selection(_activity_values,'Activity', size=16, required=True, translate=True ),
      'activity'           : fields.selection([(k,v) for k,v in ACTIVITY_SELECTION.items()],'Activity', size=16,  translate=True ),
      'humidity'           : fields.float   ('Humidity Source', help="If In and Out are measured and a factor exists the quantity will be reduced"),
      'humidity_dest'      : fields.float   ('Humidity Destination', help="If In and Out are measured and a factor exists the quantity will be reduced"),
      'factor'             : fields.float   ('Factor', help="If In and Out are measured and a factor exists the quantity will be reduced"),
      'product_dest_qty'      : fields.float   ('Quantity Destination'),
      'location_loss_id'   : fields.many2one('stock.location', 'Production Loss Location', help="This location will be used to move production loss from destination location"),
    }

    def onchange_product_id_activity(self, cr, uid, ids,product_id,activity):
        if not product_id:
            return {}
        product = self.pool.get('product.product').browse(cr, uid, [product_id])[0]

        result = {
            'name'            : stock_move.ACTIVITY_SELECTION.get(activity),
#            'name'            : activity,
            'product_uom'     : product.uom_id.id,
            'price_unit_id'   : product.price_unit_id.id,
            'price_unit'      : product.standard_price ,
            'price_unit_pu'   : product.standard_price_pu ,
            'date_expected'   : time.strftime('%Y-%m-%d %H:%M:%S'),
            'date'            : time.strftime('%Y-%m-%d %H:%M:%S'),
            'product_qty'     : 0.0,
            'factor'          : '',
        }
        return {'value': result}

    def onchange_factor(self, cr, uid, ids,product_qty,factor,price_unit_coeff):
        result = {
                'product_dest_qty' :  product_qty ,
          }

        if factor and product_qty:
            result = {
               'product_dest_qty' :  product_qty * (1 - factor / 100),
            }
        result['move_value_cost'] = product_qty * price_unit_coeff
        return {'value': result}

    def onchange_lot_id_care(self, cr, uid, ids,prodlot_id=False, product_qty=False, location_id=False, context=None):
        #copied from stock.py
        if not prodlot_id or not location_id:
            return {}
        ctx = context and context.copy() or {}
        ctx['location_id'] = location_id
        prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, ctx)
        location = self.pool.get('stock.location').browse(cr, uid, location_id)
        warning = {}
        if (location.usage == 'internal') and (product_qty > (prodlot.stock_available or 0.0)):
            warning = {
                'title': 'Bad Lot Assignation !',
                'message': 'You are moving %.2f products but only %.2f available in this lot.' % (product_qty, prodlot.stock_available or 0.0)
            }
            return {'warning': warning}

        # FIXME should location_id be part of query => price per location ?
        if prodlot.stock_available > 0.0 and prodlot.move_value_cost > 0.0 :
            price_unit_coeff = prodlot.stock_available / prodlot.move_value_cost
            return {'value' : { 'price_unit_coeff' : price_unit_coeff }}


stock_move()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def draft_validate_care(self, cr, uid, ids, *args):
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            if len(pick.move_lines):
                for move in pick.move_lines:
                    if move.product_qty != move.product_dest_qty:
                        move = self.pool.get('stock.move').create(cr, uid, {
                            'name': move.name,
                            'product_id': move.product_id.id,
                            'product_qty': move.product_qty - move.product_dest_qty,
    #                        'product_uos_qty': move.product_qty,
                            'product_uom': move.product_uom.id,
    #                        'product_uos': move.product_uom.id,
                            'date_expected': move.date_expected,
                            'location_id': move.location_dest_id.id,
                            'location_dest_id': move.location_loss_id.id,
                            'picking_id': move.picking_id.id,
    #                        'move_dest_id': move.move_dest_id.id,
                            'state': 'draft',
                            'date': move.date_expected,
                            'price_unit' :move.price_unit,
                            'price_unit_id' :move.price_unit_id.id,
    #                        'price_unit_coeff' : move.price_subtotal/move.product_qty,
                            'move_value_cost':  ( move.product_qty - move.product_dest_qty ) * move.price_unit_coeff,
                            'activity' : move.activity,
                            'prodlot_id': move.prodlot_id.id,
                        })
                        #self.pool.get('stock.move').write(cr, uid, [move.move_dest_id.id], {'location_id':order.location_id.id})
        # we have to reerad the moves because some may have created above
        for pick in self.browse(cr, uid, ids):
            self.draft_force_assign(cr, uid, ids)
            move_ids = [x.id for x in pick.move_lines]
            self.pool.get('stock.move').force_assign(cr, uid, move_ids)
            wf_service.trg_write(uid, 'stock.picking', pick.id, cr)

            self.action_move(cr, uid, [pick.id])
            wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
        return True

stock_picking()
