#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-10-17 12:10:57+02
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from time import mktime
from datetime import datetime
import time
from osv import fields,osv
import pooler
import logging

class chricar_account_move_import_deny(osv.osv):
     _name = "chricar.account_move_import_deny"

     _columns = {
       'company_id'         : fields.many2one('res.company', 'Company'),
       'name'               : fields.char    ('Voucher', size=16, required=True),
       'code'               : fields.char    ('Code', size=8),
       'date_start'         : fields.date    ('Date Start'),
       'date_stop'          : fields.date    ('Date Stop'),
}
     _defaults = {
}
     _order = "code"
chricar_account_move_import_deny()

class chricar_account_tax_code_deloitte(osv.osv):
     _name = "chricar.account_tax_code_deloitte"

     _columns = {
       'company_id'         : fields.many2one('res.company', 'Company'),
       'name'               : fields.char    ('Tax Name', size=32, required=True),
       'code'               : fields.char    ('Code', size=8, required=True),
       'account_id'         : fields.many2one('account.account','Tax Account',required=True),
       'percent'            : fields.float   ('Percent', digits=(8,4), required=True, help=""),
}
     _order = "code"
chricar_account_tax_code_deloitte()

class chricar_account_opening_deloitte(osv.osv):
     _name = "chricar.account_opening_deloitte"

     _columns = {
       'company_id'         : fields.many2one('res.company', 'Company'),
       'account'            : fields.char    ('Account', size=8, required=True),
       'amount'             : fields.float   ('Amount', required=True, digits=(16,2)),
       'name'               : fields.char    ('Account Name', size=64, required=True),
       'date'               : fields.char    ('Date', size=16, required=True),
}
     _order = "account"

chricar_account_opening_deloitte()


class chricar_account_move_line_deloitte(osv.osv):
     _name = "chricar.account_move_line_deloitte"

     def _analytic_account_id(self, cr, uid, ids, name, arg, context):
         result = {}
         for move in self.browse(cr, uid, ids):
             result[move.id] = False
             if move.analytic_account and move.company_id:
                 account_ids= self.pool.get('account.analytic.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',move.analytic_account)])
                 if len(account_ids):
                     result[move.id] = account_ids[0]
         return result

     def _account_id(self, cr, uid, ids, name, arg, context):
         result = {}
         for move in self.browse(cr, uid, ids):
             result[move.id] = False
             if move.account and move.company_id:
                 if len(move.account) == 4:
                     acc = move.account
                 else:
                     acc = move.account[:2]+'00'
                 account_ids= self.pool.get('account.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',acc)])
                 if len(account_ids):
                     result[move.id] = account_ids[0]
         return result

     def _counter_account_id(self, cr, uid, ids, name, arg, context):
         result = {}
         for move in self.browse(cr, uid, ids):
             result[move.id] = False
             if move.counter_account and move.company_id:
                 if len(move.counter_account) == 4:
                     acc = move.counter_account
                 else:
                     acc = move.counter_account[:2]+'00'
                 account_ids= self.pool.get('account.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',acc)])
                 if len(account_ids):
                     result[move.id] = account_ids[0]
         return result

     
     def _period_id(self, cr, uid, ids, name, arg, context):
         result = {}
         for move in self.browse(cr, uid, ids):
             date = False
             try:
                 date = time.strptime(move.date,'%d.%m.%y')
             except:
                 try:
                    date = time.strptime(move.date,'%d/%m/%y')
                 except:
                    try:
                       date = time.strptime(move.date,'%d-%m-%y')
                    except:
                       continue
             date = datetime.fromtimestamp(mktime(date))
             if date: 
                 period_ids= self.pool.get('account.period').search(cr,uid,[('company_id','=',move.company_id.id),('date_start','<=',date),('date_stop','>=',date )])

             if len(period_ids):
                 result[move.id] = period_ids[0]

         return result

     _columns = {
       'company_id'         : fields.many2one('res.company', 'Company'),
       'account'            : fields.char    ('Account Deloitte', size=8, required=True),
       'account_id'         : fields.function(_account_id, method=True, string="Account",type='many2one', relation='account.account',  select="1", store=True ),
       'account_type_name'  : fields.related ('account_id', 'user_type', string="Account Type",type='many2one', relation='account.account.type',  select="1", store=True ),
       'amount'             : fields.float   ('Amount', required=True, digits=(16,2)),
       'analytic_account'   : fields.char    ('Analytic Account Deloitte', size=8),
       'analytic_account_id': fields.function(_analytic_account_id, method=True, string="Analytic Account",type='many2one', relation='account.analytic.account',  select="1", store=True ),

       'ba'                 : fields.char    ('BA', size=8),
       'bc'                 : fields.char    ('BC', size=8),
       'counter_account'    : fields.char    ('Counter Account Deloitte', size=8),
       'counter_account_id' : fields.function(_counter_account_id, method=True, string="Counter Account",type='many2one', relation='account.account',  select="1", store=True ),
       'date'               : fields.char    ('Date', size=16, required=True),
       'period_id'          : fields.function(_period_id, method=True, string="Period",type='many2one', relation='account.period', store=True, select="1",  ),
       'fiscalyear_id'      : fields.related ('period_id', 'fiscalyear_id', string='Fiscal Year', type='many2one', relation='account.fiscalyear', store=True),
       'description'        : fields.char    ('text', size=128),
       'fix'                : fields.char    ('Fix', size=8),
       'fnr'                : fields.char    ('FNR', size=8),
       'lc'                 : fields.char    ('LC', size=8),
       'name'               : fields.char    ('Voucher', size=16, required=True),
       'symbol'             : fields.char    ('Symbol', size=8),
       'tax_code'           : fields.char    ('Tax Code', size=8),
       'state'              : fields.selection([('draft','Draft'), ('progress','Progress'), ('done','Done')], 'State', required=True,)
}
     _defaults = {
       'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'state' : 'draft',
}
     _order = "name"

     def autodetect(self, cr, uid, ids, context=None):
         _logger = logging.getLogger(__name__)
         if not context:
            context = {}
         account_obj = self.pool.get('account.account')
         analytic_obj = self.pool.get('account.analytic.account')
         analytic_line_obj = self.pool.get('account.analytic.line')
         analytic_jour_obj = self.pool.get('account.analytic.journal')
         move_obj = self.pool.get('account.move')
         move_line_obj = self.pool.get('account.move.line')
         analytic_line_obj = self.pool.get('account.analytic.line')
         period_obj = self.pool.get('account.period')
         journal_obj = self.pool.get('account.journal')
         top_obj = self.pool.get('chricar.top')
         location_obj = self.pool.get('stock.location')
         now =  time.strftime("%Y%m%d%H%M%S")

         if context.get('company_id'):
              company_id = context.get('company_id')
         else:
              company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
              context['company_id'] = company_id

         acc_deloitte_ids = self.search(cr, uid, [('company_id','=',company_id),('state','not in',('progress','done'))])
         if not acc_deloitte_ids:
             return True
         self.write(cr, uid, acc_deloitte_ids, {'state': 'progress'} )
         acc_ids = account_obj.search(cr, uid, [('company_id','=',company_id)])
         _logger.info('FGF account ids %s' % (acc_ids))
         acc_codes = []
         for acc in  account_obj.browse(cr, uid, acc_ids, context=None):
             if acc.code not in acc_codes:
                 acc_codes.append(acc.code)
         #_logger.info('FGF account names %s' % (acc_codes))

         _logger.info('FGF account deloitte ids %s' % (acc_deloitte_ids))
         acc_deloitte_codes = []
         for deloitte_acc in  self.browse(cr, uid, acc_deloitte_ids, context=None):
	     if deloitte_acc.account[:2] not in ['23','33'] \
			     and deloitte_acc.account not in acc_codes \
			     and deloitte_acc.account not in acc_deloitte_codes:
                 acc_deloitte_codes.append(deloitte_acc.account)
         _logger.info('FGF missing acc_deloitte_codes %s' % (acc_deloitte_codes))
         
         counter= 0
         user_type = self.pool.get('account.account.type').search(cr, uid, [('code','=','view')])[0]
         parent_id = account_obj.search(cr, uid, [('parent_id','=',False)])[0]
         for acc_deloitte_code in acc_deloitte_codes:
                 counter += 1
                 vals = {
                   'code' : acc_deloitte_code,
                   'name' : 'i-'+now+'-'+str(counter),
                   'type' : 'other',
                   'user_type' : user_type,
                   'currency_mode' : 'current',
                   'parent_id' : parent_id,
                 }
                 _logger.info('FGF new account %s' % (vals))
                 account_obj.create(cr, uid, vals, context)

         # create missing analytic accounts
         aacc_ids = analytic_obj.search(cr, uid, [('company_id','=',company_id)])
         aacc_codes = []
         for aacc in  analytic_obj.browse(cr, uid, aacc_ids, context=None):
             if aacc.code:
                  aacc_codes.append(aacc.code)

         aacc_deloitte_ids = self.search(cr, uid, [('company_id','=',company_id)])
         aacc_deloitte_codes = []
         for deloitte_aacc in  self.browse(cr, uid, aacc_deloitte_ids, context=None):
             if deloitte_aacc.analytic_account \
			     and deloitte_aacc.analytic_account not in aacc_deloitte_codes \
			     and deloitte_aacc.analytic_account not in aacc_codes:
                  aacc_deloitte_codes.append(deloitte_aacc.analytic_account)

         counter= 0

         _logger.info('FGF aacc_codes %s' % (aacc_codes))
         _logger.info('FGF missing aacc_deloitte_codes %s' % (aacc_deloitte_codes))
         for aacc_deloitte_code in aacc_deloitte_codes:
                 counter += 1
                 val = {
                   'code' : aacc_deloitte_code,
                   'name' : 'i-'+now+'-'+str(counter),
                 }
                 analytic_obj.create(cr, uid, val)
                 _logger.info('FGF create aacc_deloitte_codes %s' % (val))

         # update deloitte moves
         for deloitte_move in self.browse(cr, uid, acc_deloitte_ids, context=context):
              vals = {}
	      if not deloitte_move.account_id and deloitte_move.account[:2] not in ['23','33']:
                   vals['account_id'] =  account_obj.search(cr, uid, [('code','=', deloitte_move.account)])
              if deloitte_move.analytic_account and not deloitte_move.analytic_account_id:
                   vals['analytic_account_id'] =  analytic_obj.search(cr, uid, [('code','=', deloitte_move.analytic_account)])
              if vals:
                  _logger.info('FGF create aacc_deloitte_codes %s' % (vals))
                  self.write(cr, uid, deloitte_move.id, vals ,context)
         return True

     def create_move(self, cr, uid, line, vals, context ):
         _logger = logging.getLogger(__name__)
         account_obj = self.pool.get('account.account')
         move_line_obj = self.pool.get('account.move.line')
         analytic_line_obj = self.pool.get('account.analytic.line')
         l = line
         l['journal_id'] = vals['journal_id']
         l['state'] = 'draft'
         l['date'] = vals['date']
         l['period_id'] = vals['period_id']
         l['move_id'] = context['move_id']
         analytic_usage = ''
         #_logger.info('FGF move_line = %s' % (l))
         for acc in account_obj.browse(cr, uid, [line['account_id']], context):
                 analytic_usage =  acc.account_analytic_usage
                 if analytic_usage == 'none':
                     l['analytic_account_id'] = ''
                 #_logger.info('FGF move_line = %s' % (l))
                 move_line_id = move_line_obj.create(cr, uid, l)

                 if l['analytic_account_id']:
                    l['general_account_id'] = line['account_id']
                    l['account_id'] = line['analytic_account_id']
                    l['journal_id'] = context['journal_analyitc_id']
                    l['ref'] = line['name']
                    l['move_id'] = move_line_id
                    if l['debit'] > 0.0 :
                       l['amount'] = -l['debit']
                    else:
                       l['amount'] = l['credit']
                    #_logger.info('FGF move_analyitc line = %s' % (l))
                    analytic_line_obj.create(cr, uid, l)




     def transfer_deloitte_moves(self, cr, uid, ids, context=None):
         _logger = logging.getLogger(__name__)
         if not context:
            context = {}
         account_obj = self.pool.get('account.account')
         analytic_obj = self.pool.get('account.analytic.account')
         analytic_line_obj = self.pool.get('account.analytic.line')
         analytic_jour_obj = self.pool.get('account.analytic.journal')
         move_obj = self.pool.get('account.move')
         move_line_obj = self.pool.get('account.move.line')
         analytic_line_obj = self.pool.get('account.analytic.line')
         period_obj = self.pool.get('account.period')
         journal_obj = self.pool.get('account.journal')
         top_obj = self.pool.get('chricar.top')
         location_obj = self.pool.get('stock.location')
         
         if context.get('company_id'):
              company_id = context.get('company_id')
         else:
              company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
              context['company_id'] = company_id

         acc_deloitte_ids = self.search(cr, uid, [('company_id','=',company_id),('state','=','progress')])
         if not acc_deloitte_ids:
             return True

         journal_id = journal_obj.search(cr, uid, [('code','=','DE')], context=context)[0]
         journal_analyitc_id = analytic_jour_obj.search(cr, uid, [('code','=','Deloitte')], context=context)[0]
         context['journal_analyitc_id'] = journal_analyitc_id
 
         cr.execute("""select distinct company_id, period_id, symbol||'-'||name||'-D' as name, date
                  from chricar_account_move_line_deloitte
                 where id in (%s)""" % (','.join(map(str,acc_deloitte_ids)) ))
         for move in cr.dictfetchall():
             vals = move
             d =  datetime.strptime(move['date'],"%d.%m.%y")
             date = d.strftime('%Y-%m-%d') 
             vals.update({
                'journal_id' : journal_id,
                'state'      : 'draft',
                'date'       : date
             })
             #_logger.info('FGF move vals %s' % (vals))
             move_id = move_obj.create(cr, uid, vals, {} )
             context['move_id'] = move_id 
             #_logger.info('FGF move_id = %s' % (move_id))
             # FGF 20120304 - this code is copied from a 2 years old working sql procedure !
             # writing in python from scratch would look much different
             cr.execute("""
select d.account_id,date, d.description as name, d.analytic_account_id,
       case when d.amount > 0 then d.amount else 0 end as debit,
       case when d.amount < 0 then -d.amount else 0 end as credit,
       'valid' as state 
  from chricar_account_move_line_deloitte d,
       account_account ac,
       account_account_type at
 where 
   ac.id = d.account_id
   and at.id = ac.user_type
   and d.company_id = %s
   and d.period_id = %s
   and symbol||'-'||d.name||'-D' = '%s'
   and (at.close_method != 'none' or tax_code is null)
union all
-- tax code account - net
select d.account_id,date, d.description as name, d.analytic_account_id,
       case when d.amount > 0 then round( d.amount / (1+tc.percent),2) else 0 end as debit,
       case when d.amount < 0 then round(-d.amount / (1+tc.percent),2) else 0 end as credit,
       'valid' as state
  from chricar_account_move_line_deloitte d,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where 
   ac.id = d.account_id
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and d.company_id = %s
   and d.period_id = %s
   and symbol||'-'||d.name||'-D' = '%s'
union all
-- tax code account - tax - avoid rounding differnces !!!
select tc.account_id,date, d.description as name, d.analytic_account_id,
       case when d.amount > 0 then  d.amount - round( d.amount / (1+tc.percent),2) else 0 end as debit,
       case when d.amount < 0 then -d.amount - round(-d.amount / (1+tc.percent),2) else 0 end as credit,
       'valid' as state
  from chricar_account_move_line_deloitte d,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where 
   ac.id = d.account_id
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and percent > 0
   and d.company_id = %s
   and d.period_id = %s
   and symbol||'-'||d.name||'-D' = '%s'

union all
-- counter account
-- no tax code account 
select d.counter_account_id,date, d.description as name, d.analytic_account_id,
       case when d.amount < 0 then -d.amount else 0 end as debit,
       case when d.amount > 0 then  d.amount else 0 end as credit,
       'valid' as state
  from chricar_account_move_line_deloitte d,
       account_account ac,
       account_account_type at
 where 
   ac.id = d.counter_account_id
   and at.id = ac.user_type
   and (at.close_method != 'none' or tax_code is null)
   and d.company_id = %s
   and d.period_id = %s
   and symbol||'-'||d.name||'-D' = '%s'
union all
-- tax code account - net
select d.counter_account_id,date, d.description as name, d.analytic_account_id,
       case when d.amount < 0 then round(-d.amount / (1+tc.percent),2) else 0 end as debit,
       case when d.amount > 0 then round( d.amount / (1+tc.percent),2) else 0 end as credit,
       'valid' as state
  from chricar_account_move_line_deloitte d,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where 
   ac.id = d.counter_account_id
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and d.company_id = %s
   and d.period_id = %s
   and symbol||'-'||d.name||'-D' = '%s'
union all
-- tax code account - tax - avoid rounding differnces !!!
select tc.account_id,date, d.description as name, d.analytic_account_id,
       case when d.amount < 0 then -d.amount - round(-d.amount / (1+tc.percent),2) else 0 end as debit,
       case when d.amount > 0 then  d.amount - round( d.amount / (1+tc.percent),2) else 0 end as credit,
       'valid' as state
  from chricar_account_move_line_deloitte d,
       account_account ac,
       account_account_type at,
       chricar_account_tax_code_deloitte tc
 where 
   ac.id = d.counter_account_id
   and tc.code = d.tax_code
   and at.id = ac.user_type
   and at.close_method = 'none'
   and percent > 0
   and d.company_id = %s
   and d.period_id = %s
   and symbol||'-'||d.name||'-D' = '%s' 
            """ % ( 
vals['company_id'], vals['period_id'], vals['name'], \
vals['company_id'], vals['period_id'], vals['name'], \
vals['company_id'], vals['period_id'], vals['name'], \
vals['company_id'], vals['period_id'], vals['name'], \
vals['company_id'], vals['period_id'], vals['name'], \
vals['company_id'], vals['period_id'], vals['name'], )
)
             for line in cr.dictfetchall():
                 self.create_move(cr, uid, line, vals, context )
        
         journal_id = journal_obj.search(cr, uid, [('code','=','DEN')], context=context)[0]
         journal_analyitc_id = analytic_jour_obj.search(cr, uid, [('code','=','Deloitte')], context=context)[0]
         context['journal_analyitc_id'] = journal_analyitc_id
         period_ids = self.search(cr, uid, [('state', '=', 'progress')])
         ##########################
         #create a move to neutralize the OpenERP move_lines
         ##########################
         cr.execute("""
             select distinct period_id, date_start 
               from chricar_account_move_line_deloitte d,
                    account_period p
              where period_id in (%s)""" % (','.join(map(str,period_ids)) ))
         for move in cr.dictfetchall():
             vals = move
             vals.update({
                'journal_id' : journal_id,
                'state'      : 'draft',
                'name'       : 'neutral',
             })
             #_logger.info('FGF move vals %s' % (vals))
             move_id = move_obj.create(cr, uid, vals,{} )
             context['move_id'] = move_id
             cr.execute("""
select account_id,amn.date,amn.journal_id,amn.id,amn.period_id, analytic_account_id,
   case when sum(case when debit is null then 0 else debit end) > 0 then  sum(case when debit is null then 0 else debit end) else 0 end as cred,
   case when sum(case when debit is null then 0 else debit end) < 0 then -sum(case when debit is null then 0 else debit end) else 0 end as deb,
  'valid'
  from account_move_line aml,
       account_move am,
       account_journal aj,
       account_move amn,  -- neutral move
       account_journal ajn
 where aj.id = am.journal_id
   and aj.name not in ( 'Deloitte')
   and aj.is_opening_balance = False
   and aml.move_id = am.id
   and am.period_id = amn.period_id
   and ajn.name = 'Deloitte neutral'
   and ajn.id = amn.journal_id
   and aml.state='valid'
   and am.period_id = %s
   --and am.state='posted'
 group by account_id,amn.date,amn.journal_id,amn.id,amn.period_id,analytic_account_id
 having sum(case when debit is null then 0 else debit end) != 0
union all
select aml.account_id, analytic_account_id,
   case when sum(case when credit is null then 0 else credit end) < 0 then -sum(case when credit is null then 0 else credit end) else 0 end as credit,
   case when sum(case when credit is null then 0 else credit end) > 0 then  sum(case when credit is null then 0 else credit end) else 0 end as debit
  from account_move_line aml,
       account_move am,
       account_journal aj 
 where aj.id = am.journal_id
   and aj.code != 'DE'
   and aj.is_opening_balance = False
   and aml.move_id = am.id
   and aml.state='valid'
   and am.period_id = %s
   --and am.state='posted'
 group by account_id,amn.date,amn.journal_id,amn.id,amn.period_id,analytic_account_id
having sum(case when credit is null then 0 else credit end) != 0
""" % (move['period_id'],move['period_id']))
        
             for line in cr.dictfetchall():
                 self.create_move(cr, uid, line, vals, context )
         
         self.write(cr, uid, acc_deloitte_ids, {'state': 'done'} )

         return True

chricar_account_move_line_deloitte()

