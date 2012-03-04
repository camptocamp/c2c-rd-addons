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
                 account_ids= self.pool.get('account.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',move.account)])
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
       'counter_account'    : fields.char    ('Counter Account', size=8),
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

         if context.get('company_id'):
              company_id = context.get('company_id')
         else:
              company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
              context['company_id'] = company_id

         acc_deloitte_ids = self.search(cr, uid, [('company_id','=',company_id),('state','not in',('progress','done'))])
         if not acc_deloitte_ids:
             return
         self.write(cr, uid, acc_deloitte_ids, {'state': 'progress'} )
         acc_ids = account_obj.search(cr, uid, [('company_id','=',company_id)])
         #_logger.info('FGF account ids %s' % (acc_ids))
         acc_codes = []
         for acc in  account_obj.browse(cr, uid, acc_ids, context=None):
             acc_codes.append(acc.code)
         #_logger.info('FGF account names %s' % (acc_names))

         #_logger.info('FGF account deloitte ids %s' % (acc_deloitte_ids))
         acc_deloitte_codes = []
         for deloitte_acc in  self.browse(cr, uid, acc_deloitte_ids, context=None):
             acc_deloitte_codes.append(deloitte_acc.account)
         
         now =  time.strftime("%Y%m%d%H%M%S")
         counter= 0
         user_type = self.pool.get('account.account.type').search(cr, uid, [('code','=','view')])[0]
         parent_id = account_obj.search(cr, uid, [('parent_id','=',False)])[0]
         for acc_deloitte_code in acc_deloitte_codes:
             if acc_deloitte_code not in acc_codes:
                 counter += 1
                 vals = {
                   'name' : acc_deloitte_code,
                   'code' : 'i-'+now+'-'+str(counter),
                   'type' : 'other',
                   'user_type' : user_type,
                   'currency_mode' : 'current',
                   'parent_id' : parent_id,
                 }
                 _logger.info('FGF new account %s' % (vals))
                 account_obj.create(cr, uid, vals, context)

         # create missing analytic accounts
         aacc_ids = account_obj.search(cr, uid, [('company_id','=',company_id)])
         aacc_codes = []
         for aacc in  account_obj.browse(cr, uid, aacc_ids, context=None):
             aacc_codess.append(aacc.code)

         aacc_deloitte_ids = self.search(cr, uid, [('company_id','=',company_id)])
         aacc_deloitte_codes = []
         for deloitte_aacc in  self.browse(cr, uid, aacc_deloitte_ids, context=None):
             if deloitte_aacc.analytic_account:
                  aacc_deloitte_codes.append(deloitte_aacc.analytic_account)

         counter= 0

         for aacc_deloitte_code in aacc_deloitte_codes:
             if aacc_deloitte_code and aacc_deloitte_code not in aacc_codes:
                 counter += 1
                 val = {
                   'code' : aacc_deloitte_code,
                   'name' : 'i-'+now+'-'+str(counter),
                 }
                 analytic_obj.create(cr, uid, val)

         # update deloitte moves
         for deloitte_move in self.browse(cr, uid, acc_deloitte_ids, context=context):
              vals = {}
              if not deloitte_move.account_id:
                   vals['account_id'] =  account_obj.search(cr, uid, [('code','=', deloitte_move.account)])[0],
              if not deloitte_move.analytic_account_id:
                   vals['analytic_account_id'] :  analyitc_obj.search(cr, uid, [('code','=', deloitte_move.anayltic_account)])[0],
              if vals:
                  self.write(cr, uid, deloitte_move.id, vals ,context)
                  
chricar_account_move_line_deloitte()

