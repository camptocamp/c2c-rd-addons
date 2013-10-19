# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2004-2013 Camptocamp Austria (<http://camptocamp.com>).
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

import decimal_precision as dp


class res_company(osv.osv):
    _inherit  = "res.company"
    
    def _get_amount_budget(self, cr, uid, ids, field_name, arg, context=None):
        result = {}

        for comp in self.browse(cr, uid, ids, context):
            amount_tot = 0
            for proj in  comp.company_project_ids:
                if proj.amount_budget:
                    amount_tot += proj.amount_budget
            result[comp.id] = amount_tot
        return result
     
    _columns = {
         'company_project_ids' : fields.one2many('project.project', 'company_id', 'Projects', readonly=True),
         'amount_budget' : fields.function(_get_amount_budget, digits_compute=dp.get_precision('Account'), method=True, string="Amount Budget", type='float')
      }
     
res_company()

class project(osv.osv):
    _inherit = "project.project"

    def _get_amount_budget(self, cr, uid, ids, field_name, arg, context=None):
         result = {}

         for project in self.browse(cr, uid, ids, context):
             amount_tot = 0
             for task in  project.tasks:
                 if task.amount_budget:
                    amount_tot += task.amount_budget
             result[project.id] = amount_tot
         return result
   
    _columns = {
         'amount_budget' : fields.function(_get_amount_budget, digits_compute=dp.get_precision('Account'), method=True, string="Amount Budget", type='float'),
         'location_id'   : fields.many2one('stock.location','Object', select=True)
      }

project()


class project_task(osv.osv):
    _inherit = "project.task"
   
    _columns = {
        'amount_budget'    : fields.float("Amount Budget", digits_compute=dp.get_precision('Account'), help="Budgeted amount, must be classified according to accounting and tax rules using the attributes below"),
        'payment_term_id'  : fields.many2one('account.payment.term','Payment Term', help="The payment terms are used to create budget payment lines"),                                    
        'account_id'       : fields.many2one('account.account', 'Expense Account', help="Financial account (expense, depreciation), which defines budget item"),
#       'account_asset_id' : fields.many2one('account.account', 'Asset Account', help="Financial account for assets (only), which defines budget item"),
        'years'            : fields.integer ('Year(s)', help="1 for immediate exepense according to payment terms, 2-n for depreciation"),
        'years_tax'        : fields.integer ('Tax Year(s)', help="1 for immediate exepense according to payment terms, 2-n for equaly split over multiple years"),
      }
    
    def budget_lines(self, cr, uid, task_ids, context) :
        res = {}
        # delete existing
        # insert new
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(project_task, self).write(cr, uid, ids, vals, context=context)
        lines = self.budget_lines(cr, uid, ids, context)
        return res
    
    def create(self, cr, uid, vals, context=None): 
        res = super(project_task, self).create(cr, uid, vals, context=context)
        lines = self.budget_lines(cr, uid, [res], context)
        return res
    
project_task()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

