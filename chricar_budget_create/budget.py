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
from openerp.osv import fields,osv
#import pooler

import openerp.addons.decimal_precision as dp
import logging

class c2c_budget_line(osv.osv):
    _inherit = "c2c_budget.line"
    _columns = {
        'period_source_id' : fields.many2one('account.period','Source Period', readonly=True ),
        }

c2c_budget_line()

class c2c_budget_item(osv.osv):
    _inherit = "c2c_budget.item"

    def budget_item_views_create(self, cr, uid, parent_ids, context={}):
        _logger = logging.getLogger(__name__)
        account_obj = self.pool.get('account.account')
        budget_item_obj = self.pool.get('c2c_budget.item')
        missing_parent_ids = list(parent_ids)
        _logger.debug('FGF missing parent %s' % (missing_parent_ids))
        for account in account_obj.browse(cr, uid, parent_ids, context=None):
            if account.parent_id and account.parent_id.id not in missing_parent_ids:
                missing_parent_ids.append(account.parent_id.id)
        if missing_parent_ids != parent_ids:
            self.budget_item_views_create(cr, uid, missing_parent_ids, context)
        val= {'active':True,
              'style':'bold',
              'type':'view'}  
        budget_items_missing = []
        budget_view_ids = budget_item_obj.search(cr, uid, [('type','=','view')])
        budget_codes=[]
        for items in budget_item_obj.browse(cr, uid, budget_view_ids, context):
            budget_codes.append(items.code)
        for account in account_obj.browse(cr, uid, missing_parent_ids, context=None):
            if account.code not in budget_codes:
                val1=dict(val)
                val1['code']= account.code
                val1['name']= account.name
                budget_items_missing.append(val1)
                _logger.debug('FGF budget_items missing  %s' % (val1))
                self.create(cr, uid, val1)
 
    def budget_item_parent_rel_create(self, cr, uid, parent_ids, context): 
        _logger = logging.getLogger(__name__)
        budget_item_obj = self.pool.get('c2c_budget.item')
        company_id = context['company_id']
        _logger.debug('FGF parent dict company_id %s' % (company_id))
        cr.execute("""select a.code, p.code
             from account_account a,
                  account_account p
            where p.id = a.parent_id
              and a.company_id = p.company_id
              and a.company_id = %s
           """ % ( company_id))
        parent_dict = dict(cr.fetchall())
        _logger.debug('FGF parent dict %s' % (parent_dict))
        parent_rel = []
        budget_missing_parents_ids = budget_item_obj.search(cr, uid, [('parent_id','=',False)],context=context)
        _logger.debug('FGF missing parent ids %s' % (budget_missing_parents_ids))
        for item in budget_item_obj.browse(cr, uid, budget_missing_parents_ids, context):
            _logger.debug('FGF parent itemcode %s' % (item.code))
            try: 
              #if item.code == parent_dict[item.code]:
                _logger.debug('FGF parent  %s' % (item.code))
                code_parent = parent_dict[item.code]
                budget_item_id = budget_item_obj.search(cr, uid, [('code','=',item.code)],context=context)[0]
                budget_parent_id = budget_item_obj.search(cr, uid, [('code','=',code_parent)],context=context)[0]
                # if a item structure exists we must append the new structure to the existing one
                parent_rel.append((budget_item_id, budget_parent_id))
            except:
                _logger.debug('FGF parent pass %s' % (item.code))
                pass
        parent_rel_done = []
        _logger.debug('FGF parent rel ids %s' % (parent_rel))
        if parent_rel:
          while not parent_rel_done or parent_rel != parent_rel_done :
            for r in parent_rel:
                try: 
                    self.write(cr, uid, r[0],{'parent_id':r[1]})
                    parent_rel_done.append(r)
                except:
                    pass

    def budget_parent(self, cr, uid, context):
        _logger = logging.getLogger(__name__)
        budget_top_id = context['budget_top_id']
        if budget_top_id:   
           missing_top = self.search(cr, uid,[('id','!=', budget_top_id),('parent_id','=',False )],context=context)
           _logger.debug('FGF missing top %s %s' % (budget_top_id, missing_top))
           if missing_top:
               self.write(cr,uid,missing_top,{'parent_id': budget_top_id})

    def budget_item_account_rel(self, cr, uid, context):
        _logger = logging.getLogger(__name__)
        company_id = context['company_id']
        cr.execute(""" select a.id as account_id,b.id budget_item_id 
                         from account_account a,
                              c2c_budget_item b
                        where a.code = b.code
                          and b.type != 'view'
                          and a.company_id = %s
                          and (a.id,b.id) not in (select account_id ,b.id as budget_item_id from c2c_budget_item_account_rel);"""  %(company_id))
        for missing in cr.dictfetchall():
            _logger.debug('FGF missing rel %s' % (missing))
            self.write(cr, uid, [missing['budget_item_id']], {'account' : [(6,0, [missing['account_id']])]}, context )
         
 
    
    def budget_item_create(self, cr, uid, context={}):
        _logger = logging.getLogger(__name__)
        budget_item_obj = self.pool.get('c2c_budget.item')
        budget_top_id = budget_item_obj.search(cr, uid, [('parent_id','=',False)])[0]
        context['budget_top_id'] = budget_top_id
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
              and code not in (select code from c2c_budget_item )""" % (company_id, (','.join(map(str,user_type_ids)))))
        budget_items_missing = []
        parent_ids = []
        #item_dict = cr.dictfetchall()
        val= {'active':True,
              'style':'normal',
              'company_id':company_id,
              'type':'normal'} 
        for budget_item in cr.dictfetchall():
            val1 = dict(val)
            val1['code']= budget_item['code']
            val1['name']= budget_item['name']
            budget_items_missing.append(val1)
            if budget_item['parent_id'] not in parent_ids:
                parent_ids.append(budget_item['parent_id'])
            _logger.debug('FGF items missing %s' % (val1))
            budget_item_obj.create(cr, uid, val1, context)
        # create missing view structure
        context['company_id'] = company_id
        budget_item_obj.budget_item_views_create(cr, uid, parent_ids, context) 
        budget_item_obj.budget_item_parent_rel_create(cr, uid, parent_ids, context) 
        budget_item_obj.budget_item_account_rel(cr, uid, context)
        budget_item_obj.budget_parent(cr, uid, context)

        return 
                

c2c_budget_item()


class c2c_budget_version(osv.osv):
    _inherit = "c2c_budget.version"

    def budget_lines_create(self, cr, uid, version, date, context={}):
       return



c2c_budget_version()
