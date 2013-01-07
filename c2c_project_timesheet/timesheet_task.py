# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-18 23:44:30+02
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
from osv import fields,osv
import logging

class project_work(osv.osv):
    _inherit = "project.task.work"
    _logger = logging.getLogger(__name__)
    
    def _update_project_id(self, cr, uid, ids, context=None):
        task_work_obj = self.pool.get('project.task.work')
        task_work_ids = task_work_obj.search(cr, uid, [('task_id','in',ids)])
        self._logger.debug('update project `%s` `%s`', ids, task_work_ids)
        return task_work_ids

    _columns = {
        #'date': fields.datetime('Date', select="1"),
        #'task_id': fields.many2one('project.task', 'Task', ondelete='cascade', required=True, select="1"),
        #'user_id': fields.many2one('res.users', 'Done by', required=True, select="1"),
        'to_invoice': fields.many2one('hr_timesheet_invoice.factor', 'Type of Invoicing', help="It allows to set the discount while making invoice"),
        'project_id' : fields.related('task_id', 'project_id', type='many2one', relation="project.project", string='Project',
        store = True
        # FIXME activation of this function causes project_id not be stored on normal entry 
        #          store =  { 'project.task' :
        #                   ( _update_project_id, ['project_id'],
        #                    10)}
),
    }

    def onchange_task_id(self, cr, uid, ids, task_id, context=None):
        result = {}
        if task_id:
            task_obj = self.pool.get('project.task')
            for task in task_obj.browse(cr, uid, [task_id]): 
                if task.project_id and task.project_id.to_invoice:
	            return {'value':{'to_invoice': task.project_id.to_invoice.id,}}
        return {'value':{}}

    def _get_product(self, cr, uid, work_id):
        product_id = ''
        for work in self.browse(cr, uid, [work_id] ):
            grid_obj = self.pool.get('analytic.user.funct.grid')

            grid_ids = grid_obj.search(cr, uid, [('user_id','=', work.user_id.id),('account_id','=',work.task_id.project_id.analytic_account_id.id)])
            for grid_line in grid_obj.browse(cr, uid, grid_ids):
                product_id = grid_line.product_id.id

            if not product_id:
                product_ids = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id']).product_id
                if product_ids:
                    product_id = product_id.id
                

        return product_id


    def write(self, cr, uid, ids, vals, context=None):
        obj_timesheet = self.pool.get('hr.analytic.timesheet')
        obj_analytic_line= self.pool.get('account.analytic.line')
        self._logger.debug('FGF vals `%s`',  vals)
        if 'user_id' not in vals:
                vals['user_id'] = uid
        res= super(project_work,self).write(cr, uid, ids, vals, context)
        for work in self.browse(cr, uid, ids, context=context):
            if work.hr_analytic_timesheet_id and work.hr_analytic_timesheet_id.line_id:
                val = {
                   'to_invoice': work.to_invoice.id,
                   'name' : work.task_id.name+': '+ work.name,
                   'account_id' : work.task_id.project_id.analytic_account_id.id,
                   }
                product_id = self._get_product(cr, uid, work.id)
                if product_id:
                    val['product_id'] = product_id
                self._logger.debug('FGF update analytic `%s` `%s`', work.hr_analytic_timesheet_id.line_id.id, val)
                obj_analytic_line.write(cr, uid, [work.hr_analytic_timesheet_id.line_id.id], val)
         
                
        return res

    def create(self, cr, uid, vals, *args, **kwargs):
        res = super(project_work,self).create(cr, uid, vals, *args, **kwargs)
        timeline_id = vals.get('hr_analytic_timesheet_id') and vals['hr_analytic_timesheet_id'] or ''
        if timeline_id:
            obj_timesheet = self.pool.get('hr.analytic.timesheet')
            for work in self.browse(cr, uid, [res] ):
                vals = {}
                if work.to_invoice:
                    vals['to_invoice'] = work.to_invoice.id
                product_id = self._get_product(cr, uid, work.id)
                if product_id:
                    vals['product_id'] = product_id
                obj_timesheet.write(cr, uid, [timeline_id], vals)

        return res

project_work()

#class hr_timesheet_sheet(osv.osv):
#    _name = "hr_timesheet_sheet.sheet"

#    _columns = {
#        'work_ids': fields.one2many('project.task.work', 'hr_timesheet_sheet_id2', 'Work done'),
#    }

#hr_timesheet_sheet()
