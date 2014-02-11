# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools import config
from openerp.tools.sql import drop_view_if_exists

class chricar_report_location_moves(osv.osv):
        _name = "chricar.report.location.moves"
        _description = "Location Moves"
        _auto = False
        _columns = {
                'company_id'  : fields.many2one('res.company', 'Company', readonly=True),
                'name'        : fields.char ('Name',size=16, readonly=True),
                'picking_id'  : fields.many2one('stock.picking','Stock Picking', readonly=True),
                'product_id'  : fields.many2one('product.product', 'Product', readonly=True),
                'location_id' : fields.many2one('stock.location', 'Location', readonly=True),
                'partner_id'  : fields.many2one('res.partner', 'Partner', readonly=True),
                'period_id'   : fields.many2one('account.period', 'Period', readonly=True),
                'prodlot_id'  : fields.many2one('stock.production.lot', 'Production Lot', readonly=True),
                'date'        : fields.date    ('Date',readonly=True),
                'product_qty' : fields.float('Quantity', readonly=True),
                'move_value_cost' : fields.float('Cost Value', readonly=True),
                'move_value_sale' : fields.float('Sale Value', readonly=True),
                'cost_price' : fields.float('Cost Price', readonly=True),
                'sale_price' : fields.float('Sale Price', readonly=True),
                'value_correction': fields.float('Value Correction', readonly=True),
                'usage'      : fields.related('location_id','usage',type="char", relation="stock.location", string="Usage", readonly=True),
                'variants'   : fields.related('product_id','variants',type="char", relation="product.product", string="Variants", readonly=True),
                'categ_id'   : fields.related('product_id','categ_id',type="many2one", relation="product.category", string="Category", readonly=True),
                'state'      : fields.selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Canceled')], 'Status', readonly=True, select=True),

        }
        _order = 'product_id'
        def init(self, cr) :
                drop_view_if_exists(cr, "chricar_location_move_col")
                drop_view_if_exists(cr, "chricar_report_location_moves_sum")
                drop_view_if_exists(cr, "chricar_report_location_moves")
                
                cr.execute("""
                create or replace view chricar_report_location_moves
                as (
                select id*2 as id,name,
                     picking_id,product_id, 
                     location_dest_id as location_id,
                     partner_id,period_id,prodlot_id,
                     date,
                     product_qty,move_value_cost,move_value_sale,
                     case when product_qty != 0 then  move_value_cost/product_qty  else 0 end as cost_price,
                     case when product_qty != 0 then  move_value_sale/product_qty  else 0 end as sale_price,
                     value_correction,
                     state, company_id
                from stock_move
                    
                union all
                select id*2-1 as id,name,
                     picking_id,product_id, 
                     location_id,
                     partner_id,period_id,prodlot_id,
                     date,
                     -product_qty,-move_value_cost,-move_value_sale,
                     case when product_qty != 0 then  move_value_cost/product_qty  else 0 end as cost_price,
                     case when product_qty != 0 then  move_value_sale/product_qty  else 0 end as sale_price,
                     -value_correction,
                     state, company_id
                from stock_move
                    
                   )
                """)
chricar_report_location_moves()


class chricar_report_location_moves_sum(osv.osv):
        _name = "chricar.report.location.moves.sum"
        _description = "Location Product Sum"
        _auto = False
        _columns = {
                'product_id'  : fields.many2one('product.product', 'Product', readonly=True),
                'location_id' : fields.many2one('stock.location', 'Location', readonly=True),
                'product_qty' : fields.float('Quantity', readonly=True),
                'move_value_cost' : fields.float('Cost Value', readonly=True),
                'move_value_sale' : fields.float('Sale Value', readonly=True),
                'cost_price' : fields.float('Cost Price', readonly=True),
                'sale_price' : fields.float('SAle Price', readonly=True),
                'usage'      : fields.related('location_id','usage',type="char", relation="stock.location", string="Usage", readonly=True),
                'categ_id'   : fields.related('product_id','categ_id',type="many2one", relation="product.category", string="Category", readonly=True),
        }
        _order = 'product_id'        
        def init(self, cr):
                drop_view_if_exists(cr, "chricar_report_location_moves_sum")
                cr.execute("""
                create or replace view chricar_report_location_moves_sum
                as ( 
                select min(id) as id, 
                 product_id,location_id, 
                 sum(product_qty) as product_qty,
                 sum(move_value_cost) as move_value_cost,
                 sum(move_value_sale) as move_value_sale, 
                 case when sum(product_qty) != 0 then  sum(move_value_cost)/sum(product_qty)  else 0 end as cost_price,
                 case when sum(product_qty) != 0 then  sum(move_value_sale)/sum(product_qty)  else 0 end as sale_price
                from chricar_report_location_moves
                where state ='done'
                group by product_id,location_id
                   )
                """)
chricar_report_location_moves_sum()


class chricar_location_move_col(osv.osv):
        _name = "chricar.location.move.col"
        _description = "Reporting columns for stock move aggregate"
        _auto = False
        _columns = {
                'company_id'  : fields.many2one('res.company', 'Company', readonly=True),
                'product_id'  : fields.many2one('product.product', 'Product', readonly=True),
                'location_id' : fields.many2one('stock.location', 'Location', readonly=True),
                'picking_id'  : fields.many2one('stock.picking', 'Picking', readonly=True),
                'prodlot_id'  : fields.many2one('stock.production.lot', 'Production Lot', readonly=True),
                'date'        : fields.datetime('Date Time', readonly=True),
                'date2'       : fields.date('Date', readonly=True),
                'period_id'   : fields.many2one('account.period', 'Period', readonly=True),
                'product_qty'   : fields.float('Quantity', readonly=True),
                'qty_plus'      : fields.float('Qty Plus', readonly=True),
                'qty_minus'     : fields.float('Qty Minus', readonly=True),
                'qty_inventory' : fields.float('Qty Inventory', readonly=True),
                'move_value_cost': fields.float('Cost', readonly=True),
                'cost_plus'      : fields.float('Cost Plus', readonly=True),
                'cost_minus'     : fields.float('Cost Minus', readonly=True),
                'cost_inventory' : fields.float('Cost Inventory', readonly=True),
                'state'      : fields.selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Confirmed'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Canceled')], 'Status', readonly=True, select=True),
                'categ_id'   : fields.related('product_id','categ_id',type="many2one", relation="product.category", string="Category", readonly=True),
        }
        _order = 'product_id'        
        def init(self, cr):
                drop_view_if_exists(cr, "chricar_location_move_col")
                cr.execute("""
                create or replace view chricar_location_move_col as (
select id,company_id, product_id,location_id, picking_id, prodlot_id,
       date, date::date as date2,period_id,
       product_qty,
       case when product_qty >0 then product_qty else 0 end as qty_plus ,
       case when product_qty <0 then product_qty else 0 end as qty_minus,
       0 as qty_inventory,
       move_value_cost,
       case when move_value_cost >0 then move_value_cost else 0 end as cost_plus ,
       case when move_value_cost <0 then move_value_cost else 0 end as cost_minus,
       0 as cost_inventory,state
       from chricar_report_location_moves
       where state ='done' 
       and value_correction is null 
       and id not in (select 2*move_id from stock_inventory_move_rel
                      union
                      select 2*move_id-1 from stock_inventory_move_rel)
           
union all      
select id,company_id, product_id, location_id, picking_id, prodlot_id,
       date,date::date as date2,period_id,
       product_qty,
       0,0,
       product_qty as qty_inventory,
       move_value_cost,
       0,0,
       move_value_cost as cost_inventory,state
       from chricar_report_location_moves
       where state ='done'
       and (value_correction is not null
        or id  in (select 2*move_id from stock_inventory_move_rel
                      union
                      select 2*move_id-1 from stock_inventory_move_rel)
           )
)""")
           
chricar_location_move_col()
