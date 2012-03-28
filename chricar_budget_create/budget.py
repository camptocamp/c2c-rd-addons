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
import time
from osv import fields,osv
import pooler

import decimal_precision as dp


class c2c_budget_item(osv.osv):
    _inherit = "c2c_budget.item"

    def budget_item_views_create(self, cr, uid, parent_ids, context={}):
        account_obj = self.pool.get('account.account')
        budget_item_obj = self.pool.get('c2c_budget.item')
        missing_parent_ids = list(parent_ids)
        for account in account_obj.browse(cr, uid, parent_ids, context=None):
            if account.parent_id not in missing_parent_ids:
                missing_parent_ids.append(account.parent_id)
        if missing_parent_ids != parent_ids:
            self.budget_item_views_create(cr, uid, missing_parent_ids, context)
        val= {'active':True,
              'style':'bold',
              'type':'view'}  
        budget_items_missing = []
        budget_view_ids = budget_item_obj.seach(cr, uid, [('type','=','view')], context)
        budget_codes=[]
        for itmes in budget_item_obj.brwose(cr, uid, budget_view_ids, context):
            budget_codes.append(items.code)
        for account in account_obj.browse(cr, uid, missing_parent_ids, context=None):
            if account.code not in budget_codes:
                val['code']= account.code
                val['name']= account.name
                budget_items_missing.append(val)
        self.create(cr, uid, val)
 
    def budget_item_parent_rel_create(self, cr, uid, parent_ids, context): 
        budget_item_obj = self.pool.get('c2c_budget.item')
        cr.execute("""select code, parent_code
             from account_account a,
                  account_account p
            where p.id = a.parent_id
           """)
        parent_dict = cr.dictfetchall()
        parent_rel = []
        budget_missing_parents_ids = budget_item_obj.seach(cr, uid, [('parent_id','=',False)], context)
        for item in budget_item_obj.browse(cr, uid, budget_missing_parents_ids, context):
            if item.code == parent_dict.get(item.code):
                code_parent = parent_dict['item.code']
                budget_item_id = budget_item_obj.search(cr, uid, [('code','=',item.code)])
                budget_parent_id = budget_item_obj.search(cr, uid, [('code','=',code_parent)]) 
                parent_rel.append((budget_item_id, budget_parent_id))
        parent_rel_done = []
        while parent_rel != parent_rel_done:
            for r in parent_rel:
                try: 
                    self.write(cr, uid, r[0],{'parent_id':r[1]})
                    parent_rel_done.append(r)
                except:
                    pass
    
    def budget_item_create(self, cr, uid, context={}):
        # will create missing budget items + structure as for accounts
        user_type_ids = self.pool.get('account.account.type').search(cr, uid, [('code','in',['income','expense'])])
        if context.get('company_id'):
            company_id = context['company_id']
        else:
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        cr.execute("""select code,name,parent_id
             from account_account
            where company_id = %s
              and type = 'other'
              and user_type in (%s)
              and code not in (select code from c2c_budget_item)""" % ((','.join(map(str,user_type_ids)))))
        budget_items_missing = []
        parent_ids = []
        item_dict = cr.dictfetchall()
        val= {'active':True,
              'style':'normal',
              'type':'normal'} 
        for budget_item in item_dict:
            val['code']= budget_item.code
            val['name']= budget_item.name
            budget_items_missing.append(val)
            parent_ids.append(budget_item.parent_id)
        self.create(cr, uid, val)
        # create missing view structure
        self.budget_item_views_create(cr, uid, parent_ids, context) 
        self.budget_item_parent_rel_create(cr, uid, parent_ids, context) 

        return 
                

c2c_budget_item()


class c2c_budget_version(osv.osv):
    _inherit = "c2c_budget.version"

    def budget_lines_create(self, cr, uid, version, date, context={}):
       return



c2c_budget_version()
