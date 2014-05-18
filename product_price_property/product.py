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
import openerp.addons.decimal_precision as dp
import logging

class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
      'list_price': fields.property(
            relation='product.product',
            type='float',
            digits_compute=dp.get_precision('Sale Price'),
            string="Sale Price",
            view_load=None,
            group_name=None,
            help="Base price for computing the customer price. Sometimes called the catalog price."),
      'standard_price': fields.property(
            relation='product.product',
            type='float',
            digits_compute=dp.get_precision('Purchase Price'),
            string="Cost Price",
            view_load=None,
            group_name=None,
            help="Product's cost for accounting stock valuation. It is the base price for the supplier price."),
       # 'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Sale Price'), help="Base price for computing the customer price. Sometimes called the catalog price."),
       # 'standard_price': fields.float('Cost Price', required=True, digits_compute=dp.get_precision('Purchase Price'), help="Product's cost for accounting stock valuation. It is the base price for the supplier price."),

        }

    def init(self, cr):

        sql = """
        insert into ir_property(res_id,type,company_id,name,value_float,fields_id)
        select 'product.product,'||p.id , 'float', t.company_id, 'list_price',list_price,f.id
          from product_template t,
               product_product p,
               ir_model_fields f
         where t.id = p.product_tmpl_id
           and list_price is not null
           and f.name = 'list_price'
           and f.model='product.product'
           except select res_id,type,company_id,name,value_float,fields_id from ir_property
           ;
        """
        cr.execute(sql)
        sql = """
        insert into ir_property(res_id,type,company_id,name,value_float,fields_id)
        select 'product.product,'||p.id , 'float', t.company_id, 'standard_price',standard_price,f.id
          from product_template t,
               product_product p,
               ir_model_fields f
         where t.id = p.product_tmpl_id
           and list_price is not null
           and f.name = 'standard_price'
           and f.model='product.product'
           except select res_id,type,company_id,name,value_float,fields_id from ir_property
           ;
        """
        cr.execute(sql)
      
        # for performane reasons we must use SQL inserts       
        sql = """
        select t.id as template_id, t.list_price, t.standard_price, p.id as product_id , t.company_id
          from product_template t,
               product_product p
         where t.id = p.product_tmpl_id
         order by p.id;
        """   
        #property_obj = self.pool.get('ir.property')
        #for template_id, list_price, standard_price, product_id, company_id in cr.fetchall():
        #    vals = {
        #         'res_id': 'product.product,'+str(product_id), 
        #         'type': 'float',
        #         'company_id': company_id,
        #        }
        #    if list_price:
        #        vals.update({ 'name' : 'list_price', 'value_float': list_price})
        #        property_obj.create(cr, 1, vals)
        #    if standard_price:
        #        vals.update({ 'name' : 'standard_price', 'value_float': standard_price})
        #        property_obj.create(cr, 1, vals)
        # 
        # this creates one record per company . wrong !!!
        # self.write(cr, 1, [product_id], {'list_price': list_price, 'standard_price': standard_price} , context = {'company_id': company_id})
        
product_product()
