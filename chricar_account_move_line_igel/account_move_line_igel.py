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
from openerp.osv import fields,osv
#import pooler
import logging

class chricar_account_move_line_igel(osv.osv):
    _name = "chricar.account.move.line.igel"
    _logger = logging.getLogger(__name__)



    def _analytic_account_id(self, cr, uid, ids, name, arg, context):
         result = {}
         for move in self.browse(cr, uid, ids):
             result[move.id] = False
             if move.kst_nr and move.company_id:
                 account_ids= self.pool.get('account.analytic.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',move.kst_nr)])
                 if len(account_ids):
                     result[move.id] = account_ids[0]
         return result

    _columns = {
      'company_id'         : fields.many2one('res.company', 'Company', required=True),
      'kanzlei'            : fields.integer ('Kanzlei'),
      'klient'             : fields.integer ('Klient'),
       'fiscalyear_id'      : fields.related ('period_id', 'fiscalyear_id', string='Fiscal Year', type='many2one', relation='account.fiscalyear', store=True),
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
       'analytic_account_id': fields.function(_analytic_account_id, method=True, string="Analytic Account",type='many2one', relation='account.analytic.account',  select="1", store=True ),
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
       'company_id' : lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id,
       'state' : 'draft',
}
    _order =   "name"

    _sql_constraints = [('key_uniq','unique(kanzlei,klient,fiscalyear_id,name)', 'Journalrow must be unique for kanzlei/klient/fiscalyear_id,buchungszeile!')]

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
        location_ids = location_obj.search(cr, uid, [('company_id','=',company_id)])
        _logger.debug('FGF location ids %s' % (location_ids))

        acc_igel_ids = self.search(cr, uid, [('company_id','=',company_id),('state','not in',('progress','done'))])
        if not acc_igel_ids:
            return
        self.write(cr, uid, acc_igel_ids, {'state': 'progress'} )
        # create  missing accounts
        acc_ids = account_obj.search(cr, uid, [('company_id','=',company_id)])
        #_logger.debug('FGF account ids %s' % (acc_ids))
        acc_names = []
        for acc in  account_obj.browse(cr, uid, acc_ids, context=None):
            acc_names.append(acc.name)
        #_logger.debug('FGF account names %s' % (acc_names))

        #_logger.debug('FGF account igel ids %s' % (acc_igel_ids))
        acc_igel_names = []
        for igel_acc in  self.browse(cr, uid, acc_igel_ids, context=None):
            acc_igel_names.append(igel_acc.kontoname)
        #_logger.debug('FGF account igel names %s' % (acc_igel_names))

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
                _logger.debug('FGF new account %s' % (vals))
                account_obj.create(cr, uid, vals, context)

        # create missing analytic accounts
        aacc_ids = account_obj.search(cr, uid, [('company_id','=',company_id)])
        aacc_names = []
        for aacc in  account_obj.browse(cr, uid, aacc_ids, context=None):
            aacc_names.append(aacc.code)

        aacc_igel_ids = self.search(cr, uid, [('company_id','=',company_id)])
        aacc_igel_names = []
        for igel_aacc in  self.browse(cr, uid, aacc_igel_ids, context=None):
            if igel_aacc.kst_nr:
                aacc_igel_names.append(igel_aacc.kst_nr)

        counter= 0

        for aacc_igel_name in aacc_igel_names:
            if aacc_igel_name and aacc_igel_name not in aacc_names:
                counter += 1
                val = {
                  'code' : aacc_igel_name,
                  'name' : 'i-'+now+'-'+str(counter),
                }
                analytic_obj.create(cr, uid, val)

        # update igel moves
        for igel_move in self.browse(cr, uid, acc_igel_ids, context=context):
            try:
                date =  datetime.strptime(igel_move.buchungsdatum,"%Y/%m/%d")
            except:
                date =  datetime.strptime(igel_move.buchungsdatum,"%m/%d/%Y")
#             _logger.debug('FGF date %s' % (date))
            date = date.strftime('%Y-%m-%d')
#             _logger.debug('FGF date %s' % (date))

            vals = {
               'date':date,
               'period_id' : period_obj.find(cr, uid, date, context=context)[0],
               'account_id' : account_obj.search(cr, uid, [('name','=', igel_move.kontoname)])[0],
            }
            if not igel_move.analytic_account_id and igel_move.kst_nr:
                a_id = analytic_obj.search(cr, uid, [('code','=', igel_move.kst_nr)])[0]
                if a_id:
                    vals['analytic_account_id'] = a_id
            if not vals.get('analytic_account_id'):
                text = igel_move.text.upper()
                _logger.debug('FGF text %s' % (text))
                top_ind = text.find('TOP ')
                text = text[top_ind:]
                _logger.debug('FGF text %s' % (text))
                if top_ind >= 0:
                    top = text.replace('TOP ','')
                    _logger.debug('FGF top %s' % (top))
                    top_ind = top.find(' ')
                    top_ind2 = top.find(',')
                    if top_ind >0:
                        top_nr = top[:top_ind]
                    else:
                        top_nr = top
                    top_nr = top_nr.replace(',','')
                    _logger.debug('FGF top nr %s' % (top_nr))
                    top_ids = top_obj.search(cr, uid, [('name','=',top_nr),('location_id', 'in', location_ids)])
                    _logger.debug('FGF top_ids %s' % (top_ids))
                    for top_id in top_obj.browse(cr, uid, top_ids, {}):
                        _logger.debug('FGF top analyt %s' % (top_id.account_analytic_id))
                        if top_id.account_analytic_id:
                            vals['analytic_account_id']  = top_id.account_analytic_id.id


            self.write(cr, uid, igel_move.id, vals ,context)


    def transfer_igel_moves(self, cr, uid, ids, context=None):
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

        acc_igel_ids = self.search(cr, uid, [('company_id','=',company_id),('state','=','progress')])
        if not acc_igel_ids:
            return
        # loop over vouchers
        #_logger.debug('FGF loop voucher ' )
        journal_id = journal_obj.search(cr, uid, [('code','=','Igel')], context=context)[0]
        journal_analyitc_id = analytic_jour_obj.search(cr, uid, [('code','=','Igel')], context=context)[0]

        cr.execute("""select distinct company_id, period_id, ba_nr||'-'||bel_nr as name, date
                 from chricar_account_move_line_igel
                where id in (%s)""" % (','.join(map(str,acc_igel_ids)) ))
        for move in cr.dictfetchall():

            #_logger.debug('FGF move %s' % (move))
            vals = move
            vals.update({
               'journal_id' : journal_id,
               'state'      : 'draft',
            })
            #_logger.debug('FGF move vals %s' % (vals))

            move_id = move_obj.create(cr, uid, vals, {} )
            #_logger.debug('FGF move_id = %s' % (move_id))
            cr.execute("""select account_id, period_id, company_id, betrag_soll as debit, betrag_haben as credit, text as name, analytic_account_id
                            from chricar_account_move_line_igel
                           where company_id = %s
                             and period_id  = %s
                             and ba_nr||'-'||bel_nr = '%s'""" % ( vals['company_id'], vals['period_id'], vals['name'] ))
            for line in cr.dictfetchall():
                l = line
                l['move_id'] = move_id
                if l['debit'] < 0 or l['credit'] < 0:
                    l['debit'] = line['credit']
                    l['credit'] = line['debit']
                # _logger.debug('FGF move lines%s' % (l))
                move_line_id = move_line_obj.create(cr, uid, l)
                if line['analytic_account_id']:
                    l['general_account_id'] = line['account_id']
                    l['account_id'] = line['analytic_account_id']
                    l['journal_id'] = journal_analyitc_id
                    l['move_id'] = move_line_id
                    if l['debit'] > 0.0 :
                        l['amount'] = -l['debit']
                    else:
                        l['amount'] = l['credit']
                    analytic_line_obj.create(cr, uid, l)

        self.write(cr, uid, acc_igel_ids, {'state': 'done'} )
        return


chricar_account_move_line_igel()
