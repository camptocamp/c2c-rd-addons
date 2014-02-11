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
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp

class chricar_budget_compare(osv.osv):
     _name = "chricar.budget.compare"
     _auto = False
     _columns = \
         { 'parent_id'    : fields.many2one('c2c_budget.item','Budget Parent Item')
         , 'item_id'      : fields.many2one('c2c_budget.item','Budget Item')
         , 'sequence'     : fields.integer('Sequence')
         , 'type'         : fields.selection
             ([ ('view', 'View')
              , ('normal', 'Normal')
              ]
             , 'Type'
             )
         , 'fiscalyear_id'  : fields.many2one('account.fiscalyear', 'Fiscal Year')
         , 'period_id'      : fields.many2one('account.period', 'Period')
         , 'period_last_id' : fields.many2one('account.period', 'Period')
         , 'period_name_current': fields.char('Period Current', size=64)
         , 'period_name_last'   : fields.char('Period Last', size=64)
         , 'badget_version_name': fields.char('Budget Version', size=64)
         , 'company_id'         : fields.many2one('res.company', 'Company')
         , 'budget_version_id'  : fields.many2one('c2c_budget.version','Budget Version')
         , 'budget_current' :fields.float('Budget Current',digits_compute=dp.get_precision('Account'))
         , 'budget_last'    :fields.float('Budget Last',digits_compute=dp.get_precision('Account'))
         , 'real_current'   :fields.float('Real Current', digits_compute=dp.get_precision('Account'))
         , 'real_last'      :fields.float('Real Last', digits_compute=dp.get_precision('Account'))
         } 

     def init(self, cr):
          cr.execute("""
create or replace view chricar_budget_compare
as
select 2*l.id as id, 
       p.id as parent_id, 
       i.id as item_id, i.sequence as sequence,  i.type,
       pc.fiscalyear_id,
       pc.id as period_id,
       pc.date_start as period_name,
       pl.date_start as period_name_last,
       v.name as badget_version_name,
       v.company_id as company_id,
       l.budget_version_id,
       l.amount as budget_current,
       0 as budget_last,
       0 as real_current,
       0 as real_last
  from 
    c2c_budget_item i,
    c2c_budget_item p,
    c2c_budget_line l,
    c2c_budget_version v,
    account_period pc,
    account_period pl
  where 
    p.id = i.parent_id
    and l.budget_item_id = i.id
    and v.id = l.budget_version_id
    and pc.id = l.period_id
    and pl.date_start = pc.date_start - interval '1 year'
    and pc.company_id = v.company_id  
    and pl.company_id = v.company_id  
  union all
select 2*l.id -1 as id,
       p.id, 
       i.id as item_id, i.sequence,  i.type,
       pc.fiscalyear_id,
       pc.id as period_id,
       pc.date_start as period_name,
       pl.date_start as period_name_last,
       v.name as badget_version_name,
       v.company_id as company_id,
       l.budget_version_id,
       0 as budget_current,
       l.amount as budget_last,
       0 as real_current,
       0 as real_last
  from 
    c2c_budget_item i,
    c2c_budget_item p,
    c2c_budget_line l,
    c2c_budget_version v,
    account_period pc,
    account_period pl
  where 
    p.id = i.parent_id
    and l.budget_item_id = i.id
    and v.id = l.budget_version_id
    and pl.id = l.period_id
    and pl.date_start = pc.date_start - interval '1 year'
    and pc.company_id = v.company_id  
    and pl.company_id = v.company_id  
  union all
select -l.id*2 as id,
       p.id as parent_id, 
       i.id as item_id, i.sequence, i.type,
       pc.fiscalyear_id,
       pc.id as period_id,
       pc.date_start as period_name,
       pl.date_start as period_name_last,
       'real current' as badget_version_name,
       a.company_id as company_id,
       null as budget_version_id,
       0 as budget_current,
       0 as budget_last,
       l.credit - l.debit as real_current,
       0 as real_last
  from 
    c2c_budget_item i,
    c2c_budget_item p,
    account_account a,
    c2c_budget_item_account_rel r,
    account_move_line l,
    account_period pc,
    account_period pl
  where p.id = i.parent_id
    and a.id = r.account_id
    and i.id = r.budget_item_id
    and l.account_id = a.id
    and l.state = 'valid'
    and pc.id = l.period_id
    and pl.date_start = pc.date_start - interval '1 year'
    and pc.company_id = a.company_id  
    and pl.company_id = a.company_id  
  union all
select -l.id*2-1 as id,
       p.id as parent_id, 
       i.id as item_id, i.sequence,  i.type,
       pc.fiscalyear_id,
       pc.id as period_id,
       pc.date_start as period_name,
       pl.date_start as period_name_last,
       'real last' as badget_version_name,
       a.company_id as company_id,
       null as budget_version_id,
       0 as budget_current,
       0 as budget_last,
       0 as real_current,
       l.credit - l.debit as real_last
  from 
    c2c_budget_item i,
    c2c_budget_item p,
    account_account a,
    c2c_budget_item_account_rel r,
    account_move_line l,
    account_period pc,
    account_period pl
  where p.id = i.parent_id
    and a.id = r.account_id
    and i.id = r.budget_item_id
    and l.account_id = a.id
    and l.state = 'valid'
    and pl.id = l.period_id
    and pl.date_start = pc.date_start - interval '1 year'
    and pc.company_id = a.company_id  
    and pl.company_id = a.company_id  ;
    """)

chricar_budget_compare()

class chricar_budget_compare_period(osv.osv):
     _name = "chricar.budget.compare.period"
     _auto = False
     _order = "fiscalyear_id desc,sequence"
     _columns = \
         { 'parent_id'    : fields.many2one('c2c_budget.item','Budget Parent Item')
         , 'item_id'      : fields.many2one('c2c_budget.item','Budget Item')
         , 'sequence'     : fields.integer('Sequence')
         , 'type'         : fields.selection
             ([('view', 'View')
              ,('normal', 'Normal')
              ]
             ,'Type'
             )
         , 'fiscalyear_id'  : fields.many2one('account.fiscalyear', 'Fiscal Year')
         , 'period_id'      : fields.many2one('account.period', 'Period')
         , 'company_id'     : fields.many2one('res.company', 'Company')
         , 'budget_current' :fields.float('Budget Current',digits_compute=dp.get_precision('Account'))
         , 'budget_last'    :fields.float('Budget Last',digits_compute=dp.get_precision('Account'))
         , 'real_current'   :fields.float('Real Current', digits_compute=dp.get_precision('Account'))
         , 'real_last'      :fields.float('Real Last', digits_compute=dp.get_precision('Account'))
         }

     def init(self, cr):
          cr.execute("""
DROP SEQUENCE IF EXISTS chricar_budget_compare_period_id_seq CASCADE;
CREATE SEQUENCE chricar_budget_compare_period_id_seq;
create or replace view chricar_budget_compare_period as
  select 
    nextval('chricar_budget_compare_period_id_seq'::regclass)::int as id,
    parent_id,item_id, sequence, type,
    fiscalyear_id,
    period_id,
    company_id,
    round(sum(budget_current)) as budget_current,
    round(sum(budget_last)) as budget_last,
    round(sum(real_current)) as real_current,
    round(sum(real_last)) as real_last
  from chricar_budget_compare
  group by company_id,parent_id,item_id, sequence, type, period_id, fiscalyear_id;
""")
chricar_budget_compare_period()

class chricar_budget_compare_year(osv.osv):
     _name = "chricar.budget.compare.year"
     _auto = False
     _order = "fiscalyear_id desc,sequence"
     _columns = \
         { 'parent_id'    : fields.many2one('c2c_budget.item','Budget Parent Item')
         , 'item_id'      : fields.many2one('c2c_budget.item','Budget Item')
         , 'sequence'     : fields.integer('Sequence')
         , 'type'         : fields.selection
             ([ ('view', 'View')
              , ('normal', 'Normal')
              ]
             , 'Type'
             )
         , 'fiscalyear_id'  : fields.many2one('account.fiscalyear', 'Fiscal Year')
         , 'company_id'     : fields.many2one('res.company', 'Company')
         , 'budget_current' :fields.float('Budget Current',digits_compute=dp.get_precision('Account'))
         , 'budget_last'    :fields.float('Budget Last',digits_compute=dp.get_precision('Account'))
         , 'real_current'   :fields.float('Real Current', digits_compute=dp.get_precision('Account'))
         , 'real_last'      :fields.float('Real Last', digits_compute=dp.get_precision('Account'))
         }

     def init(self, cr):
          cr.execute("""
DROP SEQUENCE IF EXISTS chricar_budget_compare_year_id_seq CASCADE;
CREATE SEQUENCE chricar_budget_compare_year_id_seq;
create or replace view chricar_budget_compare_year as
  select 
    nextval('chricar_budget_compare_year_id_seq'::regclass)::int as id,
    parent_id,
    item_id, 
    sequence, 
    type,
    fiscalyear_id,
    company_id,
    round(sum(budget_current)) as budget_current,
    round(sum(budget_last)) as budget_last,
    round(sum(real_current)) as real_current,
    round(sum(real_last)) as real_last
  from chricar_budget_compare
  group by company_id,parent_id,item_id, sequence, type,fiscalyear_id;
""")
chricar_budget_compare_year()
