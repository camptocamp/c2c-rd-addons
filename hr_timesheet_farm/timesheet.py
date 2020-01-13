# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
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
from datetime import datetime
import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

import one2many_sorted
import logging


class hr_timesheet_farm_line(osv.osv):
    _name = "hr.timesheet.farm.line"
    _table = "hr_timesheet_farm_line"
    _logger = logging.getLogger(_name)


    def _get_hours_detail(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
          hours = 0
          if line.work_ids:
            for work in line.work_ids:
                hours += work.hours
          res[line.id] = hours
        return res

    def _period_id(self, cr, uid, ids, name, arg, context):
        result = {}
        _logger = logging.getLogger(__name__)
        for line in self.browse(cr, uid, ids):
            date = line.name
            _logger.info('FGF period_id date %s' % (date)) 
            _logger.info('FGF period_id context %s' % (context)) 
            _logger.info('FGF period_id uid %s' % (context['uid'])) 
            uid = context['uid']
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
            context['company_id'] = company_id
            _logger.info('FGF period_id context %s' % (context)) 
            period_obj = self.pool.get('account.period')
            period_ids = period_obj.find(cr, uid, date, context=context)
            period_id = period_ids and period_ids[0] or False
            result[line.id] = period_id
            _logger.info('FGF period_ids result %s' % (result)) 
        return result


    _columns = {
        'user_id'       : fields.many2one('res.users', 'User', required = True),
        'name'          : fields.date   ('Date', help="Date of work", required = True),
        'period_id'     : fields.function(_period_id, method=True, string="Period",type='many2one', relation='account.period', store=True, select="1",  ),
        'fiscalyear_id' : fields.related('period_id', 'fiscalyear_id', string='Fiscal Year', type='many2one', relation='account.fiscalyear', store=True),
        'hours_regular' : fields.float  ('Hours Regular', digits=(4,2)),
        'hours_cleaning': fields.float  ('Hours Cleaning', digits=(4,2)),
        'hours_overtime_25': fields.float  ('Hours Overtime 25%', digits=(4,2)),
        'hours_overtime_50': fields.float  ('Hours Overtime 50%', digits=(4,2)),
        'hours_overtime_100': fields.float  ('Hours Overtime 100%', digits=(4,2)),
        'hours_holiday_work': fields.float  ('Hours Holiday Work', digits=(4,2)),
        'hours_holiday': fields.float  ('Hours Holiday', digits=(4,2)),
        'hours_illnes': fields.float  ('Hours Illness', digits=(4,2)),
        'hours_care': fields.float  ('Hours Care', digits=(4,2)),
        'allowance': fields.float  ('Allowance', digits=(6,2)),
        'bonus': fields.float  ('Bonus', digits=(6,2)),
        'other': fields.float  ('Other', digits=(6,2)),
        'notes': fields.text ('Notes'),
        'work_ids': one2many_sorted.one2many_sorted('hr.timesheet.farm.line.detail', 'line_id', 'Work' , order = 'prodlot_id.name') ,
        'hours_detail': fields.function(_get_hours_detail, method=True, type='float', string='Sum Detail Hours'),
        'company_id': fields.many2one('res.company', 'Company'),
        }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'name': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.timesheet.farm.line', context=c)
  
       }

    _order          = "name desc"    

hr_timesheet_farm_line()

class hr_timesheet_farm_line_detail(osv.osv):
    _name = "hr.timesheet.farm.line.detail"
    _table = "hr_timesheet_farm_line_detail"
    _logger = logging.getLogger(_name)

    _columns = {
        'line_id'     : fields.many2one('hr.timesheet.farm.line', 'Daily work', required = True),
        'date'        : fields.related ('line_id','name',type='date',string='Date',readonly=True, store=True),
        'period_id'   : fields.related ('line_id','period_id',type='many2one',string='Period', relation="account.period", readonly=True, store=True),
        'fiscalyear_id' : fields.related('line_id', 'fiscalyear_id', string='Fiscal Year', type='many2one', relation='account.fiscalyear', readonly=True,store=True),
        'hours'       : fields.float  ('Hours', digits=(4,2), required=True),
        'task_id'     : fields.many2one('project.task', 'Task', ondelete='cascade', required=True),
        'product_categ_id':fields.many2one('product.category', 'Product Category', ),
        'prodlot_id'  : fields.many2one('stock.production.lot', 'Production Lot', help="For all product related work"),
        'location_id' : fields.many2one('stock.location','Location', help="Only necessary if no production lot exists"),
        'resource_tractor_id' : fields.many2one("resource.resource", "Tractor", domain="[('code','ilike','T ') ]"),
        'hours_tractor': fields.float  ('Hours Tractor', digits=(4,2)),
        'resource_machine_id' : fields.many2one("resource.resource", "Machine", domain="[('code','ilike','M ') ]"),
        'hours_machine': fields.float  ('Hours Machine', digits=(4,2)),
        'name'        : fields.text ('Notes'),
        'user_id'     : fields.related('line_id', 'user_id', type='many2one', relation='res.users', string='User', readonly=True, store=True),
        }
    
hr_timesheet_farm_line_detail()
