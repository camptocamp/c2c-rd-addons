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
import logging

class stock_location_product(osv.osv_memory):
     _inherit = "stock.location.product"
     _logger = logging.getLogger(__name__)

     _columns = {
        'from_date2': fields.datetime('From'),
        'to_date2': fields.datetime('To'),
        'adjust_time' :fields.boolean('Adjust Time',help="Adjusts From to '00:00:00' and To to '23:59:59'")
        }

     _defaults = {
        'adjust_time'     : lambda *a: '1'
		     }

     def action_open(self, cr, uid, ids, context=None):
        self._logger.info('FGF stock_location_product ids %s' % ids)
        if context is None:
            context = {}
   	res = super(stock_location_product, self).action_open_window(cr, uid, ids, context)
	#if context.get('open')  == 'view':
   	#     res = super(stock_location_product, self).action_open_window(cr, uid, ids, context)
	if context.get('open') == 'report':
             mod_obj = self.pool.get('ir.model.data')
             rep_obj = self.pool.get('ir.actions.report.xml')
             res1 = mod_obj.get_object_reference(cr, uid, 'c2c_stock_accounting', 'report_print_computed_product')
             id = res1 and res1[1] or False
             res.update( rep_obj.read(cr, uid, [id], context=context)[0])

        self._logger.info('FGF stock_location_product res %s' % res)

        location_products = self.read(cr, uid, ids, ['from_date','to_date','from_date2', 'to_date2', 'adjust_time'], context)
        self._logger.info('FGF stock_location_products  %s' % location_products)
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
        if not res.get('context'):
	   res['context'] = {}
        res['context']['from_date']= from_date1
        res['context']['to_date']= to_date1
        res['context']['from_date1']= from_date1
        res['context']['to_date1']= to_date1
        res['context']['from_date2']= from_date2
        res['context']['to_date2']= to_date2
        res['context']['location']= self.pool.get('stock.location').read(cr, uid, res['context']['location'],['name'])['name']
        #self._logger.info('FGF stock_location_product res neu %s' % res)
	return res


     def action_open_window(self, cr, uid, ids, context=None):
	 if context is None: context = {}
         context.update({'open':'view'})
         return self.action_open( cr, uid, ids, context)

           
     def action_open_report(self, cr, uid, ids, context=None):
	 if not context: context = {}
	 data = self.read(cr, uid, ids, [], context=context)[0]
         context.update({'open':'report'})
         res = self.action_open( cr, uid, ids, context)
	 context = res['context']
         self._logger.info('FGF report context %s' % context)
         self._logger.info('FGF report data %s' % data)
	 product_obj = self.pool.get('product.product')
	 product_ids = product_obj.search(cr, uid, [])
	 datas = {
	    'ids': product_ids,
	    'model': 'ir.ui.menu',
            'form': data
	    }
         self._logger.info('FGF context %s' % context)
         return {
	    'type': 'ir.actions.report.xml',
	    'report_name': 'report.print.computed.product',
            'datas': datas,
            'context' : context
	    }


stock_location_product()


