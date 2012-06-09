# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

from osv import fields, osv
#import logging

class stock_fill_inventory(osv.osv_memory):
    _inherit = "stock.fill.inventory"


    def fill_inventory(self, cr, uid, ids, context=None):    
	if not context:
	    context = {}
	if ids and len(ids):
	    ids_1 = ids[0]

	res = super(stock_fill_inventory, self).fill_inventory(cr, uid, ids, context)


	fill_inventory = self.browse(cr, uid, ids_1, context=context)
	inventory_obj = self.pool.get('stock.inventory')
        inventory_id = context['active_ids'][0]
        inventory_obj.write(cr, uid, inventory_id , {'recursive' : fill_inventory.recursive, 'location_id': fill_inventory.location_id.id})
	
	return res


stock_fill_inventory()
