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
from openerp.osv import fields, osv
import openerp.netsvc
import logging


class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
          'picking_o_ids': fields.many2many('stock.picking', 'purchse_o_picking_rel', 'purchase_id', 'picking_id', 'Intercompany Picking', readonly=True),
    }

purchase_order()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _columns = {
          'sale_order_id': fields.related('purchase_id', 'sale_order_id', type="many2one", relation="sale.order", string='Intercompany Sale Order', help="Picking/Purchase order generted based on this intercompany sale order", readonly = True),
    }

    def button_update_so2po_move(self, cr, uid, ids, context=None):
        if not context :
           context = {}
        for pick in self.browse(cr, 1, ids, context):
            if not pick.sale_order_id :
                return True
            _logger = logging.getLogger(__name__)
            
            move_obj = self.pool.get('stock.move')
            sale_obj = self.pool.get('sale.order')
            purchase_obj = self.pool.get('purchase.order')
            
            picking_o_used_ids = [] # picking already used to set lots
            _logger.debug('FGF pic %s', pick.purchase_id.picking_o_ids)
            for o in pick.purchase_id.picking_o_ids:
                _logger.debug('FGF pic %s',o )
                picking_o_used_ids.append(o.id)
            picking_o_ids = []
            _logger.debug('FGF picking_o_used_ids %s',picking_o_used_ids )
            
            for sale in sale_obj.browse(cr, 1, [pick.sale_order_id.id], context):
                for p in sale.picking_ids:
                    _logger.debug('FGF picking_o_ids %s', p)
                    if p.id not in picking_o_used_ids and p.state in ('done'):
                        picking_o_ids.append(p.id)
            _logger.debug('FGF picking_o_ids %s', picking_o_ids)
            if not picking_o_ids:
                return True
            
            picking_o_ids2 = ','.join([str(id) for id in picking_o_ids])
            sql="""
            select product_id, product_qty, prodlot_id, price_unit*product_qty as move_value_sale
              from stock_move
             where picking_id in (%s)
               and state = 'done'
            """
            cr.execute(sql % picking_o_ids2)
            moves_o = {} # mves found in related picking
            for  product_id, product_qty, prodlot_id, move_value_sale in cr.fetchall(): 
                moves_o[product_id] = {'product_qty': product_qty, 'prodlot_id': prodlot_id, 'move_value_sale': move_value_sale}
            _logger.debug('FGF moves_o %s', moves_o)
            # FIXME - check for duplicte product id's !!!
            for line in pick.move_lines:
                vals = {}
                _logger.debug('FGF line  %s', line)
                m_id = line.product_id.id
                _logger.debug('FGF m_id  %s', m_id)
                if line.product_qty != moves_o[m_id]['product_qty']:
                    vals['product_qty'] =   moves_o[m_id]['product_qty']
                if moves_o[m_id]['prodlot_id']:
                    vals['prodlot_id'] =   moves_o[m_id]['prodlot_id']
                if line.move_value_cost !=  moves_o[m_id]['move_value_sale'] and moves_o[m_id]['product_qty'] != 0:
                    vals['price_unit'] =   moves_o[m_id]['move_value_sale'] / moves_o[m_id]['product_qty']
                    vals['move_value_cost'] =   moves_o[m_id]['move_value_sale']
                if vals:
                    _logger.debug('FGF write %s', vals)
                    move_obj.write(cr, uid, [line.id], vals)
                    
            for p_o_id in picking_o_ids:
                _logger.debug('FGF write p_o_id %s', p_o_id)
                purchase_obj.write(cr, uid, [pick.purchase_id.id], {'picking_o_ids': [(4, p_o_id)]})
            
        return True 
    
stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"

    def create(self, cr, uid, vals, context=None):
        """
        workaround to make inserted product available for validate process
        """
        new_id = super(stock_move, self).create(cr, uid, vals, context)
        for move in self.browse(cr, uid, [new_id]):
            if move.picking_id and move.picking_id.sale_order_id and move.product_id.company_id:
                product_obj = self.pool.get('product.product')
                product_obj.write(cr, 1, [move.product_id.id] , {'company_id':'' })
        return new_id 
        
stock_move()
