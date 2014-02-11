 
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time
from openerp.report import report_sxw
import logging

class report_webkit_html(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_webkit_html, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
        
class budget_item_chart(osv.osv_memory):
    """
    For Chart of Busget Items
    """
    _name = "account.analytic.chart.sum"
    _description = "Account Analytic chart"
    _logger = logging.getLogger(_name)
    _columns = {
        'chart_account_id': fields.many2one('c2c_budget.item', \
                                    'Budget Top Item',  \
                                    domain = [('parent_id','=',False)] ,\
                                    required=True),
        'fiscalyear': fields.many2one('account.fiscalyear', \
                                    'Fiscal year',  \
                                    required=True),
        'period_from': fields.many2one('account.period', 'Start period'),
        'period_to': fields.many2one('account.period', 'End period'),
        'period_budget_from': fields.many2one('account.period', 'Start period budget FY'),
        'period_budget_to': fields.many2one('account.period', 'End period budget FY'),
        'print_all_zero': fields.boolean('Print lines with all zero'),
        'print_chapter' : fields.boolean('Print chapter column'),
        'print_opening_dc' : fields.boolean('Print opening balance, debit and credit columns'),
        'print_views_only' : fields.boolean('Print only accounts of type view'),
        'print_budget_1000' : fields.boolean('Print budget balance in 1000'),
        'calc_sequence' : fields.boolean('Recalculate Budget Item Sequence (Sort by Code)'),
    }
    _defaults = {
       'print_chapter': lambda *a: True,
       'print_opening_dc': lambda *a: True,
       'calc_sequence': lambda *a: True,
        }

    
    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
        res = {}
        res['value'] = {}
        if fiscalyear_id:
            start_period = end_period = False
            #FIXME - check if closing periods are handled correctly
            # FIXME 2 statements because UNION does not guarantee a correct a correct sort of results.
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop
                               ''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]

                res['value'] = {'period_from': start_period, 
                                'period_to'  : end_period,
                                'period_budget_from': start_period, 
                                'period_budget_to'  : end_period, 
                               }
        return res

    def budget_item_chart_open(self, cr, uid, ids, context=None):
        """
        Opens chart of Accounts
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of account chart’s IDs
        @return: dictionary of Open account chart window on given fiscalyear and all Entries or posted entries
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        rep_obj = self.pool.get('ir.actions.report.xml')
        period_obj = self.pool.get('account.period')
        fy_obj = self.pool.get('account.fiscalyear')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        if data['calc_sequence']:
           cr.execute("""
             select  c2c_budget_sequence();
           """)
        self._logger.debug('open `%s` `%s` `%s`', context.get('open'), data['period_from'][0],  data['period_to'][0])
        if context.get('open')  == 'view':
            result = mod_obj.get_object_reference(cr, uid, 'c2c_budget', 'open_budget_items_tree')
            id = result and result[1] or False
            result = act_obj.read(cr, uid, [id], context=context)[0]
        elif context.get('open') == 'report':
            result = mod_obj.get_object_reference(cr, uid, 'c2c_budget_report', 'report_c2c_budget_item_chart')
            id = result and result[1] or False
            result = rep_obj.read(cr, uid, [id], context=context)[0]
            #FIXME 
            # does not open report

        result['periods'] = []
        if data['period_from'] and data['period_to']:
            result['periods'] = period_obj.build_ctx_periods(cr, uid, data['period_from'][0], data['period_to'][0])
            result['context'] = str({'fiscalyear': data['fiscalyear'][0], 'periods': result['periods']  })
        if data['period_budget_from'] and data['period_budget_to']:
            result['periods_budget'] = period_obj.build_ctx_periods(cr, uid, data['period_budget_from'][0], data['period_budget_to'][0])
            if result['periods_budget']:
                result['context'] = str({'fiscalyear': data['fiscalyear'][0], 
                                'chart_account_id' : data['chart_account_id'][0],
                                'periods': result['periods'], 
                                'periods_budget' : result['periods_budget'] ,
                                'print_all_zero'  : data['print_all_zero'],
                                'print_chapter'   : data['print_chapter'],
                                'print_opening_dc': data['print_opening_dc'],
                                'print_views_only': data['print_views_only'],
                                'print_budget_1000'   : data['print_budget_1000'],
                                })

        if data['fiscalyear']:
            result['name'] += ':' + fy_obj.read(cr, uid, [data['fiscalyear'][0]], context=context)[0]['code'] 
        if data['period_from']:
            result['name'] += ' ' + period_obj.read(cr, uid, [data['period_from'][0]], context=context)[0]['code'] 
        if data['period_to']:
            result['name'] += '-' + period_obj.read(cr, uid, [data['period_to'][0]], context=context)[0]['code'] 

        if data['period_budget_from']:
            result['name'] += ' ' + period_obj.read(cr, uid, [data['period_budget_from'][0]], context=context)[0]['code'] 
        if data['period_budget_to']:
            result['name'] += '-' + period_obj.read(cr, uid, [data['period_budget_to'][0]], context=context)[0]['code'] 
        return result

     
    def budget_item_chart_open_window(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'open':'view'})
        return self.budget_item_chart_open( cr, uid, ids, context)

    def budget_item_chart_open_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'open':'report'})
        self._logger.debug('context after `%s`', context)
        res= self.budget_item_chart_open( cr, uid, ids, context)

        data = self.read(cr, uid, ids, [], context=context)[0]
        period_obj = self.pool.get('account.period')
        data.update({'period_from_name' :  period_obj.read(cr, uid, [data['period_from'][0]], context=context)[0]['code']})
        data.update({'period_to_name' :  period_obj.read(cr, uid, [data['period_to'][0]], context=context)[0]['code']})
        data.update({'period_budget_from_name' :  period_obj.read(cr, uid, [data['period_budget_from'][0]], context=context)[0]['code'] or ''})
        data.update({'period_budget_to_name' :  period_obj.read(cr, uid, [data['period_budget_to'][0]], context=context)[0]['code'] or ''})

        if data['period_from'] and data['period_to']:
            periods = period_obj.build_ctx_periods(cr, uid, data['period_from'][0], data['period_to'][0])
            context.update({'fiscalyear': data['fiscalyear'], 'periods': periods  })

        if data['period_budget_from'] and data['period_budget_to']:
            periods_budget = period_obj.build_ctx_periods(cr, uid, data['period_budget_from'][0], data['period_budget_to'][0])
            context.update({'periods_budget': periods_budget  })

        # get ids
        item_obj = self.pool.get('c2c_budget.item')
        item_ids = item_obj._get_children_and_consol(cr, uid, [data['chart_account_id'][0]] , context)
        datas = {
             'ids': item_ids,
             'model': 'ir.ui.menu',
             'form': data
        }
        self._logger.debug('report data `%s`', datas)
       
            #'report_name': 'account_account.tree_sum',
            #'report_name': 'account.account.chart.report',
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report.c2c_budget.item.chart',
            'datas': datas,
            'context' : context
        }

           

budget_item_chart()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
                                   
