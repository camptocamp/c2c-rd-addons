
# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2012 ChriCar (http://www.chricar.at)
#   @author Ferdinand Gassauer
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import fields,osv
#import pooler



class chricar_account_move_line_deloitte_delete(osv.osv_memory):
    """
    For Chart of Accounts
    """
    _name = "chricar.account.move.line.deloitte.delete"
    _description = "Delete Deloitte Moves"
    _columns = {
        'fiscalyear': fields.many2one('account.fiscalyear', \
                                    'Fiscal year',  \
                                     required=True,),
        'period_from': fields.many2one('account.period', 'Start period', required=True),
        'period_to': fields.many2one('account.period', 'End period', required=True),
        'delete_keep': fields.selection([('keep', 'Keep'),('delete', 'Delete'),
                                        ], 'Imported Lines', required=True),
    }

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
        res = {}
        if fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period}
        else:
            res['value'] = {'period_from': False, 'period_to': False}
        return res

    def button_delete(self, cr, uid, ids, context=None):
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        journal_obj = self.pool.get('account.journal')
        deloitte_obj = self.pool.get('chricar.account_move_line_deloitte')

        journal_ids = journal_obj.search(cr, uid, [('code','in',['DE','DEN'])]) # Deloitte Journals

        data = self.read(cr, uid, ids, [], context=context)[0]
        period_from = data['period_from'][0]
        period_to = data['period_to'][0]
        period_ids = period_obj.build_ctx_periods(cr, uid, period_from, period_to)
        if not isinstance(period_ids, list):
            period_ids = [period_ids]
        move_ids = move_obj.search(cr, uid, [('period_id','in',period_ids),('journal_id','in',journal_ids)])
        move_obj.button_cancel(cr, uid, move_ids)
        move_obj.unlink(cr, uid, move_ids)

        deloitte_ids = deloitte_obj.search(cr, uid, [('period_id','in',period_ids)])
        if  data['delete_keep'] == 'keep':
            deloitte_obj.write(cr, uid, deloitte_ids, {'state':'draft'})
        else:
            deloitte_obj.unlink(cr, uid, deloitte_ids)

chricar_account_move_line_deloitte_delete()
