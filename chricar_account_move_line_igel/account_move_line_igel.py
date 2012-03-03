# -*- coding: utf-8 -*-

#!/usr/bin/python
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
import time
from datetime import datetime
from osv import fields,osv
import pooler
import logging

class chricar_account_move_line_igel(osv.osv):
     _name = "chricar.account.move.line.igel"
     _logger = logging.getLogger(__name__)
     _columns = {
       'company_id'         : fields.many2one('res.company', 'Company', required=True),
       'kanzlei'            : fields.integer ('Kanzlei'),
       'klient'             : fields.integer ('Klient'),
       'fiscalyear_id'      : fields.many2one('account.fiscalyear','Geschaeftsjahr'),
       'kontoart'           : fields.integer ('Kontoart'),
       'account_id'         : fields.many2one('account.account', 'Kontonummer' ),
       'kontoname'          : fields.char    ('Kontoname', size=64),
       'ba_nr'              : fields.char    ('BA-Nr',size=8),
       'periode'            : fields.integer ('Periode'),
       'period_id'          : fields.many2one('account.period', 'Period ERP', required=True, states={'posted':[('readonly',True)]}),
       'buchungsdatum'      : fields.char    ('Buchungsdatum',size=16),
       'date'               : fields.date    ('Buchungsdatum ERP'),
       'bel_nr'             : fields.char    ('Bel.Nr',size=16),
       'name'               : fields.integer ('Journalzeile'),
       'belegdatum'         : fields.char    ('Belegdatum',size=16),
       'gegenkonto'         : fields.char    ('Gegenkonto',size=16),
       'kst_nr'             : fields.char    ('KstNr',size=16),
       'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
       'text'               : fields.char    ('Text',size=128),
       'betrag_soll'        : fields.float   ('Betrag (Soll)'),
       'betrag_haben'       : fields.float   ('Betrag (Haben)'),
       'ust_kz'             : fields.char    ('Ust-KZ',size=4),
       'ust'                : fields.float   ('Ust'),
       'ust_betrag'         : fields.float   ('Ust-Betrag'),
       'fwc'                : fields.char    ('FWC',size=4),
       'fw_betrag'          : fields.float   ('FW-Betrag'),
       'betreuer'           : fields.char    ('Betreuer',size=16),
       'team'               : fields.char    ('Team',size=16),
       'klientengruppe'     : fields.char    ('Klientengruppe',size=16),
       'zessionsname'       : fields.char    ('Zessionsname',size=16),
       'state'              : fields.selection([('draft','Draft'), ('progress','Progress'), ('done','Done')], 'State', required=True,)
}

     _defaults = {
        'company_id' : lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id,
        'state' : 'draft',
}
     _order =   "name"

     _sql_constraints = [('key_uniq','unique(kanzlei,klient,fiscalyear_id,name)', 'Journalrow must be unique for kanzlei/klient/fiscalyear_id,buchungszeile!')]

     def transfer_igel_moves(self, cr, uid, ids, context=None):
         _logger = logging.getLogger(__name__)
         if not context:
            context = {}
         account_obj = self.pool.get('account.account')
         analytic_obj = self.pool.get('account.analytic.account')
         move_obj = self.pool.get('account.move')
         move_line_obj = self.pool.get('account.move.line')
         analytic_line_obj = self.pool.get('account.analytic.line')
         period_obj = self.pool.get('account.period')
         journal_obj = self.pool.get('account.journal')
         
         if context.get('company_id'):
              company_id = context.get('company_id')
         else:
              company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id

         # create  missing accounts
         acc_ids = account_obj.search(cr, uid, [('company_id','=',company_id)])
         _logger.info('FGF account ids %s' % (acc_ids))
         acc_names = []
         for acc in  account_obj.browse(cr, uid, acc_ids, context=None):
             acc_names.append(acc.name)
         _logger.info('FGF account names %s' % (acc_names))

         acc_igel_ids = self.search(cr, uid, [('company_id','=',company_id)])
	 _logger.info('FGF account igel ids %s' % (acc_igel_ids))
	 acc_igel_names = []
         for igel_acc in  self.browse(cr, uid, acc_igel_ids, context=None):
             acc_igel_names.append(igel_acc.kontoname)
	 _logger.info('FGF account igel names %s' % (acc_igel_names))

         now =  time.strftime("%Y%m%d%H%M%S")
         counter= 0
         user_type = self.pool.get('account.account.type').search(cr, uid, [('code','=','view')])[0]
         parent_id = account_obj.search(cr, uid, [('parent_id','=',False)])[0]
         for acc_igel_name in acc_igel_names:
             if acc_igel_name not in acc_names:
                 counter += 1
                 vals = {
                   'name' : acc_igel_name,
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
         aacc_names = []
         for aacc in  account_obj.browse(cr, uid, aacc_ids, context=None):
             aacc_names.append(aacc.code)

         aacc_igel_ids = self.search(cr, uid, [('company_id','=',company_id)])
         aacc_igel_names = []
         for igel_aacc in  self.browse(cr, uid, aacc_igel_ids, context=None):
             aacc_igel_names.append(igel_aacc.kst_nr)

         counter= 0
         
         for aacc_igel_name in aacc_igel_names:
             if aacc_igel_name not in aacc_names:
                 counter += 1
                 val = {
                   'code' : aacc_igel_name,
                   'name' : 'i-'+now+'-'+str(counter),
                 } 
                 analytic_obj.create(cr, uid, val)
         # update igel moves
         self.write(cr, uid, acc_igel_ids, {'state': 'progress'} )

         for igel_move in self.browse(cr, uid, acc_igel_ids, context=context):
             try:
                date =  datetime.strptime(igel_move.buchungsdatum,"%Y/%m/%d")
             except:
                date =  datetime.strptime(igel_move.buchungsdatum,"%m/%d/%Y")
#             _logger.info('FGF date %s' % (date))
             date = date.strftime('%Y-%m-%d')
#             _logger.info('FGF date %s' % (date))
             vals = {
                'date':date,
                'period_id' : period_obj.find(cr, uid, date, context=context)[0],
                'account_id' : account_obj.search(cr, uid, [('name','=', igel_move.kontoname)])[0],
                'analytic_account_id' : analytic_obj.search(cr, uid, [('code','=', igel_move.kst_nr)])[0],
             }
             self.write(cr, uid, igel_move.id, vals ,context) 

         

         # loop over vouchers
         _logger.info('FGF loop voucher ' )
         journal_id = journal_obj.search(cr, uid, [('code','=','Igel')], context=context)[0]

         cr.execute("""select distinct company_id, period_id, ba_nr||'-'||bel_nr as ref, date
                  from chricar_account_move_line_igel
                 where id in (%s)""" % (','.join(map(str,acc_igel_ids)) ))
         for move in cr.dictfetchall():
               
             _logger.info('FGF move %s' % (move))
             vals = move
             vals.update({
                'journal_id' : journal_id,
                'state'      : 'draft',
             })
             _logger.info('FGF move vals %s' % (vals))
             _logger.info('FGF move context %s' % (context))
           
             move_id = move_obj.create(cr, uid, vals, {} )
             _logger.info('FGF move_id = %s' % (move_id))

 
         
         # create move
         

         # create move lines

         # create analytic lines

         #return


chricar_account_move_line_igel()
