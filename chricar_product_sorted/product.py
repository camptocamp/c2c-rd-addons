# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-18 23:44:30+02
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
from osv import fields,osv
import pooler

import decimal_precision as dp

from tools.sql import drop_view_if_exists


import sys

class product_product(osv.osv):
    _inherit = "product.product"
    _order = "name_category,name_template,variants"

    def _product_name(self, cr, uid, ids, field_name, arg, context={}):
         result = {}
         for product in self.browse(cr, uid, ids, context=context):
             print >> sys.stderr,'product name',product
             try: 
                 result[product.id] = product.name
             except:
                 print >> sys.stderr,'product name execption'
         return result

    def update_category_name(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        product_ids = product_obj.search(cr, uid, [('categ_id','in',ids)])
        return product_ids

    _columns = {
          'name_template': fields.function(_product_name, method=True, string="Product",type='char', size=128, select="1",
                       store =  { 'product.template' :
                    ( lambda self, cr, uid, ids, context:
                          [f.id for f in self.pool.get('product.template').browse(cr, uid, ids, context)]
                    , None
                    , 10
                    )}
                       ),

          'name_category': fields.related('categ_id', 'name', type="char", size=64, relation="product.category", string="Category",  select="1",
                       store =  { 'product.category' :
                           ( update_category_name, ['name']
                            , 10)}
                    ),
         } 


product_product()
          
