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
import time
import datetime
from openerp.osv import osv, fields

class project_work(osv.osv):
    _inherit = "project.task.work"

    def create(self, cr, uid, vals, *args, **kwargs):
        res =  super(project_work,self).create(cr, uid, vals, *args, **kwargs)
        
        proj_work_obj = self.browse(cr, uid, [res] , context=False)
        hr_ats_obj = self.pool.get('hr.analytic.timesheet')
        aufg_obj   = self.pool.get('analytic.user.funct.grid') 
        line_obj   = self.pool.get('account.analytic.line')

        for ts in proj_work_obj:
            line_id = ts.hr_analytic_timesheet_id.line_id.id
            user_id = ts.hr_analytic_timesheet_id.line_id.user_id.id
            account_id = ts.hr_analytic_timesheet_id.line_id.account_id.id
            product_id = ts.hr_analytic_timesheet_id.line_id.product_id.id
            p = '' 
            p = aufg_obj.search(cr, uid, [('user_id','=', user_id),('account_id','=',account_id)])
            if p:
               for aufg in aufg_obj.browse(cr, uid, p, context=None):
                  line_obj.write(cr, uid, line_id, {'product_id': aufg.product_id.id,  'amount' : -ts.hours * aufg.product_id.price   }) 

        return res

    def init(self, cr):
          cr.execute("""
update account_analytic_line a set product_id = (select product_id from analytic_user_funct_grid where user_id = a.user_id and account_id = a.account_id)
 where invoice_id is null and to_invoice is not null and product_id is not null
   --and id in (select id from account_analytic_line where invoice_id is null and to_invoice is not null and product_id is not null )
   and account_id in (select account_id from analytic_user_funct_grid);
""")
# FIXME 20140924 - standard_price became function price
#          cr.execute("""
#update account_analytic_line a set amount = (select -a.unit_amount * standard_price from product_product p, product_template t where p.id =  a.product_id and t.id = p.product_tmpl_id)
# where invoice_id is null and to_invoice is not null and product_id is not null and unit_amount is not null
#   --and id in (select id from account_analytic_line where invoice_id is null and to_invoice is not null and product_id is not null )
#   and account_id in (select account_id from analytic_user_funct_grid);
#""")

project_work()
