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
from datetime import datetime, date, time

class stock_location_product(osv.osv_memory):
     _inherit = "stock.location.product"

     _columns = {
        'from_date2': fields.datetime('From'),
        'to_date2': fields.datetime('To'),
        'adjust_time' :fields.boolean('Adjust Time',help="Adjusts From to '00:00:00' and To to '23:59:59'")
        }

     _defaults = {
        'adjust_time'     : lambda *a: '1'
		     }

     def action_open_window(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
	res = super(stock_location_product, self).action_open_window(cr, uid, ids, context)

        location_products = self.read(cr, uid, ids, ['from_date','to_date','from_date2', 'to_date2', 'adjust_time'], context)
	from_date1 = location_products[0]['from_date']
	to_date1 = location_products[0]['to_date']
	from_date2 = location_products[0]['from_date2']
	to_date2 = location_products[0]['to_date2']

	if location_products[0]['adjust_time']:
		if from_date1:
			from_date1 = from_date1[0:10]+' 00:00:00'
		if to_date1:
			to_date1 = to_date1[0:10]+' 23:59:59'
		if from_date2:
			from_date2 = from_date2[0:10]+' 00:00:00'
		if to_date2:
			to_date2 = to_date2[0:10]+' 23:59:59'

        res['context']['from_date1']= from_date1
        res['context']['to_date1']= to_date1
        res['context']['from_date2']= from_date2
        res['context']['to_date2']= to_date2
	return res
           
stock_location_product()

