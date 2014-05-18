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

class product_product(osv.osv):
    _inherit = 'product.product'

    def name_get(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        _logger = logging.getLogger(__name__)
        res= super(product_product, self).name_get(cr, uid, ids, context)
        digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product UoM')

        #_logger.debug('FGF prod res %s' % (res))
        #_logger.debug('FGF prod context %s ' % (context))
        res1 =[]
        if context.get('shop'):
            context['location_id'] = self.pool.get('sale.shop').read(cr, uid, ['location_id'], [context['shop']])
            for r in res:
                for product in self.browse(cr, uid, [r[0]], context):
                    #_logger.debug('FGF prod context %s ' % (context))
                    uom_name = ' '+product.uom_id.name
                    qty = product.qty_available
                    qty_v = product.virtual_available
                    qty_str = str(round(qty,digits))
                    if qty_v != qty:
                        qty_str += ' / ' + str(round(qty_v,digits))
                    name_new = r[1] + ' [ ' + qty_str + uom_name + ' ]'
                    #_logger.debug('FGF prod name %s' % (name_new))
                    if product.packaging:
                        pack_name = []
                        for pack in product.packaging:
                            pack_name.append( '['+pack.ul.name + ' ' + _('á') + ' ' + str(pack.qty) +']' )
                        packs = ','.join(pack_name)
                        name_new += packs
                    l = (r[0],name_new)
                    res1.append(l)
                    #_logger.debug('FGF prod res1 %s' % (res1))
        else:
            res1 = res
        return res1

product_product()
