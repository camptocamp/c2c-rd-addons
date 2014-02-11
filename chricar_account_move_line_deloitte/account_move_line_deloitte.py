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
from openerp.osv import fields,osv
##import pooler
from openerp.tools.translate import _
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
                 if account_ids:
                     result[move.id] = account_ids[0]
         return result

     def _account_id(self, cr, uid, ids, name, arg, context):
         result = {}
         for move in self.browse(cr, uid, ids):
             result[move.id] = False
             if move.account and move.company_id:
                 #if len(move.account) in [3, 4]:
                 #    acc = move.account
                 #else:
                 #    acc = move.account[:2]+'00'
                 if move.account[:2] in ['23','33']:
                      acc = move.account[:2]+'00'
                 else:
                      acc =  move.account

             account_ids= self.pool.get('account.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',acc),('type','!=','view')])
             if not account_ids and move.counter_account and len(move.counter_account)==3:
                    account_ids= self.pool.get('account.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=','0'+acc),('type','!=','view')])
             if account_ids:
                 result[move.id] = account_ids[0]
         return result

     def _counter_account_id(self, cr, uid, ids, name, arg, context):
         result = {}
         for move in self.browse(cr, uid, ids):
             result[move.id] = False
             if move.counter_account and move.company_id:
                 #if len(move.counter_account) == 4:
                 #    acc = move.counter_account
                 #else:
                 #    acc = move.counter_account[:2]+'00'
                 if move.counter_account[:2] in ['23','33']:
                      acc = move.counter_account[:2]+'00'
                 else:
                      acc =  move.counter_account

                 account_ids= self.pool.get('account.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',acc),('type','!=','view')])
                 if not account_ids and len(move.counter_account)==3:
                    account_ids= self.pool.get('account.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=','0'+acc),('type','!=','view')])

                 if account_ids:
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
       'symbol'             : fields.char    ('Symbol', size=8, select=True),
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
         acc_ids = account_obj.search(cr, uid, [('company_id','=',company_id),('type','!=','view')])
         _logger.debug('FGF account ids %s' % (acc_ids))
         acc_codes = []
         for acc in  account_obj.browse(cr, uid, acc_ids, context=None):
             if acc.code not in acc_codes:
                 acc_codes.append(acc.code)
         #_logger.debug('FGF account names %s' % (acc_codes))

         _logger.debug('FGF account deloitte ids %s' % (acc_deloitte_ids))
         acc_deloitte_codes = []

         for deloitte_acc in  self.browse(cr, uid, acc_deloitte_ids, context=None):
           das = [deloitte_acc.account, deloitte_acc.counter_account]
           _logger.debug('FGF missing das %s' % (das))
           for da in das:
                if da and len(da)<4:
                  da = '0'+da
                _logger.debug('FGF da %s' % (da))
                if da and da[:2] not in ['23','33'] \
                             and da not in acc_codes \
                             and da not in acc_deloitte_codes:
                     acc_deloitte_codes.append(da)
                     _logger.debug('FGF missing da %s %s' % (da, acc_deloitte_codes))
             
         _logger.debug('FGF missing acc_deloitte_codes %s' % (acc_deloitte_codes))
         
         counter= 0
         user_type = self.pool.get('account.account.type').search(cr, uid, [('code','=','view')])[0]
         parent_id = account_obj.search(cr, uid, [('company_id','=',company_id),('parent_id','=',False)])[0]
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
                 _logger.debug('FGF new account %s' % (vals))
                 account_obj.create(cr, uid, vals, context)

         # create missing analytic accounts
         aacc_ids = analytic_obj.search(cr, uid, [('company_id','=',company_id),('company_id','=',company_id)])
         aacc_codes = []
         for aacc in  analytic_obj.browse(cr, uid, aacc_ids, context=None):
             if aacc.code:
                  aacc_codes.append(aacc.code)

         aacc_deloitte_ids = self.search(cr, uid, [('company_id','=',company_id),('company_id','=',company_id)])
         aacc_deloitte_codes = []
         for deloitte_aacc in  self.browse(cr, uid, aacc_deloitte_ids, context=None):
             if deloitte_aacc.analytic_account \
                             and deloitte_aacc.analytic_account not in aacc_deloitte_codes \
                             and deloitte_aacc.analytic_account not in aacc_codes:
                  aacc_deloitte_codes.append(deloitte_aacc.analytic_account)

         counter= 0

         _logger.debug('FGF aacc_codes %s' % (aacc_codes))
         _logger.debug('FGF missing aacc_deloitte_codes %s' % (aacc_deloitte_codes))
         for aacc_deloitte_code in aacc_deloitte_codes:
                 counter += 1
                 val = {
                   'code' : aacc_deloitte_code,
                   'name' : 'i-'+now+'-'+str(counter),
                 }
                 analytic_obj.create(cr, uid, val)
                 _logger.debug('FGF create aacc_deloitte_codes %s' % (val))

         # update deloitte moves
         for deloitte_move in self.browse(cr, uid, acc_deloitte_ids, context=context):
              vals = {}
              if not deloitte_move.account_id and deloitte_move.account[:2] not in ['23','33']:
                   vals['account_id'] =  account_obj.search(cr, uid, [('company_id','=',company_id),('code','=', deloitte_move.account)])
                   if not  vals['account_id'] and len(deloitte_move.account)< 4:
                        vals['account_id'] =  account_obj.search(cr, uid, [('company_id','=',company_id),('code','=', '0'+deloitte_move.account)])
              if deloitte_move.counter_account and not deloitte_move.counter_account_id and deloitte_move.counter_account[:2] not in ['23','33']:
                   vals['counter_account_id'] =  account_obj.search(cr, uid, [('company_id','=',company_id),('code','=', deloitte_move.counter_account)])
                   if not vals['counter_account_id'] and len(deloitte_move.counter_account)<4:
                   #if not vals.get('counter_account_id',False)  and deloitte_move.counter_account and len(deloitte_move.counter_account)<4:
                        vals['counter_account_id'] =  account_obj.search(cr, uid, [('company_id','=',company_id),('code','=', '0'+deloitte_move.counter_account)])
                 
              if deloitte_move.analytic_account and not deloitte_move.analytic_account_id:
                   vals['analytic_account_id'] =  analytic_obj.search(cr, uid, [('company_id','=',company_id),('code','=', deloitte_move.analytic_account)])
              if vals:
                  _logger.debug('FGF create aacc_deloitte_codes %s' % (vals))
                  self.write(cr, uid, deloitte_move.id, vals ,context)
         return True

     def create_move(self, cr, uid, line, vals, context ):
     #def create_move(self, cr, uid, v ):
         _logger = logging.getLogger(__name__)
         account_obj = self.pool.get('account.account')
         move_line_obj = self.pool.get('account.move.line')
         analytic_line_obj = self.pool.get('account.analytic.line')
         l = dict(line)
         l['journal_id'] = vals['journal_id']
         l['state'] = 'draft'
         l['date'] = vals['date']
         l['period_id'] = vals['period_id']
         l['move_id'] = context['move_id']
         analytic_usage = ''
         #_logger.debug('FGF move_line = %s' % (l))
         for acc in account_obj.browse(cr, uid, [line['account_id']], context):
                 analytic_usage =  acc.account_analytic_usage
                 if analytic_usage == 'none':
                     l['analytic_account_id'] = ''
                 #_logger.debug('FGF move_line = %s' % (l))
                 #move_line_id = move_line_obj.create(cr, uid, l, context)
                 #move_line_id = super(account_move_line, self).create(cr, uid, l, context)
                 return (0,0,l)
	         # FIXME - analytic line is created automatically
                 if l.get('analytic_account_id',False):
                    l['general_account_id'] = line['account_id']
                    l['account_id'] = line['analytic_account_id']
                    l['journal_id'] = context['journal_analytic_id']
                    l['ref'] = line['name']
                    l['move_id'] = move_line_id
                    if l['debit'] > 0.0 :
                       l['amount'] = -l['debit']
                    else:
                       l['amount'] = l['credit']
                    #_logger.debug('FGF move_analyitc line = %s' % (l))
                    del l['analytic_account_id']
                    del l['analytic_lines']
                    del l['state']
                    del l['credit']
                    del l['debit']
                    #analytic_line_obj.create(cr, uid, l, context)




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

         journal_id = journal_obj.search(cr, uid, [('company_id','=',company_id),('code','=','DE')], context=context)
         if journal_id: 
                 journal_id = journal_id[0] 
         else:
            raise osv.except_osv(_('Error :'), _('Deloite journal with code DE missing') )

         journaln_id = journal_obj.search(cr, uid, [('company_id','=',company_id),('code','=','DEN')], context=context)
         if journaln_id: 
                 journaln_id = journaln_id[0] 
         else:
            raise osv.except_osv(_('Error :'), _('Deloite neutral journal with code DEN missing') )

         _logger.debug('FGF journal_id  %s' % (journal_id))
         #if not journal_id:
         #    journal_id = journal_obj.create(cr, uid, {'company_id':company_id, 'code':'DE', 'name':'Deloitte', 'type','general'})
         journal_analytic_id = analytic_jour_obj.search(cr, uid, [('company_id','=',company_id),('name','=','Deloitte')], context=context)
         if journal_analytic_id: 
                 journal_analytic_id = journal_analytic_id[0] 
         context['journal_analytic_id'] = journal_analytic_id
 
         to_post = []
         cr.execute("""select  distinct company_id, period_id, coalesce(symbol,'IB')||'-'||coalesce(name,'period_id')||'-D' as name, date
                  from chricar_account_move_line_deloitte
                 where id in (%s)  """ % (','.join(map(str,acc_deloitte_ids)) ))
         period_ids = [] 
         for move in cr.dictfetchall():
             vals = dict(move)
             try:
                d =  datetime.strptime(move['date'],"%d.%m.%y")
             except:
                try:
                   d =  datetime.strptime(move['date'],"%d/%m/%y")
                except:
                   pass
             date = d.strftime('%Y-%m-%d') 
             vals.update({
                'journal_id' : journal_id,
                'state'      : 'draft',
                'date'       : date,
                #'journal_analytic_id': journal_analytic_id,
             })
             #_logger.debug('FGF move vals %s' % (vals))
             c = {}
             c['novalidate'] = True
             # moves_lines from ONE move may have different dates
             _logger.debug('FGF move_id before %s', vals  )
             move_id = move_obj.search(cr,uid, [('company_id','=',vals['company_id']), ('period_id','=',vals['period_id']), ('name','=',vals['name']) ])
             if move_id:
                continue
             else:
                move_id = move_obj.create(cr, uid, vals,  c )
             to_post.append(move_id)
             #move_id = super(account_move, self).create(cr, uid, vals, {} )
             context['move_id'] = move_id 
             vals['move_id'] = move_id 
             _logger.debug('FGF move_id = %s' % (move_id))
             # FGF 20120304 - this code is copied from a 2 years old working sql procedure !
             # writing in python from scratch would look much different
             cr.execute("""
select d.account_id,date, coalesce(d.description, coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')) as name, d.analytic_account_id,
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
   and coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')||'-D' = '%s'
   and (at.close_method != 'none' or tax_code is null)
union all
-- tax code account - net
select d.account_id,date, coalesce(d.description, coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')) as name, d.analytic_account_id,
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
   and tc.company_id = d.company_id
   and at.id = ac.user_type
   and at.close_method = 'none'
   and d.company_id = %s
   and d.period_id = %s
   and coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')||'-D' = '%s'

union all
-- tax code account - tax - avoid rounding differnces !!!
select tc.account_id,date, coalesce(d.description, coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')) as name, d.analytic_account_id,
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
   and tc.company_id = d.company_id
   and at.id = ac.user_type
   and at.close_method = 'none'
   and percent > 0
   and d.company_id = %s
   and d.period_id = %s
   and coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')||'-D' = '%s'


union all
-- counter account
-- no tax code account 
select d.counter_account_id,date, coalesce(d.description, coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')) as name, d.analytic_account_id,
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
   and coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')||'-D' = '%s'

union all
-- tax code account - net
select d.counter_account_id,date, coalesce(d.description, coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')) as name, d.analytic_account_id,
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
   and tc.company_id = d.company_id
   and at.id = ac.user_type
   and at.close_method = 'none'
   and d.company_id = %s
   and d.period_id = %s
   and coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')||'-D' = '%s'

union all
-- tax code account - tax - avoid rounding differnces !!!
select tc.account_id,date, coalesce(d.description, coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')) as name, d.analytic_account_id,
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
   and tc.company_id = d.company_id
   and at.id = ac.user_type
   and at.close_method = 'none'
   and percent > 0
   and d.company_id = %s
   and d.period_id = %s
   and coalesce(symbol,'IB')||'-'||coalesce(d.name,'period_id')||'-D' = '%s'

            """ % ( 
company_id, vals['period_id'], vals['name'], \
company_id, vals['period_id'], vals['name'], \
company_id, vals['period_id'], vals['name'], \
company_id, vals['period_id'], vals['name'], \
company_id, vals['period_id'], vals['name'], \
company_id, vals['period_id'], vals['name'], )
)
             moves= []
             for line in cr.dictfetchall():
                 # FIXME - performance 
                 v = dict(line)
                 _logger.debug('FGF create_move v %s' % (v))
                 v.update(vals)
                 _logger.debug('FGF create_move v %s' % (v))
                 v.update(context)
                 #_logger.debug('FGF create_move v %s' % (v))
                 #_logger.debug('FGF create_move line %s' % (line))
                 #_logger.debug('FGF create_move vals %s' % (vals))
                 #_logger.debug('FGF create_move context %s' % (context))
                 #moves.append( (v))
                 #try:
                     #self.create_move(cr, uid, line, vals, context )
                 #self.create_move(cr, uid, line, v, context )
                 moves.append(self.create_move(cr, uid, line, v, context ))
                 if vals['period_id'] not in period_ids:
                     period_ids.append(vals['period_id'])
                 #except:
                     #raise osv.except_osv(_('Error :'), _('FGF insert deloitte move %s %s') % (line, vals))
                 #    raise osv.except_osv(_('Error :'), _('FGF insert deloitte move %s ') % ( v))

             #_logger.debug('FGF create_move moves %s' % (moves))
             #self.create_move(cr, uid, moves)
             _logger.debug('FGF create_moves %s' % (moves))
             move_obj.write(cr, uid, [move_id], {'line_id': moves},  c )
        
         journal_id = journal_obj.search(cr, uid, [('company_id','=',company_id),('code','=','DEN')], context=context)
         if journal_id:
             journal_id = journal_id[0]
         #journal_analytic_id = analytic_jour_obj.search(cr, uid, [('code','=','Deloitte')], context=context)[0]
         #context['journal_analytic_id'] = journal_analytic_id
         _logger.debug('FGF create_move neutral period_ids %s', period_ids )
         ##########################
         #create a move to neutralize the OpenERP move_lines
         ##########################
         # dirty hack
         if not period_ids:
             period_ids = [0]
         cr.execute("""
             select distinct period_id, date_stop as date
               from chricar_account_move_line_deloitte d,
                    account_period p
              where p.id = d.period_id
                and period_id in (%s)""" % (','.join(map(str,period_ids)) ))
         for move in cr.dictfetchall():
             _logger.debug('FGF create_move neutral move %s', move)
             vals = move
             vals.update({
                'journal_id' : journal_id,
                'state'      : 'draft',
                'name'       : 'neutral-'+ move['date'],
                'ref'       : 'neutral-'+ move['date'],
             })
             _logger.debug('FGF move vals %s' % (vals))
             move_id = move_obj.create(cr, uid, vals,{} )
             to_post.append(move_id)
             context['move_id'] = move_id
             cr.execute("""
select account_id,analytic_account_id,
   case when sum(case when debit is null then 0 else debit end) > 0 then  sum(case when debit is null then 0 else debit end) else 0 end as credit,
   case when sum(case when debit is null then 0 else debit end) < 0 then -sum(case when debit is null then 0 else debit end) else 0 end as debit
  from account_move_line aml,
       account_move am,
       account_journal aj
 where aj.id = am.journal_id
   and aj.name not in ( 'Deloitte')
   and aj.is_opening_balance = False
   and aml.move_id = am.id
   and aml.state='valid'
   and am.company_id = %s
   and am.period_id = %s
   and am.state='posted'
 group by account_id,analytic_account_id
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
   and am.company_id = %s
   and am.period_id = %s
   and am.state='posted'
 group by account_id,analytic_account_id
having sum(case when credit is null then 0 else credit end) != 0
""" % (company_id,move['period_id'],
      company_id,move['period_id']))
             moves = [] 
             for line in cr.dictfetchall():
                 #try:
                    line['name'] = 'neutral-'+ move['date'],
                    _logger.debug('FGF create_move neutral move line %s %s' % ( vals,context))
                    #self.create_move(cr, uid, line, vals, context )
                    moves.append(self.create_move(cr, uid, line, vals, context ))
                 #except:
                 #   raise osv.except_osv(_('Error :'), _('FGF Error neutralize %s %s') % (line, vals ))
                   

             move_obj.write(cr, uid, [move_id], {'line_id': moves},  c )  
         self.write(cr, uid, acc_deloitte_ids, {'state': 'done'} )
         # period_ids are stored incorrectly - no idea why
         cr.execute("""
         update account_move_line l 
            set period_id = (select period_id from account_move m where m.id = l.move_id) 
          where period_id !=  (select period_id from account_move n where n.id = l.move_id) 
            and journal_id in (select id from account_journal where code like 'DE%');
         """)

         move_obj.button_validate(cr, uid, to_post, context)
         

         return True

chricar_account_move_line_deloitte()

