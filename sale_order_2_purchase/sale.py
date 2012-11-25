# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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
#import logging
import netsvc

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _create_intercompany_purchase_order(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """ create an intercompany purchase order based on sale order
        """
        if not context:
            context = {}
        ctx = {}
        
        company_obj =  self.pool.get('res.company')
        partner_o_id = order.partner_id.id
        comp_o_id = company_obj.search(cr, uid, [('partner_id','=',partner_o_id)])[0]
        if not comp_o_id:
            return False
        
        ctx['company_id'] = comp_o_id
        
        po_obj = self.pool.get('purchase.order')
        pol_obj = self.pool.get('purchase.order.line')
        po_price_list_obj =  self.pool.get('product.pricelist')
        warehouse_obj = self.pool.get('stock.warehouse')
        sequence_obj = self.pool.get('ir.sequence')
        
        price_list_o_id = po_price_list_obj.search(cr, uid, [('company_id','=',comp_o_id),('type','=','purchase')])
        if not price_list_o_id:
             price_list_o_id = po_price_list_obj.search(cr, uid, [('type','=','purchase')])
        
        seq_o_id = sequence_obj.search(cr, uid, [('company_id','=',comp_o_id),('code','=','purchase.order')])
        name_po = sequence_obj.next_by_id( cr, uid, seq_o_id, context=ctx)
        
        warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=', comp_o_id)], context=ctx)
        for warehouse in warehouse_obj.browse(cr, uid, warehouse_id):
            location_id = warehouse.lot_input_id.id
            
        vals_po = {
            'name' : name_po 
           ,'company_id' : comp_o_id
           ,'partner_id' : order.company_id.partner_id.id
           ,'partner_address_id' : order.company_id.partner_id.address[0].id #FIXME better choice
           ,'partner_ref': order.client_order_ref
           ,'date_order' : order.date_order
           ,'pricelist_id': price_list_o_id[0]
           ,'location_id': location_id,
            
            }
        po_id = po_obj.create(cr, uid, vals_po, ctx)
        
        x_rate = ''
        # FIXME currency conversion missing

        
        for line in order_lines:
            vals_pol = {
                 'order_id' : po_id,
                 'name': line.name,
                 #'origin': order.name,
                 'date_planned':  order.date_order,
                 'product_id': line.product_id.id,
                 'product_qty': line.product_uom_qty,
                 'product_uom': line.product_uom.id,
                 'product_uos_qty': (line.product_uos and line.product_uos_qty) or line
                 .product_uom_qty,
                 'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
                 'price_unit' : x_rate and line.price_unit * x_rate or line.price_unit,
                 
                 #'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                 #'procure_method': line.type,
                 #'move_id': move_id,
                 'company_id': comp_o_id,
                 'note': line.notes
                
                }
            pol_obj.create(cr, uid, vals_pol, ctx)   
        
        #wf_service = netsvc.LocalService("workflow")
        #wf_service.trg_create(uid, 'purchase.order', po_id, cr)
        
        po_obj.wkf_confirm_order(cr, uid, [po_id], context=ctx)

      
            
            
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        res = super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id, context)
        res1 = self._create_intercompany_purchase_order(cr, uid, order, order_lines, picking_id, context)
        return res
    
sale_order()

