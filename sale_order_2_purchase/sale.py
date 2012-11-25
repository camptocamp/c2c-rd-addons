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
import netsvc
import logging

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _create_intercompany_purchase_order(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """ create an intercompany purchase order based on sale order
        """
        _logger = logging.getLogger(__name__)

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
        product_obj = self.pool.get('product.product')
        tax_obj = self.pool.get('account.tax')
        product_obj = self.pool.get('product.product')
        fiscal_position_obj = self.pool.get('account.fiscal.position')
        
        
        price_list_o_id = po_price_list_obj.search(cr, uid, [('company_id','=',comp_o_id),('type','=','purchase')])
        if not price_list_o_id:
             price_list_o_id = po_price_list_obj.search(cr, uid, [('type','=','purchase')])
        
        seq_o_id = sequence_obj.search(cr, uid, [('company_id','=',comp_o_id),('code','=','purchase.order')])
        name_po = sequence_obj.next_by_id( cr, uid, seq_o_id, context=ctx)
        
        warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=', comp_o_id)], context=ctx)
        for warehouse in warehouse_obj.browse(cr, uid, warehouse_id):
            location_id = warehouse.lot_input_id.id
        
        partner_o_id = order.company_id.partner_id.id
        
        
        #fiscal_position_id =  order.company_id.partner_id.fiscal_position_id and order.company_id.partner_id.fiscal_position_id.id
        # FIXME - Not sure that we can use the fiscal position of other partner - must be a property !?
        fiscal_position_id = ''
        
        vals_po = {
            'name' : name_po 
           ,'company_id' : comp_o_id
           ,'partner_id' : partner_o_id
           ,'partner_address_id' : order.company_id.partner_id.address[0].id #FIXME better choice
           ,'partner_ref': order.client_order_ref +' ('+order.name+')'
           ,'date_order' : order.date_order
           ,'pricelist_id': price_list_o_id[0]
           ,'location_id': location_id
           ,'fiscal_position_id': fiscal_position_id
            }
        po_id = po_obj.create(cr, uid, vals_po, ctx)
        
        x_rate = ''
        # FIXME currency conversion missing

        ctx['partner_id'] = order.company_id.partner_id.id
        for line in order_lines:
            
            product = product_obj.browse(cr, uid, line.product_id.id, context=ctx)
            self._logger.debug('FGF product %s', product)            
            taxes_all = tax_obj.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
            self._logger.debug('FGF taxes_all %s', taxes_all)
            taxes = []
            for t in taxes_all:
                if t.company_id.id == comp_o_id:
                    taxes.append(t)
            self._logger.debug('FGF taxes %s', taxes)
            fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=ctx) or False
            self._logger.debug('FGF fpos %s', fpos)
            taxes_ids = fiscal_position_obj.map_tax(cr, uid, fpos, taxes)
            self._logger.debug('FGF taxes_ids %s', taxes_ids)
            
            vals_pol = {
                 'order_id' : po_id,
                 'name': line.name,
                 #'origin': order.name,
                 'date_planned':  order.date_order,
                 'product_id': line.product_id.id,
                 'product_qty': line.product_uom_qty,
                 'product_uom': line.product_uom.id,
                 #'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty ,
                 #'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
                 'price_unit' : x_rate and line.price_unit * x_rate or line.price_unit,
                 
                 #'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                 #'procure_method': line.type,
                 #'move_id': move_id,
                 'company_id': comp_o_id,
                 #'note': line.notes
                 'taxes_id' : [(6, 0, taxes_ids)],
                }
            
            self._logger.debug('FGF vals_pol %s', vals_pol)
            pol_id = pol_obj.create(cr, uid, vals_pol, ctx)  
            
              
            
            # make sure that a user without access to main company can read the product
            # FIXME
            if line.product_id.company_id:
                product_obj.write(cr, uid, [line.product_id.id], {'company_id': ''})

        
        #po_obj.wkf_confirm_order(cr, uid, [po_id], context=ctx)
        #po_obj.wkf_apprve_order(cr, uid, [po_id], context=ctx)
      
                
            
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        res = super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id, context)
        res1 = self._create_intercompany_purchase_order(cr, uid, order, order_lines, picking_id, context)
        return res
    
sale_order()

