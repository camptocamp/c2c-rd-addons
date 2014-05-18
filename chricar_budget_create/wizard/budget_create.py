# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
import logging

class c2c_budget_create(osv.osv_memory):
    """
    create budget items and lines from previous accounting periods
    """
    _name = "c2c_budget.create"
    _description = "Create Budget Wizard"
    
    _columns = {
        'budget_version_id'  : fields.many2one('c2c_budget.version','Budget Version', required=True),
        'period_from': fields.many2one('account.period', 'Start period', required=True),
        'period_to': fields.many2one('account.period', 'End period', required=True),
        'create_items': fields.boolean('Create Missing Budget Items', help="This will create a budget item structure identical to account structure"),
        'replace_lines': fields.boolean('Replace Existing Budget Lines', help="Only lines created by this wizard will be removed for the selected matching periods"),
        'exclude_product_plan' : fields.boolean('Exclude P&L accounts ', help="Excludes P&L accounts associated with product budget"),
    }
    _defaults = {
        'create_items' : lambda *a: True,
        }

    def replace_lines(self, cr, uid, ids, periods, context=None):
        if not context:
           context={}
        budget_lines_obj = self.pool.get('c2c_budget.line')
        delete_ids = budget_lines_obj.search(cr, uid, [('period_id','in', periods),('period_source_id','!=', False)],  )
        if delete_ids:
            budget_lines_obj.unlink(cr, uid, delete_ids);

    def _product_account_ids(self, cr, uid, budget_id):
        res = []
        return res
        
    def c2c_budget_create(self, cr, uid, ids, context=None):
        if not context:
           context = {}
        _logger = logging.getLogger(__name__)
        
        period_obj = self.pool.get('account.period')
        budget_item_obj = self.pool.get('c2c_budget.item')
        budget_version_obj = self.pool.get('c2c_budget.version')
        budget_lines_obj = self.pool.get('c2c_budget.line')
        if context is None:
            context = {}
        if context.get('currency_id'):
            currency_id = context['currency_id']
        else:
            currency_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.currency_id.id
        data = self.read(cr, uid, ids, [], context=context)[0]
        # first we create the missing budget_items
        if data['create_items']:
            budget_item_obj.budget_item_create(cr, uid, context)
        
        # now we create the new budget item lines
        budget_version_id = data['budget_version_id'][0]
        context['version_id'] = budget_version_id
        context['budget_version_id'] = budget_version_id

        #
        for version in budget_version_obj.browse(cr, uid, [budget_version_id], context):
            start_date = version.budget_id.start_date
            end_date = version.budget_id.end_date
            company_id = version.company_id.id
        _logger.debug('FGF version date %s %s' % (start_date,end_date))
        _logger.debug('FGF version context %s' % (context))
        periods_new = period_obj.search(cr, uid, [('company_id','=',company_id), ('date_start','>=',start_date), ('date_stop','<=',end_date)])
        if not isinstance(periods_new, list):
            periods_new = [periods_new]
        _logger.debug('FGF periods_new %s' % (periods_new))
        periods = []
        if data['period_from'] and data['period_to']:
            periods = period_obj.build_ctx_periods(cr, uid, data['period_from'][0], data['period_to'][0])
        if not isinstance(periods, list):
            periods = [periods]

            
        if periods:
            _logger.debug('FGF periods %s' % (periods))

            cr.execute("""select p.id ,pn.id 
                            from account_period p,
                                 account_period pn
                           where p.id in (%s)
                             and pn.id in (%s)
                             and to_char(p.date_start,'MM') = to_char(pn.date_start,'MM')
                           """ % (','.join(map(str,periods)) , ','.join(map(str,periods_new))))
            period_map_list = cr.fetchall()
            period_map = dict(period_map_list)
            _logger.debug('FGF period_map %s' % (period_map))
            periods_new2 = []
            for p in period_map_list:
                periods_new2.append(p[1])
            _logger.debug('FGF period_new2 %s' % (periods_new2))
            #
            if data['replace_lines']:
                self.replace_lines(cr, uid, ids, periods_new2, context)
                
            val = {'budget_version_id': data['budget_version_id'][0],
                   'currency_id' : currency_id,
                   'name' : _('Sum Prev Period'),
                   }
            vals =[]
            
            account_ids = self._product_account_ids(cr, uid, budget_version_id)

            cr.execute("""
select -sum(l.debit-l.credit) as amount, l.analytic_account_id, budget_item_id, l.period_id as period_source_id
  from account_move_line l,
       c2c_budget_item_account_rel r,
       c2c_budget_item i
where l.period_id in (%s)
  and r.account_id = l.account_id
  and r.budget_item_id = i.id
  and l.company_id = %s
  and l.account_id not in %s
group by l.analytic_account_id, budget_item_id, l.period_id""" % (','.join(map(str,periods)), company_id, tuple(account_ids)))
            
            for line in cr.dictfetchall():
                _logger.debug('FGF line %s' % ( line))
                val.update(line)
                val['period_id'] =  period_map[line['period_source_id']]
                vals.append(val)
                _logger.debug('FGF budget line %s' % (val))
                budget_lines_obj.create(cr, uid, val)
            #_logger.debug('FGF line vals %s' % (vals))
            #if vals:
            #    budget_lines_obj.create(cr, uid, vals)
        return True
                 
c2c_budget_create()
       
