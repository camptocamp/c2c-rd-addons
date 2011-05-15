 
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

from osv import fields, osv

class account_chart_sum(osv.osv_memory):
    """
    For Chart of Accounts
    """
    _name = "account.chart.sum"
    _description = "Account chart (sum)"
    _columns = {
        'fiscalyear': fields.many2one('account.fiscalyear', \
                                    'Fiscal year',  \
                                    required=True),
        'period_from': fields.many2one('account.period', 'Start period'),
        'period_to': fields.many2one('account.period', 'End period'),
        'period_prev_from': fields.many2one('account.period', 'Start period prev FY'),
        'period_prev_to': fields.many2one('account.period', 'End period prev FY'),

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
                res['value'] = {'period_from': start_period, 'period_to': end_period}

            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p,
                                    account_fiscalyear f, 
                                    account_fiscalyear pf 
                               WHERE f.id = %s
                                 AND pf.date_stop = f.date_start -1
                                 AND p.fiscalyear_id = pf.id
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_prev_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p,
                                    account_fiscalyear f, 
                                    account_fiscalyear pf 
                               WHERE f.id = %s
                                 AND pf.date_stop = f.date_start -1
                                 AND p.fiscalyear_id = pf.id
                               ORDER BY p.date_stop desc 
                               LIMIT 1) AS period_prev_start
                               ''', (fiscalyear_id, fiscalyear_id))
            periods_prev =  [i[0] for i in cr.fetchall()]
            if periods_prev and len(periods_prev) > 1:
                start_prev_period = periods_prev[0]
                end_prev_period = periods_prev[1]
                res['value'] = {'period_from': start_period, 'period_to': end_period,'period_prev_from': start_prev_period, 'period_prev_to': end_prev_period}
        return res

    def account_chart_sum_open_window(self, cr, uid, ids, context=None):
        """
        Opens chart of Accounts
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of account chart’s IDs
        @return: dictionary of Open account chart window on given fiscalyear and all Entries or posted entries
        """
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        period_obj = self.pool.get('account.period')
        fy_obj = self.pool.get('account.fiscalyear')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        result = mod_obj.get_object_reference(cr, uid, 'chricar_account_period_sum', 'action_account_chart_sum')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['periods'] = []
        if data['period_from'] and data['period_to']:
            result['periods'] = period_obj.build_ctx_periods(cr, uid, data['period_from'], data['period_to'])
            result['context'] = str({'fiscalyear': data['fiscalyear'], 'periods': result['periods']  })
        if data['period_prev_from'] and data['period_prev_to']:
            result['periods_prev'] = period_obj.build_ctx_periods(cr, uid, data['period_prev_from'], data['period_prev_to'])
            if result['periods_prev']:
                result['context'] = str({'fiscalyear': data['fiscalyear'], 'periods': result['periods'], 'periods_prev' : result['periods_prev']  })
        if data['fiscalyear']:
            result['name'] += ':' + fy_obj.read(cr, uid, [data['fiscalyear']], context=context)[0]['code'] 
        if data['period_from']:
            result['name'] += ' ' + period_obj.read(cr, uid, [data['period_from']], context=context)[0]['code'] 
        if data['period_to']:
            result['name'] += '-' + period_obj.read(cr, uid, [data['period_to']], context=context)[0]['code'] 

        if data['period_prev_from']:
            result['name'] += ' ' + period_obj.read(cr, uid, [data['period_prev_from']], context=context)[0]['code'] 
        if data['period_prev_to']:
            result['name'] += '-' + period_obj.read(cr, uid, [data['period_prev_to']], context=context)[0]['code'] 

        #print >> sys.stderr, 'wiz',result
        return result

account_chart_sum()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
                                   
