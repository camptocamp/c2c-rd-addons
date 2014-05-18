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

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def name_get(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        res= super(stock_production_lot, self).name_get(cr, uid, ids, context)
        if not res:
            return []
        _logger.debug('FGF lot res %s' % (res))
        #_logger.debug('FGF lot context %s ' % (context))
        resd = dict(res)
        digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product UoM')
        #_logger.debug('FGF lot d %s ' % (resd))
        res1 =[]
        if context.get('location_id'):
            for lot in self.browse(cr, uid, ids, context):
                qty = lot.stock_available
                _logger.debug('FGF lot res %s %s' % (lot.id, qty))
                name_new = resd[lot.id] + '  [' + str(round(qty,digits)) +' '+ lot.product_id.uom_id.name+']'
                _logger.debug('FGF lot name %s' % (name_new))
                if lot.product_id.packaging:
                    pack_name = []
                    for pack in lot.product_id.packaging:
                        pack_name.append( '['+pack.ul.name + ' ' + _('á') + ' ' + str(pack.qty) +']' )
                    packs = ','.join(pack_name)
                    name_new += packs
                l = (lot.id,name_new)
                res1.append(l)
                _logger.debug('FGF lot res1 %s' % (res1))
        else:
            _logger.debug('FGF lot res else %s' % (res))
            res1 = res
        return res1

stock_production_lot()
