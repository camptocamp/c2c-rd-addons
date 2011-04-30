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
#import decimal_precision as dp

import re  
from tools.translate import _
        
        
#----------------------------------------------------------
#  Product Category
#----------------------------------------------------------

class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
        'allow_negative_stock' : fields.boolean('Allow Negative Stock', help="Allows negative stock quantities per location / lot for this category - use with care !"),
    }
     
product_category()

       
#----------------------------------------------------------
#  Product
#----------------------------------------------------------

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'allow_negative_stock' : fields.boolean('Allow Negative Stock', help="Allows negative stock quantities per location / lot for this category - use with care !"),
    }

product_template()


class stock_move(osv.osv):
    _inherit = 'stock.move'

    # FIXME - check does not raise error
    # allow_negative_stock is defined for product_template
    def _check_allow_negative_stock(self, cr, uid, ids, context=None):
          
        for move in self.browse(cr, uid, ids):
            do_check = True
            if move.product_id.allow_negative_stock or move.product_id.categ_id.allow_negative_stock:
               do_check = False
            if do_check:
	       # name field = product qty
               cr.execute(
               "select sum(name) \
                  from chricar_stock_product_by_location_prodlot \
                 where product_id = %d \
                   and company_id = %d \
                 group by product_id, location_id,prodlot_id \
                having sum(name) < 0" % ( move.product_id.id, move.company_id.id )) 
            if cr.fetchone():
                   return False
        return True
        
    _constraints = [ (_check_allow_negative_stock, 'Error: Negative quantities for location and/or lots are not allowed for this product or product category', ['name']), ]

     
stock_move()
