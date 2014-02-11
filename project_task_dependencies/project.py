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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.one2many_sorted as one2many_sorted
import time
from datetime import datetime
from datetime import timedelta
import networkx 
import logging



class project_task(osv.Model):

    _inherit = 'project.task'


    _duration_units= \
        [ ('days',  _('Days'))
        , ('month', _('Month'))
        , ('hours', _('Hours'))
        , ('Minutes', _('Minutes'))
        ]

    def _duration(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}        
        res = {}
        for task in self.browse(cr, uid, ids, context):
            if task.date_start and task.date_end:
                #_logger.debug('FGF date change %s %s' % (date_start, date_end ))
                from_date = datetime.strptime(task.date_start,'%Y-%m-%d %H:%M:%S')
                to_date = datetime.strptime(task.date_end,'%Y-%m-%d %H:%M:%S')
                duration = (to_date - from_date).days
            else:
                duration = ''
            #return {'value': {'duration': duration }}
            res[task.id] = duration
        return res
    
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
        'duration_helper': fields.integer('Duration', help="Input changes Date End (not respecting weekends etc"),
        'duration': fields.function(_duration, type='integer', string="Duration"),
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
        _logger = logging.getLogger(__name__)
        res = {}
        if date_start and date_end:
            _logger.debug('FGF date change %s %s' % (date_start, date_end ))
            from_date = datetime.strptime(date_start,'%Y-%m-%d %H:%M:%S')
            to_date = datetime.strptime(date_end,'%Y-%m-%d %H:%M:%S')
            duration = (to_date - from_date).days
        else:
            duration = ''
        return {'value': {'duration_helper': duration }}
 
    def on_change_duration(self, cr, uid, ids, date_start, duration):
        _logger = logging.getLogger(__name__)
        res = {}
        _logger.debug('FGF duration change %s %s' % (date_start, duration ))
        if date_start and duration:
            from_date = datetime.strptime(date_start,'%Y-%m-%d %H:%M:%S')
            to_date = from_date + timedelta(days=duration)
            date_end = datetime.strftime(to_date,'%Y-%m-%d %H:%M:%S')            
        else:
            date_end = ''
           
        return {'value': {'date_end': date_end}}
    
    def compute_date_compare(self, cr, uid, predecessor, context=None):
        _logger = logging.getLogger(__name__)
        res = ''
        if predecessor.state != 'cancelled':
            _logger.debug('FGF compute date %s,%s,%s' % (predecessor.name, predecessor.date_end, predecessor.date_deadline)   )
            res = predecessor.date_end or predecessor.date_deadline
        elif predecessor.predecessor_ids:
            for p in predecessor.predecessor_ids:
                _logger.debug('FGF compute date next'    )
                res = self.compute_date_compare(cr, uid, p, context)
        else:
            _logger.debug('FGF compute date nothing'    )
            
        return res
            
        
    def compute_earliest_start(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        res = ''
        if not isinstance(ids,list):
            ids = [ids]
        for task in self.browse(cr, uid, ids, context=context):
            _logger.debug('FGF task %s,%s' % (task.id, task.name)   )
            if task.compute_dependency and task.predecessor_ids:
                date_start = ''
                for predecessor in task.predecessor_ids:
                    date_compare = self.compute_date_compare(cr, uid,  predecessor, context)
                    _logger.debug('FGF task date_compare %s' % (date_compare)   )
                    #date_compare = predecessor.date_end or predecessor.date_deadline
                    if date_compare:
                        date_start = max(date_start or date_compare, date_compare)
                        _logger.debug('FGF task start new %s' % (date_start)   )
                        from_date = datetime.strptime(date_start,'%Y-%m-%d %H:%M:%S')
                        to_date = from_date + timedelta(days=(task.duration or task.duration_min or 1) )
                        date_end = datetime.strftime(to_date,'%Y-%m-%d %H:%M:%S')
                        res = (date_start, date_end)
        return res
    
    def compute_earliest_start_successors(self, cr, uid, ids, context=None):   
        if not context:
            context = {}
        _logger = logging.getLogger(__name__)
        res = ''
        _logger.debug('FGF task ids %s' % (ids)   )
        if not isinstance(ids, list):
            ids = [ids]
        for task in self.browse(cr, uid, ids, context=context):
            if task.successor_ids:
                _logger.debug('FGF successors %s' % (task.successor_ids)   )
                for successor in task.successor_ids:
                    _logger.debug('FGF successor %s' % (successor.id)   )
                    if successor.state not in ('done'):
                        dates = self.compute_earliest_start(cr, uid, successor.id, context)
                        if dates:
                            self.write(cr, uid, [successor.id], {'date_start': dates[0], 'date_end': dates[1]})

        return res


    def networkx_test(self, cr, uid, ids, vals, context=None):
        _logger = logging.getLogger(__name__)
        g = networkx.DiGraph()
        for task in self.browse(cr, uid, ids, context=context):
            g.add_nodes(task.id)
            for dep in task.successor_ids:
                g.add_edge(task.id, dep.id)
        _logger.debug('FGF networkx nodes%s' % (g.nodes()))
        _logger.debug('FGF networkx edges%s' % (g.edges()))
        return
                 
    def create(self, cr, uid, vals, context=None) :
        if vals.get('duration') and vals['duration']:
            vals['duration_helper'] = vals['duration']
        res = super(project_task, self).create(cr, uid, vals, context=context)
        self.compute_earliest_start(cr, uid, [res], context=None)
        return res

    def write(self, cr, uid, ids, vals, context=None) :
        _logger = logging.getLogger(__name__)
        if vals.get('duration') and vals['duration']:
            vals['duration_helper'] = vals['duration']
        res = super(project_task, self).write(cr, uid, ids, vals, context=context)
        
        dates = self.compute_earliest_start(cr, uid, ids, context=None)
        if dates and  dates[0] and dates[1]:
            vals['date_start'] = dates[0]
            vals['date_end'] = dates[1]
            #_logger.debug('FGF task write vals %s' % vals)
            res = super(project_task, self).write(cr, uid, ids, vals, context=context)
        
        self.compute_earliest_start_successors(cr, uid, ids, context)
               
        #self.networkx_test(cr, uid, ids, vals, context)
        return res

# end project_task
