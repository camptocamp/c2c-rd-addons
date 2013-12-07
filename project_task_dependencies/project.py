# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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
from openerp.tools.translate import _
import one2many_sorted
import time
from datetime import datetime
import logging



class project_task(osv.Model):

    _inherit = 'project.task'


    _duration_units= \
        [ ('days',  _('Days'))
        , ('month', _('Month'))
        , ('hours', _('Hours'))
        , ('Minutes', _('Minutes'))
        ]

    _columns = {
        'predecessor_ids': one2many_sorted.many2many_sorted('project.task',
                                            'task_predecessors_rel',
                                            'task_id', 'predecessor_id',
                                            'Task Predecessor',
                                             order = 'date_start, name' ),
        'successor_ids': one2many_sorted.many2many_sorted('project.task',
                                            'task_predecessors_rel',
                                            'predecessor_id','task_id',
                                            'Task Successor',
                                             order = 'date_start, name' ),
        'duration': fields.integer('Duration',digits=(4)),
        'duration_min': fields.integer('Minimum Duration', digits=(4), help="Minimum duration in duration_unit. If not set it is computed automatically as difference between start and end date"),
        'duration_unit': fields.selection(_duration_units, 'Duration Unit', required=True, help="Currently only days are supported"),
        'compute_dependency': fields.boolean('Compute earliest start date', help="If set we compute the earliest start date of this task and of all marked successors and based on date for start and end or deadline if end not set"),
    }

    _defaults = {
    	'compute_dependency': lambda *a : True,
    	'duration_unit': lambda *a : 'days' 
    }

    def action_close(self, cr, uid, ids, context=None):

        for record in self.browse(cr, uid, ids, context=context):
            for predecessor in record.predecessor_ids:
                if predecessor.state != 'done':
                    raise osv.except_osv(_('Warning!'), _("Please complete  \
                        the predecessor task %s in order to close this tasks." % predecessor.name))

        return super(project_task, self).action_close(cr, uid, ids, context)

    def on_change_date(self, cr, uid, ids, date_start, date_end):
        res = {}
        if date_start and date_end:
            from_date = datetime.strptime(date_start,'%Y-%m-%d %H:%M:%S')
            to_date = datetime.strptime(date_end,'%Y-%m-%d %H:%M:%S')
            duration = (to_date - from_date).days
        else:
            duration = ''
        return {'value': {'duration': duration }}
        
    
    #def compute_duration(self, cr, uid, task_id, context=None):
        #_logger = logging.getLogger(__name__)
        #res = {}
        #for task in self.browse(cr, uid, [task_id], context=context):
            #if not task.duration and (task.date_start and task.date_end):
                #from_date = datetime.strptime(task.date_start,'%Y-%m-%d %H:%M:%S')
                #to_date = datetime.strptime(task.date_end,'%Y-%m-%d %H:%M:%S')
                #diff = to_date - from_date
                #_logger.debug('FGF date diff %s %s %s' % (from_date,to_date,diff.days)   )
                #res = diff.days
                ##self.write(cr, uid, task_id, res)
        #return res 

    def compute_earliest_start(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        res = ''
        if not isinstance(ids,list):
            ids = [ids]
        for task in self.browse(cr, uid, ids, context=context):
            _logger.debug('FGF task %s,%s' % (task.id, task.name)   )
            
            # for this task
            if task.compute_dependency and task.predecessor_ids:
                
                
                date_start = ''
                #_logger.debug('FGF task start %s' % (date_start)   )
                for predecessor in task.predecessor_ids:
                    date_compare = predecessor.date_end or predecessor.date_deadline
                    #if (date_compare and date_compare <> date_start) or date_start == '':
                    if date_compare:
                        date_start = max(date_start or date_compare, date_compare)
                        _logger.debug('FGF task start new %s' % (date_start)   )
                #self.write(cr, uid, task.id, {'date_start': date_start} )
                date_end = date_start + task.duration
                _logger.debug('FGF task write %s %s %s %s' % (task.id, date_start, date_end, task.name)   )
                res = (date_start, date_end)
                
            # for successors
            if task.successor_ids:
                _logger.debug('FGF successors %s' % (task.successor_ids)   )
                for successor in task.successor_ids:
                    _logger.debug('FGF successor %s' % (successor.id)   )
                    if successor.state != 'done':
                        date_start = self.compute_earliest_start(cr, uid, successor.id, context)
                        if date_start:
                            self.write(cr, uid, [successor.id], {'date_start': date_start})
                    
        return res

                 
    def create(self, cr, uid, vals, context=None) :
        res = super(porject_task, self).create(cr, uid, vals, context=context)
        self.compute_earliest_start(cr, uid, [res], context=None)
        return res

    def write(self, cr, uid, ids, vals, context=None) :
        _logger = logging.getLogger(__name__)
        date_start = self.compute_earliest_start(cr, uid, ids, context=None)
        if date_start:
            vals['date_start'] = date_start
        
        res = super(project_task, self).write(cr, uid, ids, vals, context=context)
        
        return res




project_task()
