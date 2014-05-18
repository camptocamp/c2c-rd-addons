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
          'sale_order_id': fields.many2one('sale.order', 'Sale Order Reference', help="Purchase order generted based on this sale order"),
    }

purchase_order()

class sale_order(osv.osv):
    _inherit = "sale.order"
  
# _o_ are variables of the _o_ther company

    def _comp_o_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        company_obj =  self.pool.get('res.company')
        for order in self.browse(cr, uid, ids, context=context):
            partner_o_id = order.partner_id.id
            comp_o_ids = company_obj.search(cr, uid, [('partner_id','=',partner_o_id)])
            if comp_o_ids: 
                res[order.id] =  comp_o_ids[0]
            else:
                res[order.id] =  ''
               
        return res


    _columns = {
          'comp_o_id': fields.function(_comp_o_id, method=True, type='many2one', relation='res.company', string='Partner Company',),
    }

    def _sql(self, cr,uid, comp_o_id, inc_exp,account_o_id, product_id):
                 
        sql = """
        insert into ir_property(res_id,type,company_id,name, value_reference, fields_id)
        select 'product.template,'||t.id , 'many2one', %s, 'property_account_%s','account.account,'||%s,f.id
          from product_template t,
               product_product p,
               ir_model_fields f
         where t.id = p.product_tmpl_id 
           and p.id = %s
           and f.name = 'property_account_%s'
           and f.model= 'product.template'
           except select res_id,type,company_id,name,value_reference,fields_id from ir_property
                """ % ( comp_o_id, inc_exp, account_o_id, product_id ,inc_exp) 
        return sql
                
    def _product_o_update(self, cr, uid, product_id, comp_o_id, context):
        """ create properties and VAT info forproduct
        """
        _logger = logging.getLogger(__name__)
        
        account_obj = self.pool.get('account.account')
        product_obj = self.pool.get('product.product')
        property_obj = self.pool.get('ir.property')
        tax_obj = self.pool.get('account.tax')
        
        for product in product_obj.browse(cr, uid, [product_id], context):
            # data from source company
            ctx={'company_id':comp_o_id, 'force_company':comp_o_id }
            
            # customer tax
            taxes_ids = product.taxes_id
            self._logger.debug('FGF product custom tax %s', taxes_ids) 
            taxes_o_ids = []
            for tax in taxes_ids:
                tax_o_id = tax_obj.search(cr, uid, [('company_id','=',comp_o_id),('type_tax_use','=',tax.type_tax_use),('amount','=',tax.amount)])
                if tax_o_id:
                   self._logger.debug('FGF cust tax_o_id %s', tax_o_id) 
                   taxes_o_ids.append(tax_o_id[0])
            if taxes_o_ids:
                product_obj.write(cr, uid, product_id, {'taxes_id': [(6, 0, taxes_o_ids)]  }, context=ctx)
                
            # supplier tax
            supplier_taxes_ids = product.supplier_taxes_id
            self._logger.debug('FGF product supplier_tax %s', supplier_taxes_ids) 
            taxes_o_ids = []
            for tax in supplier_taxes_ids:
                tax_o_id = tax_obj.search(cr, uid, [('company_id','=',comp_o_id),('type_tax_use','=',tax.type_tax_use),('amount','=',tax.amount)])
                if tax_o_id:
                   self._logger.debug('FGF supp tax_o_id %s', tax_o_id) 
                   taxes_o_ids.append(tax_o_id[0])
            if taxes_o_ids:
                product_obj.write(cr, uid, product_id, {'supplier_taxes_id': [(6, 0, taxes_o_ids)]  }, context=ctx)
                
            # income account
            property_account_income_code = product.property_account_income.code
            self._logger.debug('FGF product income %s', property_account_income_code ) 
            account_income_o_id = account_obj.search(cr, uid, [('company_id','=',comp_o_id),('code','=',property_account_income_code)])
            if account_income_o_id:
                self._logger.debug('FGF account_income_o_id %s', account_income_o_id[0]) 
                # FIXME this does not update the correct company 
                #product_obj.write(cr, uid, product_id, {'property_account_expense':account_expense_o_id[0]}, context=ctx)
                sql = self._sql(cr,uid, comp_o_id, 'income', str(account_income_o_id[0]), product_id)
                cr.execute(sql)
            
            # expense
            property_account_expense_code = product.property_account_expense.code 
            self._logger.debug('FGF product expense code %s', property_account_expense_code ) 
            account_expense_o_id = account_obj.search(cr, uid, [('company_id','=',comp_o_id),('code','=',property_account_expense_code)])
            if account_expense_o_id:
                self._logger.debug('FGF account_expense_o_id %s', account_expense_o_id[0]) 
                # FIXME this does not update the correct company 
                #product_obj.write(cr, uid, product_id, {'property_account_expense':account_expense_o_id[0]}, context=ctx)
                # we have to insert using sql 
                sql = self._sql(cr,uid, comp_o_id, 'expense', str(account_expense_o_id[0]), product_id)
                cr.execute(sql)
                

        
    def _create_intercompany_purchase_order(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """ create an intercompany purchase order based on sale order
        """
        _logger = logging.getLogger(__name__)

        if not context:
            context = {}
        ctx = {}
        
        #company_obj =  self.pool.get('res.company')
        #partner_o_id = order.partner_id.id
        #comp_o_id = company_obj.search(cr, uid, [('partner_id','=',partner_o_id)])[0]
        #if not comp_o_id:
        #    self._logger.debug('FGF no intercompany %s', partner_o_id)
        #    return False
        comp_o_id = order.comp_o_id.id
       
        ctx={'company_id':comp_o_id, 'force_company':comp_o_id }
        
        fiscal_position_obj = self.pool.get('account.fiscal.position')
        po_obj = self.pool.get('purchase.order')
        po_price_list_obj =  self.pool.get('product.pricelist')
        pol_obj = self.pool.get('purchase.order.line')
        product_obj = self.pool.get('product.product')
        product_obj = self.pool.get('product.product')
        sequence_obj = self.pool.get('ir.sequence')
        so_obj = self.pool.get('sale.order')
        tax_obj = self.pool.get('account.tax')
        warehouse_obj = self.pool.get('stock.warehouse')
        
        
        price_list_o_id = po_price_list_obj.search(cr, uid, [('company_id','=',comp_o_id),('type','=','purchase')])
        if not price_list_o_id:
             price_list_o_id = po_price_list_obj.search(cr, uid, [('type','=','purchase')])
        
        seq_o_id = sequence_obj.search(cr, uid, [('company_id','=',comp_o_id),('code','=','purchase.order')])
        name_po = sequence_obj.next_by_id( cr, uid, seq_o_id, context=ctx)
        
        warehouse_id = warehouse_obj.search(cr, uid, [('company_id', '=', comp_o_id)], context=ctx)
        for warehouse in warehouse_obj.browse(cr, uid, warehouse_id):
            location_id = warehouse.lot_input_id.id
        
        partner_o_id = order.company_id.partner_id.id
        
        
        fiscal_position_id =  order.company_id.partner_id.property_account_position and order.company_id.partner_id.property_account_position.id
        
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
           ,'sale_order_id' : order.id
            }
        po_id = po_obj.create(cr, uid, vals_po, ctx)

        for po_o in po_obj.browse(cr, uid, [po_id]):
            po_name = po_o.name
            for so in so_obj.browse(cr,uid, [order.id]):
                so_obj.write(cr, uid, [so.id], { 'client_order_ref' : order.client_order_ref +' ('+po_name+')' })

        
        x_rate = ''
        # FIXME currency conversion missing

        ctx['partner_id'] = order.company_id.partner_id.id
        for line in order_lines:
            # we need to create account properties and tax info in ther company if these are missing
            self._product_o_update(cr, uid, line.product_id.id, comp_o_id, context)
            
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
      
                
            
    #def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
    #    res = super(sale_order, self)._create_pickings_and_procurements(cr, uid, order, order_lines, picking_id, context)
    #    res1 = self._create_intercompany_purchase_order(cr, uid, order, order_lines, picking_id, context)
    #    return res
    
    def button_create_so_2_po(self, cr, uid, ids, context=None):
        """ button to create PO for already confirmed SO
        """
        _logger = logging.getLogger(__name__)
        context = context or {}
        for order in self.browse(cr, uid, ids, context):
            order_lines = order.order_line
            self._logger.debug('FGF order %s', order, order_lines)
            self._create_intercompany_purchase_order(cr, uid, order, order_lines, False, context)
        
    
        
sale_order()

