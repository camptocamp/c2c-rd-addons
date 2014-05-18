# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
from openerp.tools.translate import _
import time
import logging


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        _logger = logging.getLogger(__name__)
        
        res = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context)
        prod_obj = self.pool.get('product.product')
        prod_id = res['product_id']
        self._logger.debug('FGF PO prepare line %s %s' % (prod_id, res))
        for prod in  prod_obj.browse(cr, uid, [prod_id] ,context):
            if len(prod.packaging):
                res['product_packaging'] = prod.packaging[0].id
        
        self._logger.debug('FGF PO prepare line `%s`', res)

        
        return res
purchase_order()
    


