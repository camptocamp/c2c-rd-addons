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
import logging
from openerp.tools.translate import _

class stock_location(osv.osv):
    _inherit = 'stock.location'

    def name_get(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        _logger = logging.getLogger(__name__)
        #_logger.debug('FGF loc ids %s' % (ids))
        res= super(stock_location, self).name_get(cr, uid, ids, context)
        digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product UoM')

        #_logger.debug('FGF loc res %s' % (res))
        #_logger.debug('FGF loc context %s ' % (context))
        resd = dict(res)
        #_logger.debug('FGF loc d %s ' % (resd))
        res1 =[]
        if context.get('product_id'):

            for product in product_obj.browse(cr, uid, [context.get('product_id')]):
                uom_name = ' '+product.uom_id.name
                packs = ''
                if product.packaging:
                    pack_name = []
                    for pack in product.packaging:
                        pack_name.append( '['+pack.ul.name + ' ' + _(u'á') + ' ' + str(pack.qty) +']' )
                    packs = ','.join(pack_name)

            for loc in self.browse(cr, uid, ids, context):
                qty = loc.stock_real
                qty_v = loc.stock_virtual
                qty_str = str(round(qty,digits))
                if qty_v != qty:
                    qty_str += ' / ' + str(round(qty_v,digits))
                name_new = resd[loc.id] + ' [ ' + qty_str + uom_name + ' ]' + packs
                #_logger.debug('FGF loc name %s' % (name_new))

                l = (loc.id,name_new)
                res1.append(l)
                #_logger.debug('FGF loc res1 %s' % (res1))
        else:
            res1 = res
        return res1

stock_location()
