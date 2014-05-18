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
#import logging

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        """ This will automatically choose the oldest production lot and location with qty > 0
        """
        prodlot_obj = self.pool.get('stock.production.lot')
        stock_location_obj = self.pool.get('stock.location')
        
        res = super(sale_order, self)._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context)
        
        product_id = res['product_id']
        lot_ids = prodlot_obj.search(cr, uid, [('product_id','=', product_id)])
        lot_where = ' '
        if lot_ids:        
	    lot_where = ' and m.prodlot_id in (' + ','.join([str(id) for id in lot_ids]) + ') '
        
        # find stock location with 
        top_location_id = order.shop_id.warehouse_id.lot_stock_id.id
        location_ids = stock_location_obj.search(cr, uid, [('location_id','child_of', [top_location_id]) ], context=context)
        location_where = ' ('+ ','.join([str(id) for id in location_ids]) +') ' 
        
        sql = """select l.id, m.prodlot_id,
                 sum(case when l.id = m.location_dest_id then product_qty
                      else -product_qty end) as qty_available
                 from stock_move m,
                      stock_location l
                 where m.product_id = %s %s
                   and m.state = 'done'
                   and l.usage = 'internal'
                   and l.id in  %s 
                   and (m.location_id = l.id or m.location_dest_id = l.id) 
                 group by l.id, m.prodlot_id
                 having sum(case when l.id = m.location_dest_id then product_qty
                      else -product_qty end) > 0
                 order by m.prodlot_id asc
               """ % (product_id, lot_where, location_where)
        cr.execute(sql)
        locations = cr.dictfetchall()
        
        lot_id = ''
        for r in locations:
          if not lot_id or r['prodlot_id'] < lot_id:
            lot_id = r['prodlot_id']
	    res['location_id'] = r['id']
	    if r['prodlot_id']:
               res['prodlot_id'] = r['prodlot_id']        
             
     
               
        return res
        
sale_order()

