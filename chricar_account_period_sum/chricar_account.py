# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import logging

class account_account(osv.osv):
    _inherit = "account.account"
    _logger = logging.getLogger(__name__)

    def __compute_sum(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        """ compute the balance, debit and/or credit for the provided
        account ids
        Arguments:
        `ids`: account ids
        `field_names`: the fields to compute (a list of any of
                       'balance', 'debit' and 'credit')
        `arg`: unused fields.function stuff
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        """
        mapping = {
            'opening_balance_sum': "sum(case when substr(name,5,2) = '00' then debit - credit else 0 end) as opening_balance_sum",
            'debit_sum'  : "sum(case when substr(name,5,2) = '00' then 0 else debit end) as debit_sum",
            'credit_sum' : "sum(case when substr(name,5,2) = '00' then 0 else credit end) as credit_sum",
            'balance_sum': "sum(debit) - sum(credit) as balance_sum" ,
        }
        #get all the necessary accounts
        children_and_consolidated = self._get_children_and_consol(cr, uid, ids, context=context)

        #compute for each account the balance/debit/credit from the move lines
        accounts = {}
        if children_and_consolidated:
            # FIXME allow only fy and period filters
            # remove others filters from context or raise error
            #aml_query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)

            #wheres = [""]
            #if query.strip():
            #    wheres.append(query.strip())
            #if aml_query.strip():
            #    wheres.append(aml_query.strip())
            #filters = " AND ".join(wheres)
            #filters = ' AND period_id in ( select id from account_period where fiscalyear_id in ( %s ) ) ' % context.get('fiscalyear', False)
            if context.get('periods', False):
                periods = context.get('periods', False)
            else:
                # default if startet without form
                date = time.strftime('%Y-%m-%d')
                fiscalyear_pool = self.pool.get('account.fiscalyear')
                fy_id = fiscalyear_pool.search(cr, uid, [('date_start','<=',date), ('date_stop','>=',date)])
                period_pool = self.pool.get('account.period')
                periods = period_pool.search(cr, uid, [('fiscalyear_id','in',fy_id)])

            self._logger.debug('Periods: `%s`', periods)
            # FIXME - tuple must not return ',' if only one period is available - period_id in ( p,) should be period_id in ( p )
            filters = ''
            if periods:
                filters = ' AND period_id in (%s) ' % (','.join(map(str,periods)) )
            # IN might not work ideally in case there are too many
            # children_and_consolidated, in that case join on a
            # values() e.g.:
            # SELECT l.account_id as id FROM account_move_line l
            # INNER JOIN (VALUES (id1), (id2), (id3), ...) AS tmp (id)
            # ON l.account_id = tmp.id
            # or make _get_children_and_consol return a query and join on that
            request = ("SELECT l.account_id as id, " +\
                       ', '.join(map(mapping.__getitem__, field_names)) +
                       " FROM account_account_period_sum l" \
                       " WHERE l.account_id IN %s " \
                            + filters +
                       " GROUP BY l.account_id")
            params = (tuple(children_and_consolidated),) + query_params
            cr.execute(request, params)
            self._logger.debug('Status: `%s`', cr.statusmessage)

            for res in cr.dictfetchall():
                accounts[res['id']] = res

            # consolidate accounts with direct children
            children_and_consolidated.reverse()
            brs = list(self.browse(cr, uid, children_and_consolidated, context=context))

            sums = {}
            currency_obj = self.pool.get('res.currency')
            while brs:
                current = brs[0]
#                can_compute = True
#                for child in current.child_id:
#                    if child.id not in sums:
#                        can_compute = False
#                        try:
#                            brs.insert(0, brs.pop(brs.index(child)))
#                        except ValueError:
#                            brs.insert(0, child)
#                if can_compute:
                brs.pop(0)
                for fn in field_names:
                    sums.setdefault(current.id, {})[fn] = accounts.get(current.id, {}).get(fn, 0.0)
                    for child in current.child_id:
                        if child.company_id.currency_id.id == current.company_id.currency_id.id:
                            sums[current.id][fn] += sums[child.id][fn]
                        else:
                            sums[current.id][fn] += currency_obj.compute(cr, uid, child.company_id.currency_id.id, current.company_id.currency_id.id, sums[child.id][fn], context=context)
            res = {}
            null_result = dict((fn, 0.0) for fn in field_names)
            for id in ids:
                res[id] = sums.get(id, null_result)
            return res

    def __compute_prev_sum(self, cr, uid, ids, field_names, arg=None, context=None,
                  query=None, query_params=None):
        """ compute the balance, debit and/or credit for the provided
        account ids
        Arguments:
        `ids`: account ids
        `field_names`: the fields to compute (a list of any of
                       'balance', 'debit' and 'credit')
        `arg`: unused fields.function stuff
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        """
        mapping = {
             'balance_prev_sum': "sum(debit) - sum(credit) as balance_prev_sum" ,
        }
        #get all the necessary accounts
        children_and_consolidated = self._get_children_and_consol(cr, uid, ids, context=context)
        self._logger.debug('Children: `%s`', children_and_consolidated)

        #compute for each account the balance/debit/credit from the move lines
        accounts = {}
        if children_and_consolidated :
            # FIXME allow only fy and period filters
            # remove others filters from context or raise error
            #aml_query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)

            #wheres = [""]
            #if query.strip():
            #    wheres.append(query.strip())
            #if aml_query.strip():
            #    wheres.append(aml_query.strip())
            #filters = " AND ".join(wheres)
            if context.get('periods_prev', False):
                periods_prev = context.get('periods_prev', False)
            else:
                # default if startet without form
                date = (datetime.today() + relativedelta(years=-1)).strftime('%Y-%m-%d')
                fiscalyear_pool = self.pool.get('account.fiscalyear')
                fy_id = fiscalyear_pool.search(cr, uid, [('date_start','<=',date), ('date_stop','>=',date)])
                period_pool = self.pool.get('account.period')
                periods_prev = period_pool.search(cr, uid, [('fiscalyear_id','in',fy_id),('date_start','<=',date)])
            if periods_prev and len(periods_prev) > 0:
                filters = ' AND period_id in (%s) ' % (','.join(map(str,periods_prev)) )
            else:
                filters = ' AND 1=2'
            # IN might not work ideally in case there are too many
            # children_and_consolidated, in that case join on a
            # values() e.g.:
            # SELECT l.account_id as id FROM account_move_line l
            # INNER JOIN (VALUES (id1), (id2), (id3), ...) AS tmp (id)
            # ON l.account_id = tmp.id
            # or make _get_children_and_consol return a query and join on that
            if not query_params:
                query_params = ''
            params = (', '.join(map(str,children_and_consolidated)))
            request = ("SELECT l.account_id as id, " +\
                       ', '.join(map(mapping.__getitem__, field_names)) +
                       " FROM account_account_period_sum l" \
                       " WHERE l.account_id IN (%s) " \
                            + filters +
                       " GROUP BY l.account_id") % (params)
            #params = (tuple(children_and_consolidated),)
            #params = (tuple(children_and_consolidated),) + query_params
            #params = (', '.join(map(str,children_and_consolidated)))
            self._logger.debug('Request: `%s`', request)
            self._logger.debug('Params: `%s`', params)
            cr.execute(request)
            self._logger.debug('Status: `%s`', cr.statusmessage)

            for res in cr.dictfetchall():
                accounts[res['id']] = res

            # consolidate accounts with direct children
            children_and_consolidated.reverse()
            brs = list(self.browse(cr, uid, children_and_consolidated, context=context))

            sums = {}
            currency_obj = self.pool.get('res.currency')
            while brs:
                current = brs[0]
#                can_compute = True
#                for child in current.child_id:
#                    if child.id not in sums:
#                        can_compute = False
#                        try:
#                            brs.insert(0, brs.pop(brs.index(child)))
#                        except ValueError:
#                            brs.insert(0, child)
#                if can_compute:
                brs.pop(0)
                for fn in field_names:
                    sums.setdefault(current.id, {})[fn] = accounts.get(current.id, {}).get(fn, 0.0)
                    for child in current.child_id:
                        if child.company_id.currency_id.id == current.company_id.currency_id.id:
                            sums[current.id][fn] += sums[child.id][fn]
                        else:
                            sums[current.id][fn] += currency_obj.compute(cr, uid, child.company_id.currency_id.id, current.company_id.currency_id.id, sums[child.id][fn], context=context)
            res = {}
            null_result = dict((fn, 0.0) for fn in field_names)
            for id in ids:
                res[id] = sums.get(id, null_result)
            return res


    _columns = {
        'opening_balance_sum': fields.function(__compute_sum, digits_compute=dp.get_precision('Account'), method=True, string='Opening Balance', multi='balance_sum'),
        'balance_sum': fields.function(__compute_sum, digits_compute=dp.get_precision('Account'), method=True, string='Balance', multi='balance_sum'),
        'credit_sum': fields.function(__compute_sum, digits_compute=dp.get_precision('Account'), method=True, string='Credit', multi='balance_sum'),
        'debit_sum': fields.function(__compute_sum, digits_compute=dp.get_precision('Account'), method=True, string='Debit', multi='balance_sum'),
        'balance_prev_sum': fields.function(__compute_prev_sum, digits_compute=dp.get_precision('Account'), method=True, string='Balance Prev Year', multi='balance_prev_sum'),
        }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        account_period_sum_obj = self.pool.get('account.account_period_sum')

        res = super(account_account, self).write(cr, uid, ids, vals, context)
        for account in self.browse(cr, uid, ids):
            cr.execute("""delete from account_account_period_sum where account_id = %s""" %(account.id))
            account_period_sum_obj.init_sum(cr, uid, [account.id])

        return res

account_account()
