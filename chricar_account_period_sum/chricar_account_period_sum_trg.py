# -*- coding: utf-8 -*-
# ChriCar Beteiligungs- und Beratungs- GmbH
# Camptocamp Austria
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
from osv import fields, osv
import logging

class account_move(osv.osv):
    _inherit = "account.move"
    
    def _compute_opening_blance(self, cr, uid, account_id, fiscalyear_id):
        _logger = logging.getLogger(__name__)
        fy_obj = self.pool.get('account.fiscalyear')
        per_obj = self.pool.get('account.period')
        per_sum_obj = self.pool.get('account.account_period_sum')
        
        future_fy_id = ''
        date_start = ''
        for fy in fy_obj.browse(cr, uid, [fiscalyear_id]):
            sql = """
        select id 
          from account_fiscalyear 
         where date_start = (select min(date_start)
                               from account_fiscalyear
                              where date_start > to_date('%s','YYYY-MM-DD'))
        """ % (fy.date_start)
            _logger.debug('FGF sql fyid`%s`', sql)
            cr.execute(sql)
            future_fy_id = cr.fetchone()
            if future_fy_id:
              future_fy_id = future_fy_id[0]
              for future_fy in fy_obj.browse(cr, uid, [future_fy_id]):
                per_ids = per_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id)])
                sql="""
                select sum(debit-credit)
                  from account_account_period_sum
                 where period_id in (%s)
                   and account_id = %s
                """ % ( ','.join(map(str,per_ids)), account_id)
                cr.execute(sql)
                balance = cr.fetchone()[0]
                _logger.debug('FGF sql balance`%s`', balance)
                debit = 0.0
                credit = 0.0
                if balance > 0.0:
                    debit = balance
                if balance < 0.0:
                    credit = -balance
                vals = {
                    'debit' : debit,
                    'credit' : credit
                    }
                
                per_ob_id = per_sum_obj.search(cr, uid, [('account_id','=', account_id), ('name','=', future_fy.code+'00') ])
                if per_ob_id:
                    per_sum_obj.write(cr, uid, per_ob_id, vals)
                elif balance != 0:
                    period_id = per_obj.search(cr, uid, [('fiscalyear_id','=',future_fy.id),('date_start','=',future_fy.date_start)])[0]
                    vals['company_id'] = fy.company_id.id
                    vals['account_id'] = account_id
                    vals['name']       = future_fy.code+'00'
                    vals['period_id']  = period_id
                    vals['sum_fy_period_id'] = future_fy_id
                    per_sum_obj.create(cr, uid, vals)
                self._compute_opening_blance(cr, uid, account_id, future_fy_id)
        
    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        _logger = logging.getLogger(__name__)
        move_pre_post_ids = self.search(cr, uid, [('id','in',ids),('state','=','posted')]) 
        res = super(account_move, self).post(cr, uid, ids, context)
        move_post_post_ids = self.search(cr, uid, [('id','in',ids),('state','=','posted')])
        move_ids = []
        for post_id in move_post_post_ids:
            if post_id not in move_pre_post_ids:
                move_ids.append(post_id)
        _logger.debug('FGF sql move_ids `%s`,`%s`, `%s`, `%s`' % (ids, move_pre_post_ids, move_post_post_ids,  move_ids))      
        if not move_ids:
            return res
            
        sql1="""
            select l.company_id, l.account_id, l.period_id, p.date_start, p.fiscalyear_id, sum(debit) as debit, sum(credit), p.name as credit
              from account_move_line l,
                   account_period p,
                   account_journal j
             where move_id in (%s)
               and l.state = 'valid'
               and p.id = l.period_id
               and j.is_opening_balance,False) is False
             group by l.company_id, l.account_id, p.date_start, l.period_id, p.fiscalyear_id, p.name
             order by l.company_id, l.account_id, p.date_start, l.period_id ;
            """ %  (','.join(map(str,move_ids))) 

        _logger.debug('FGF sql`%s`', sql1)

        cr.execute(sql1)
        per_sum = cr.fetchall()
        
        per_sum_obj = self.pool.get('account.account_period_sum')
        account_obj = self.pool.get('account.account')
        
        for per_val in per_sum:
            account_id   = per_val[1]
            period_id    = per_val[2]
            fiscalyear_id= per_val[4]
            
            vals={
                'account_id'   : account_id,
                'period_id'    : period_id,
                'debit'        : per_val[5],
                'credit'       : per_val[6] 
                }
            per_id = per_sum_obj.search(cr, uid, [('account_id','=', account_id), ('period_id','=', period_id),('name','not like','%00') ])
            if per_id:
                for per_sum in per_sum_obj.browse(cr, uid, per_id):
                    vals['debit'] += per_sum.debit
                    vals['credit'] += per_sum.credit
                per_sum_obj.write(cr, uid, per_id, vals) 
            else:    
                vals['company_id'] = per_val[0]
                vals['sum_fy_period_id'] = fiscalyear_id
                vals['name'] = per_val[7]
                per_sum_obj.create(cr,uid, vals)
            
            # compute opening balance 
            for account in account_obj.browse(cr, uid, [account_id]):
                if account.user_type.close_method != 'none':
                    self._compute_opening_blance(cr, uid, account.id, fiscalyear_id)
        return res              

account_move()