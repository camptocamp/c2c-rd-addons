# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
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
from openerp.osv import fields,osv
#import pooler
import logging

class product_product(osv.osv):
    _inherit = "product.product"
    _order = "name_category,default_code,name_template,variants"

    def _update_category_name(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        product_ids = product_obj.search(cr, uid, [('categ_id','in',ids)])
        return product_ids

    _columns = {
          'name_category': fields.related('categ_id', 'name', type="char", size=64, relation="product.category", string="Category",  select="1",
                       #store = True
                       store =  { 
                               'product.product'  : (lambda self, cr, uid, ids, c={}: ids, ['categ_id'], 10),
                               'product.category' : ( _update_category_name, ['name'] , 10)
                               }
                    ),
     }
    # FIXME - not sure if index works if column default_code is empty 
    def init(self, cr):
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = \'name_category_default_code_name_template_variants_index\'')
        if not cr.fetchone():
            cr.execute('CREATE INDEX name_category_default_code_name_template_variants_index ON product_product(name_category,default_code,name_template,variants)')

    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
             context={}
        if not default:
             default = {}
        res = super(product_product, self).copy(cr, uid, id, default=default, context=context)
        _logger  = logging.getLogger(__name__)
        self._logger.debug('FGF id %s, res %s' % (id,res))
        for product in self.browse(cr, uid, [id], context):
            self._logger.debug('FGF categ id %s' % (product.categ_id.id))
            self.write(cr, uid, [res], {'name_category': product.categ_id.name })

        return res

product_product()
          
