# -*- coding: utf-8 -*-
##############################################
# ChriCar Beteiligungs- und Beratungs- GmbH
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
#
###############################################
from openerp.osv import fields, osv
from openerp.tools.misc import currency
from openerp.tools.sql import drop_view_if_exists
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging



class account_journal(osv.osv):
    _inherit = "account.journal"
    _columns = \
        { 'is_opening_balance'  : fields.boolean
            ( 'Is Opening Balance Journal'
            ,  help="check this and use this journal for closing fiscal year, the opening balance moves will not be added to chricar periods sum as opening balance is a special period 00"
            )
        }
    _defaults = {'is_opening_balance' : lambda *a: False}
account_journal()

# name should hold the period name + special names:
class account_period(osv.osv):
    _inherit = "account.period"

    def _get_prev_fy_period(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for p in self.pool.get('account.period').browse(cr, uid, ids, context=context):
            date_start = str(int(p.date_start[0:4]) - 1 ) + p.date_start[4:10]
            cr.execute("""
select id from account_period
  where
    company_id = %s
    and date_start = %s
    and special = %s """, ( p.company_id.id or p.fiscalyear_id.company_id.id, date_start, p.special))
            res[p.id] = cr.fetchone() #or False
        return res

    _columns = \
        { 'prev_fy_period': fields.function
            ( _get_prev_fy_period
            , method=True
            , relation='account.period'
            , type="many2one"
            , string='Period Prev FY'
            , store =True
            )
        }
account_period()

class account_period_sum(osv.osv):
    _name        = "account.account_period_sum"
    _description = "Account Period Sum"
    _columns     = \
        { 'name'             : fields.char    ('Period', size=16,reaodonly=True)
        , 'company_id'       : fields.many2one('res.company', 'Company', required=True)
        , 'account_id'       : fields.many2one('account.account', 'Account', required=True,ondelete="cascade",readonly=True, select="1")
        , 'period_id'        : fields.many2one('account.period' , 'Period' , required=True,ondelete="cascade",readonly=True, select="1")
        , 'sum_fy_period_id' : fields.integer ('Account FY id'             , required=True,                   readonly=True)
        , 'debit'            : fields.float   ('Debit', digits_compute=dp.get_precision('Account'), required=True,readonly=True)
        , 'credit'           : fields.float   ('Credit', digits_compute=dp.get_precision('Account'), required=True,readonly=True)
        }
    _order = 'name asc'

    def _auto_init(self, cr, context=None):
        super(account_period_sum, self)._auto_init(cr, context=context)
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = \'account_account_period_sum_index\'')
        if not cr.fetchone():
            cr.execute('CREATE INDEX account_account_period_sum_index ON account_account_period_sum ( account_id, period_id)')

    def init(self, cr):

        cr.execute("""drop function if exists account_period_sum_update(integer,integer);""")
        cr.execute("""drop function if exists account_period_sum_create(integer);""")
        cr.execute("""drop function if exists account_close_method_update(integer, varchar);""")

        cr.execute("""drop trigger if exists trg_account_move_sum_delete on account_move;""")
        cr.execute("""drop trigger if exists trg_account_move_sum_insert on account_move;""")
        cr.execute("""drop trigger if exists trg_account_move_sum_update on account_move;""")
        cr.execute("""drop trigger if exists account_close_method_update_f on account_move;""")
        cr.execute("""drop trigger if exists account_period_sum_insert on account_move;""")
        cr.execute("""drop trigger if exists trg_account_period_sum_insert on account_period;""") 


        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = \'account_account_period_sum_index\'')
        if not cr.fetchone():
            cr.execute('CREATE INDEX account_account_period_sum_index ON account_account_period_sum ( account_id, period_id)')

        cr.execute("delete from account_account_period_sum;")
        self.init_sum(cr, 1)

    def init_sum(self, cr, uid, account_ids=None):
        where = ''
        if account_ids:
            where = ' and account_id in ( %s )' % (','.join(map(str, account_ids)))
        sql="""
INSERT
  into account_account_period_sum(create_uid, create_date, name,sum_fy_period_id,period_id,company_id,account_id,credit,debit)
  SELECT
      1 as create_uid,
      now() at time zone 'UTC',
      p.name,
      nextval('account_account_period_sum_id_seq'::regclass),
      l.period_id,
      l.company_id,
      account_id,
      sum(coalesce(credit,0)),sum(coalesce(debit,0))
    from
      account_move_line l,
      account_period p,
      account_journal j,
      account_move m
    where
      p.id=l.period_id
      and j.id = l.journal_id
      and coalesce(j.is_opening_balance,False) is False
      and m.state = 'posted'
      and m.id = l.move_id
      and p.special != True
      and p.company_id = l.company_id
      and j.company_id = l.company_id %s
    group by p.name,l.period_id, l.company_id, account_id ,fiscalyear_id ;
""" % (where)
        cr.execute(sql)
        
        account_obj = self.pool.get('account.account')
        if account_ids:
            all_ids = account_ids
        else:
            all_ids = account_obj.search(cr, uid, [])
        
        account_ids = []
        for account in account_obj.browse(cr, uid, all_ids):
            if account.user_type.close_method != 'none':
                account_ids.append(account.id)

        if account_ids:
            sql1="""
    select distinct l.account_id, p.fiscalyear_id, f.date_start
        from account_move_line l,
            account_period p,
            account_fiscalyear f
        where l.state = 'valid'
        and p.id = l.period_id
        and f.id = p.fiscalyear_id
        and l.account_id in (%s)
        order by l.account_id, f.date_start ;
                """ % ( ','.join(map(str, account_ids)))

            cr.execute(sql1)
            fy_sum = cr.fetchall()
            move_obj = self.pool.get('account.move')
            for fy_val in fy_sum:
                account_id   = fy_val[0]
                fiscalyear_id= fy_val[1]
                move_obj._compute_opening_balance(cr, uid, account_id, fiscalyear_id)


account_period_sum()

class account_fy_period_sum(osv.osv):
    _name        = "account.account_fy_period_sum"
    _description = "Account Fiscalyear Period Sum"
    _auto        = False
    _columns     = \
        { 'name'               : fields.char    ('Period', size=16       ,readonly=True)
        , 'company_id'         : fields.many2one('res.company', 'Company', required=True)
        , 'account_id'         : fields.many2one('account.account', 'Account',readonly=True)
        , 'period_id'          : fields.many2one('account.period' , 'Period' ,readonly=True)
        , 'fiscalyear_id'      : fields.many2one('account.fiscalyear' , 'Fiscal Year' ,readonly=True)
        , 'debit'              : fields.float   ('Debit', digits_compute=dp.get_precision('Account') ,readonly=True)
        , 'credit'             : fields.float   ('Credit', digits_compute=dp.get_precision('Account'),readonly=True)
        , 'balance'            : fields.float   ('Balance Period', digits_compute=dp.get_precision('Account')    ,readonly=True)
        , 'balance_cumulative' : fields.float   ('Balance cumulativ', digits_compute=dp.get_precision('Account')    ,readonly=True)
#        , 'sum_fy_period_id'   : fields.integer ('Account FY id'             ,readonly=True)
        , 'date_start'           : fields.date    ('Date Start',readonly=True)
        , 'date_stop'           : fields.date    ('Date Stop' ,readonly=True)
        , 'move_line_ids'      : fields.one2many('account.move.line','account_period_sum_id','Account_moves')
        }
    _order = 'date_start asc,name'

    def init(self, cr):
        drop_view_if_exists(cr, "account_account_fy_period_sum")
        cr.execute("""
  create or replace view account_account_fy_period_sum as
    select
        s.id  as id,
        s.name,
        s.company_id,
        s.account_id,s. period_id, p.fiscalyear_id,
        s.debit as debit ,s.credit as credit,
        s.debit-s.credit as balance,
        sum(case when pcum.date_start <= p.date_start then cum.debit-cum.credit else 0 end) as balance_cumulative,
        --s.sum_fy_period_id as sum_fy_period_id,
        p.date_start,p.date_stop
      from
        account_account_period_sum s,
        account_period p,
        account_fiscalyear y,
        account_account_period_sum cum,
        account_period pcum
      where
        p.id = s.period_id
        and y.id = p.fiscalyear_id
        and pcum.id = cum.period_id
        and y.id = pcum.fiscalyear_id
        and pcum.date_start <= p.date_start
        and case when s.name like '%00' then s.id = cum.id else 1=1 end
        and cum.account_id = s.account_id
      group by
        s.id,
        s.name,
        s.company_id,
        s.account_id,s.period_id,p.fiscalyear_id,
        s.debit,s.credit ,
        s.debit-s.credit ,
        s.sum_fy_period_id ,
        p.date_start,
        p.date_stop;
  """)
account_fy_period_sum()

class account_fiscalyear_sum(osv.osv):
    _name        = "account.account_fiscalyear_sum"
    _logger      = logging.getLogger(_name)
    _description = "Account Fiscalyear Sum"
    _auto        = False

    # to avoid view_id
    class one2many_periods (fields.one2many):
        #_logger      = logging.getLogger(_name)
        def get (self, cr, obj, ids, name, user=None, offset=0, context=None, values={}):
            res = {}
            for id in ids :
                res[id] = []
                print "ID",id
                fy = obj.pool.get('account.account_fiscalyear_sum').browse(cr, user, id, context=context)
                ids2 = obj.pool.get (self._obj).search \
                    ( cr
                    , user
                    , [ ('company_id', '=', fy.company_id.id)
                      , ('account_id', '=', fy.account_id.id)
                      , ('fiscalyear_id', '=', fy.fiscalyear_id.id)
                      ]
                    , limit = self._limit
                    )
                for r in ids2:
                    #self._logger.debug('r_ids2 `%s`', r)
                    res [fy.id].append(r)
            return res
        #  set missing
    # end class one2many_periods

    class one2many_per_delta (fields.one2many):
        #_logger      = logging.getLogger(_name)
        def get (self, cr, obj, ids, name, user=None, offset=0, context=None, values={}):
            res = {}
            for id in ids :
                res[id] = []
                fy = obj.pool.get('account.account_fiscalyear_sum').browse(cr, user, id, context=context)
                delta_obj = obj.pool.get('account.account.period.sum.delta')
                ids3 = delta_obj.search \
                    ( cr
                    , user
                    , [ ('company_id', '=', fy.company_id.id)
                      , ('account_id', '=', fy.account_id.id)
                      , ('fiscalyear_id', '=', fy.fiscalyear_id.id)
                      ]
                    , limit = self._limit
                    )
                #cr.execute("""select id from account_account_period_sum_delta
                #           where company_id = %s
                #             and account_id = %s
                #             and fiscalyear_id = %s
                #             order by name""" , (fy.company_id.id,fy.account_id.id,fy.fiscalyear_id.id))
                #ids3 = cr.fetchall()

                #self._logger.debug('ids3 `%s`', ids3)

                def _cmp(a, b) :
                    if a.name < b.name : return -1
                    elif a.name > b.name : return 1
                    #else :
                    #   if  a.move_id.name < b.move_id.name : return -1
                    #  elif a.move_id.name > b.move_id.name : return 1
                    return 0
                # end def _cmp

                #for r in ids3:
                for r in sorted(delta_obj.browse(cr, user, ids3, context), cmp=lambda a, b: _cmp(a, b)):
                #TypeError: browse_record(account.account.period.sum.delta, 1761010) is not JSON serializable
                    #self._logger.debug('r_ids3 `%s` `%s`', r, r.name)
                    res [fy.id].append( r.id )
            return res

    _columns = \
        { 'company_id'         : fields.many2one('res.company', 'Company', required=True)
        , 'account_id'         : fields.many2one('account.account', 'Account',readonly=True)
        , 'name'               : fields.char    ('Fiscal Year', size =16, readonly=True)
        , 'fiscalyear_id'      : fields.many2one('account.fiscalyear' , 'Fiscal Year',readonly=True)
        , 'debit'              : fields.float   ('Debit', digits_compute=dp.get_precision('Account'),           readonly=True)
        , 'credit'             : fields.float   ('Credit', digits_compute=dp.get_precision('Account'),          readonly=True)
        , 'balance'            : fields.float   ('Balance', digits_compute=dp.get_precision('Account'),         readonly=True)
        , 'opening_balance'    : fields.float   ('Opening Balance', digits_compute=dp.get_precision('Account'), readonly=True)
        , 'date_start'         : fields.date    ('Date Start',readonly=True)
        , 'date_stop'          : fields.date    ('Date Stop' ,readonly=True)
#        , 'sum_fy_period_ids'  : fields.one2many('account.account_fy_period_sum','sum_fy_period_id','Fiscal Year Period Sum')
        , 'sum_fy_period_ids'  : one2many_periods('account.account_fy_period_sum','id','Fiscal Year Period Sum', readonly=True)
        , 'sum_fy_period_delta_ids' : one2many_per_delta('account.account.period.sum.delta','id','Fiscal Year Period Delta', readonly=True)
        , 'code'               : fields.related ('account_id','code',type='char', size=8,string='Code')
#        , 'closing_text_ids'   : one2many_periods('account.closing.text','id','Closing Text', readonly=True, )
        }
    _order = 'name desc'

    def init(self, cr):
        cr.execute("""
DROP SEQUENCE IF EXISTS account_account_fiscalyear_sum_id_seq CASCADE;
CREATE SEQUENCE account_account_fiscalyear_sum_id_seq;
DROP VIEW IF EXISTS account_account_fiscalyear_sum CASCADE;
create or replace view account_account_fiscalyear_sum as
  select
      --nextval('account_account_fiscalyear_sum_id_seq'::regclass) as id,
      min(s.id) as id,
      s.company_id,
      account_id,
      to_char(y.date_stop,'YYYY') || case when to_char(y.date_stop,'MM')  != '12'
                                     then  '-'||to_char(y.date_stop,'MM')
                                      else '' end as name,
      y.id as fiscalyear_id,
      sum(case when s.name like '%00' then 0 else debit end) as debit,
      sum(case when s.name like '%00' then 0 else credit end) as credit,
      sum(debit) - sum(credit) as balance,
      sum(case when s.name like '%00' then debit - credit else 0 end) as opening_balance,
      y.date_start,
      y.date_stop
    from
      account_account_period_sum s,
      account_period p,
      account_fiscalyear y
    where
      p.id = s.period_id
      and y.id = p.fiscalyear_id
    group by
      s.company_id,
      --sum_fy_period_id,
      s.account_id,
      y.id,
      to_char(y.date_stop,'YYYY') || case when to_char(y.date_stop,'MM')  != '12'
                                     then  '-'||to_char(y.date_stop,'MM')
                                     else '' end            ,
      y.date_start,
      y.date_stop;
""")
account_fiscalyear_sum()

class account_account_with_postings(osv.osv):
    _name        = "account.account_with_postings"
    _description = "Accounts with Postings"
    _auto        = False
    _columns     = \
        { 'code'              : fields.char     ('Code', size=16, readonly=True)
        , 'name'              : fields.char     ('Name', size=128, readonly=True)
        , 'company_id'        : fields.many2one ('res.company', 'Company', required=True)
        , 'shortcut'          : fields.char     ('Shortcut', size=12,readonly=True)
        , 'currency_id'       : fields.many2one ('res.currency' , 'Currency',readonly=True)
        , 'note'              : fields.text     ('Note', readonly=True)
        , 'user_type'         : fields.many2one ('account.account.type', 'Account Type',readonly=True)
        , 'reconcile'         : fields.boolean  ('Reconcile', readonly=True)
        , 'sum_period_ids'    : fields.one2many ('account.account_period_sum','account_id','Sum Periods')
        , 'sum_fy_period_ids' : fields.one2many ('account.account_fy_period_sum','account_id','Sum Fiscal Year Periods')
        , 'sum_fiscalyear_ids': fields.one2many ('account.account_fiscalyear_sum','account_id','Sum Fiscal Years')
        }
    _order = 'code, name'

    def init(self, cr):
        drop_view_if_exists(cr, "account_account_with_postings")
        cr.execute("""
create or replace view account_account_with_postings as
  select
      a.id,
      a.code,
      a.name,
      a.company_id,
      a.shortcut,
      a.currency_id,
      a.note,
      a.user_type,
      a.reconcile
    from account_account a
    where exists (select 'x' from account_account_period_sum where account_id = a.id and company_id = a.company_id);
""")
account_account_with_postings()
#
# sum_period_id must be a get_id (account, period) to link move_lines to periods
#
class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _columns = \
        { 'account_period_sum_id': fields.many2one('account.account_period_sum', 'Period Sum', select=1)}
account_move_line()



class account_account_period_sum_cur_prev(osv.osv):
    _name        = "account.account.period.sum.cur.prev"
    _description = "Account Period Sum current previous"
    _auto        = False
    _columns     = \
        { 'name'          : fields.char    ('Period', size=16       ,readonly=True)
        , 'company_id'    : fields.many2one('res.company', 'Company', required=True)
        , 'account_id'    : fields.many2one('account.account', 'Account',readonly=True)
        , 'period_id'     : fields.many2one('account.period' , 'Period' ,readonly=True)
        , 'date_start'    : fields.date    ('Date Start' ,readonly=True)
        , 'fiscalyear_id' : fields.many2one('account.fiscalyear' , 'Fiscal Year' ,readonly=True)
        , 'balance_curr'  : fields.float   ('Balance Current Period', digits_compute=dp.get_precision('Account'),readonly=True)
        , 'balance_prev'  : fields.float   ('Balance Current Period', digits_compute=dp.get_precision('Account'),readonly=True)
#        , 'balance_cumulative' : fields.float   ('Balance cumulativ', digits_compute=dp.get_precision('Account'),readonly=True)
        }

    def init(self, cr):
        drop_view_if_exists(cr, "account_account_period_sum_delta") # ???
        drop_view_if_exists(cr, "account_account_period_sum_cur_prev")
        cr.execute("""
  create or replace view account_account_period_sum_cur_prev as
    select
        c.id*2 as id,
        c.company_id,
        account_id,
        p.id as period_id,
        p.fiscalyear_id,
        case when c.name like '%00' then '00'  else p.code end as name,
        c.debit-c.credit as balance_curr ,0 as balance_prev,
        case when c.name like '%00' then p.date_start -1 else p.date_start end as date_start
      from
        account_period p left outer join account_account_period_sum c on (c.period_id = p.id)
  union
    select
        c.id*2 -1 as id,
        c.company_id,
        account_id,p.id as period_id,
        p.fiscalyear_id,
        case when c.name like '%00' then '00'  else p.code end as name,
        0 as balance_curr,
        c.debit-c.credit  as balance_prev,
        case when c.name like '%00' then p.date_start -1 else p.date_start end as date_start
      from
        account_period p left outer join account_account_period_sum c on (c.period_id = p.prev_fy_period);
  """)
account_account_period_sum_cur_prev()

class account_account_period_sum_delta(osv.osv):
    _name        = "account.account.period.sum.delta"
    _logger      = logging.getLogger(_name)
    _description = "Account Period Sum Delta"
    _auto        = False

    def __balance_cum(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        """ compute the balance cum  for the provided
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
        mapping = \
            { 'balance_curr_cum': "SUM(p.balance_curr)  as balance_curr_cum"
            , 'balance_prev_cum': "SUM(p.balance_prev)  as balance_prev_cum"
            , 'balance_diff_cum': "SUM(p.balance_curr) - SUM(p.balance_prev) as balance_diff_cum "
            , 'balance_diff_pro_cum': "case when SUM(p.balance_prev) != 0 \
                                          then ((SUM(p.balance_curr) / SUM(p.balance_prev)) -1 ) * 100 \
                                          else null end as balance_diff_pro_cum "
            }

        params = 0
        periods = {}
        res = {}

        for line1 in self.browse(cr, uid, ids, context=context):
            account_id = line1.account_id.id
            fiscalyear_id = line1.fiscalyear_id.id
        period_sum_delta_obj = self.pool.get('account.account.period.sum.delta')
        lines = period_sum_delta_obj.search(cr, uid, [('account_id','=',account_id),('fiscalyear_id','=',fiscalyear_id)], context=context)
        self._logger.debug('lines `%s` `%s`', line1.id, lines)
        filters = " AND l.id in (%s)" %  (','.join(map(str,lines)) )
        request = ("SELECT l.id as id, l.name,  " +
                       ', '.join(map(mapping.__getitem__, field_names)) +
                       " FROM account_account_period_sum_delta l, account_account_period_sum_delta p"
                       " WHERE l.fiscalyear_id = " + str(fiscalyear_id) +
                       "   AND l.account_id = " + str(account_id) +
                       "   AND p.fiscalyear_id = l.fiscalyear_id "
                       "   AND p.account_id = l.account_id "
                       "   AND p.date_start <= l.date_start "
                            + filters +
                       " GROUP BY l.id,l.name  "
                       " ORDER by l.name")

        self._logger.debug('request `%s`', request)
        #params = (tuple(period_ids),) #+ query_params
        #params = (','.join(map(str,period_ids)) )
        cr.execute(request)

        for res in cr.dictfetchall():
            self._logger.debug('res `%s`', res)
            for k, v in res.iteritems():
                if k == 'id':
                    k1 = k
                    v1 = v
            del res[k1]
            periods[v1] = res
        self._logger.debug('periods `%s`', periods)
        return periods

    class one2many_movelines (fields.one2many):
        #_logger      = logging.getLogger(_name)
        def get (self, cr, obj, ids, name, user=None, offset=0, context=None, values={}):
            res = {}
            for id in ids :
                res[id] = []
                print "ID",id
                per = obj.pool.get('account.account.period.sum.delta').browse(cr, user, id, context=context)
                ids2 = obj.pool.get (self._obj).search \
                    ( cr
                    , user
                    , [ ('company_id', '=', per.company_id.id)
                      , ('account_id', '=', per.account_id.id)
                      , ('period_id', '=', per.period_id.id)
                      ]
                    , limit = self._limit
                    )
                for r in ids2:
                    #self._logger.debug('r_ids2 `%s`', r)
                    res [per.id].append(r)
            return res
        #  set missing
    # end class one2many_periods


    _columns = \
        { 'name'             : fields.char    ('Period', size=16,readonly=True)
        , 'company_id'       : fields.many2one('res.company', 'Company', required=True)
        , 'account_id'       : fields.many2one('account.account', 'Account',readonly=True)
        , 'period_id'        : fields.many2one('account.period' , 'Period' ,readonly=True)
        , 'date_start'       : fields.date    ('Date Start' ,readonly=True)
        , 'fiscalyear_id'    : fields.many2one('account.fiscalyear' , 'Fiscal Year' ,readonly=True)
        , 'balance_curr'     : fields.float   ('Curr Period', digits_compute=dp.get_precision('Account'),readonly=True)
        , 'balance_prev'     : fields.float   ('Prev Period', digits_compute=dp.get_precision('Account'),readonly=True)
        , 'diff'             : fields.float   ('Diff Period', digits_compute=dp.get_precision('Account'),readonly=True)
        , 'diff_pro'         : fields.float   ('Diff Period %', digits=(8,2),readonly=True)
        , 'balance_curr_cum' : fields.function(__balance_cum, digits_compute=dp.get_precision('Account'), method=True, string='Curr Cum', multi='balance_cum',readonly=True)
        , 'balance_prev_cum' : fields.function(__balance_cum, digits_compute=dp.get_precision('Account'), method=True, string='Prev Cum', multi='balance_cum',readonly=True)
        , 'balance_diff_cum' : fields.function(__balance_cum, digits_compute=dp.get_precision('Account'), method=True, string='Diff Cum', multi='balance_cum',readonly=True)
        , 'balance_diff_pro_cum' : fields.function(__balance_cum, digits_compute=dp.get_precision('Account'), method=True, string='Diff Cum %', multi='balance_cum',readonly=True)
        , 'move_line_ids'    : one2many_movelines('account.move.line', 'id','Account Moves',readonly=True)
        }
    #_order = 'name'

    def init(self, cr):
        drop_view_if_exists(cr, "account_account_period_sum_delta")
        cr.execute("""
  create or replace view account_account_period_sum_delta as
    select
        min(id) as id,
        company_id,account_id,
        name,period_id,
        date_start,
        fiscalyear_id,
        sum(balance_curr) as balance_curr,
        sum(balance_prev) as balance_prev,
        sum(balance_curr) - sum(balance_prev) as diff,
        case when sum(balance_prev) != 0 then ((sum(balance_curr) / sum(balance_prev)) -1)*100 else 0.0 end as diff_pro
      from account_account_period_sum_cur_prev
      group by company_id,account_id, name, period_id,fiscalyear_id,date_start
      having company_id > 0;
  """)
account_account_period_sum_delta()
