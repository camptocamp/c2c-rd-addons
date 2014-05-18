# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.com>).
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

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _logger = logging.getLogger(__name__)

    def action_invoice_create(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).action_invoice_create(cr, uid, ids, context) 
        self._logger.debug('PO inv create ids,res:%s %s', ids, res)

        invoice_ids = res
        if not isinstance(invoice_ids,list):
           invoice_ids = [invoice_ids]
        picking_obj = self.pool.get('stock.picking')
        picking_ids = picking_obj.search(cr, uid, [('purchase_id','in',ids)])
        self._logger.debug('PO inv create picking_ids:%s', picking_ids)
        for picking_id in picking_ids:
            picking_obj.write(cr, uid, picking_id, {'invoice_ids' : [(6,0, invoice_ids )]}, context=context) 
        return res

purchase_order()
