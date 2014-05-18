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
from datetime import datetime, date, time
import logging
import openerp.tools
import pytz

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
        self._logger.debug('FGF stock_location_product ids %s' % ids)
        self._logger.debug('FGF stock_location_product context %s' % context)
        if context is None:
            context = {}
        res = super(stock_location_product, self).action_open_window(cr, uid, ids, context)
        if context.get('open') == 'report':
             mod_obj = self.pool.get('ir.model.data')
             rep_obj = self.pool.get('ir.actions.report.xml')
             res1 = mod_obj.get_object_reference(cr, uid, 'c2c_stock_accounting', 'report_print_computed_product')
             id = res1 and res1[1] or False
             res.update( rep_obj.read(cr, uid, [id], context=context)[0])

        self._logger.debug('FGF stock_location_product res %s' % res)

        location_products = self.read(cr, uid, ids, ['from_date','to_date','from_date2', 'to_date2', 'adjust_time'], context)
        self._logger.debug('FGF stock_location_products  %s' % location_products)
        from_date1 = location_products[0]['from_date']
        to_date1 = location_products[0]['to_date']
        from_date2 = location_products[0]['from_date2']
        to_date2 = location_products[0]['to_date2']


        format = tools.DEFAULT_SERVER_DATETIME_FORMAT
        tz = context['tz']
        date_local = tools.server_to_local_timestamp(date, format, format, tz)

        res['context']['local_from_date1'] = ''
        res['context']['local_to_date1'] = ''
        res['context']['local_from_date2'] = ''
        res['context']['local_to_date2'] = ''

        if from_date1:
             res['context']['local_from_date1'] = tools.server_to_local_timestamp(from_date1, format, format, tz)
        if to_date1:
             res['context']['local_to_date1'] =  tools.server_to_local_timestamp(to_date1, format, format, tz)
        if from_date2:
             res['context']['local_from_date2'] = tools.server_to_local_timestamp(from_date2, format, format, tz)
        if to_date2:
             res['context']['local_to_date2'] =  tools.server_to_local_timestamp(to_date2, format, format, tz)

        res['context']['from_date']= from_date1
        res['context']['to_date']= to_date1
        res['context']['from_date1']= from_date1
        res['context']['to_date1']= to_date1
        res['context']['from_date2']= from_date2
        res['context']['to_date2']= to_date2
        res['context']['location_name']= self.pool.get('stock.location').read(cr, uid, res['context']['location'],['name'])['name']
        #res['context']['cr1'] = cr
        self._logger.debug('FGF stock_location_product res neu %s' % res)
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
         self._logger.debug('FGF report context %s' % context)
         self._logger.debug('FGF report data %s' % data)
         product_obj = self.pool.get('product.product')
         product_ids = product_obj.search(cr, uid, [])
         datas = {
            'ids': product_ids,
            'model': 'ir.ui.menu',
            'form': data
            }
         self._logger.debug('FGF context %s' % context)
         return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.print.computed.product',
            'datas': datas,
            'context' : context
            }

     def  onchange_date(self, cr, uid, ids, field_name, adjust_time, time, date, context=None):
         if adjust_time:
             format = tools.DEFAULT_SERVER_DATETIME_FORMAT
             tz = context['tz']
             date_local = tools.server_to_local_timestamp(date, format, format, tz)
             date_local_new = date_local[0:10]+' '+ time
             server_tz = tools.get_server_timezone()
             if server_tz != 'UTC':
                 raise osv.except_osv(_('Error'), _('Only UTC server time is currently supported'))
             # convet to UTC
             utc = pytz.utc
             local_tz = pytz.timezone(tz)
             fmt = '%Y-%m-%d %H:%M:%S'
             dt = datetime.strptime(date_local_new, fmt)
             local_dt = local_tz.localize(dt) 
             date_r = utc.normalize(local_dt.astimezone(utc)).strftime(fmt)
         else:
             date_r = date
         result = {'value': {
                   field_name : date_r
                            }
                  }
         return result
         

stock_location_product()


