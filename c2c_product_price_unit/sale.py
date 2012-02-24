# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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

from osv import osv, fields
import decimal_precision as dp

import math
#from _common import rounding
import re  
from tools.translate import _
        
import sys


#----------------------------------------------------------
# Sale Line INHERIT
#----------------------------------------------------------
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _get_default_id(self, cr, uid, price_unit_id, context=None):
       pu = self.pool.get('c2c_product.price.unit')
       if not pu: return 1.0
       return pu.get_default_id(cr, uid, price_unit_id, context)

    def _get_default_price_unit_pu(self, cr, uid, price_unit_id, context=None):
       pu = self.browse(cr, uid, price_unit_id)
       res  = 0.0
       if not pu:
           return res
       for p in pu:
           res = p.price_unit
       return res

    _columns = {
        'price_unit_id'    : fields.many2one('c2c_product.price_unit','Price Unit', required=True),
        'price_unit_pu'    : fields.float(string='Unit Price',digits_compute=dp.get_precision('Sale Price') , required=True, \
                            help='Price using "Price Units"') ,
        'price_unit'       : fields.float(string='Unit Price internal', required=True, digits=(16, 8), \
                            help="""Product's cost for accounting stock valuation. It is the base price for the supplier price."""),
    }
    _defaults = {
        'price_unit_id'   : _get_default_id,
        'price_unit_pu'   : _get_default_price_unit_pu,
        'price_unit'      : 0.0
        }


    def init(self, cr):
      cr.execute("""
          update sale_order_line set price_unit_pu = price_unit  where price_unit_pu is null;
      """)
      cr.execute("""
          update sale_order_line set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
      """)

    #def product_id_change_c2c_pu(self, cr, uid, ids, pricelist, product, qty=0,
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,context={}):
       res = {}
       print >>sys.stderr,'sale a0',   qty,qty_uos,uos,uom
       res = super(sale_order_line, self).product_id_change( cr, uid, ids, pricelist, product, qty=qty, 
                uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, update_tax=update_tax,
                date_order=date_order)
       print >>sys.stderr,'sale a1',   res['value']  
       if product:
           prod = self.pool.get('product.product').browse(cr, uid, product)
           price_unit_id = prod.list_price_unit_id.id
           print >>sys.stderr,'sale pu',   price_unit_id, product, u'prod.name'
           res['value']['price_unit_id'] = price_unit_id
           print >>sys.stderr,'sale pu2',  res['value']
     
           if res['value']['price_unit'] and qty:
               coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
               res['value']['price_unit_pu'] = res['value']['price_unit'] * coeff 
               print >>sys.stderr,'sale 2',coeff, res['value']['price_unit'],   res['value']  
       return res

    def onchange_price_unit(self, cr, uid, ids, field_name,qty, price_pu, price_unit_id):
        if  price_pu and  price_unit_id and qty:
            coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
            price = price_pu / float(coeff) #* qty
            return {'value': {field_name : price}}
        return {}

sale_order_line()

class sale_order(osv.osv):
    _inherit = "sale.order"

    # FIXME define ship line fields like in purchase order
    # should store price_unit_id for sales

    # FIXME define inv line fields like in purhcase order

    def inv_line_create(self, cr, uid, a, ol):
        line = super(purchase_order, self).inv_line_create(cr, uid, a, ol)
        print >> sys.stderr,'po line',line

        price_unit_pu =  ol.price_unit_pu or 0.0
        print >> sys.stderr,'price_unit_pu' ,price_unit_pu
        print >> sys.stderr,'price_unit_id' ,ol.price_unit_id.id
        #FIXME
        line[2]['price_unit_pu'] = price_unit_pu
        line[2]['price_unit_id'] = ol.price_unit_id.id
        #the 2 values have to be written to the line
        #line['value'].update({'price_unit_pu' : price_unit_pu, 'price_unit_id' : ol.price_unit_id.id })
        print >> sys.stderr,'po line after',line
        return line


    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        res = super(sale_order,self)._prepare_order_line_move( cr, uid, order, line, picking_id, date_planned, context)
        res.update({'price_unit_sale_id': line.price_unit_id.id , 'price_unit_sale':line.price_unit_pu , 'price_unit_id': line.product_id.price_unit_id.id})
        return res

sale_order()




