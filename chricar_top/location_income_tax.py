# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-07-09 16:17:22+02
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
from osv import fields,osv
import decimal_precision as dp

class location_income_tax(osv.osv):
    _name = "location.income.tax"
    _description = "Holds data of yearly income statement"
    _columns = {
        'location_id'        : fields.many2one('stock.location','Location', select=True, required=True),
        'fiscalyear_id'      : fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
        'account_id'         : fields.many2one('account.account', 'Account', required=True, ondelete="cascade",domain="[('type', '!=', 'view')]"),
        'company_id'         : fields.related('account_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'amount'             : fields.float('Amount', digits_compute=dp.get_precision('Account'),required=True),
        'note'               : fields.text('Note'),
}

    def _tax_2_move(self, cr, uid, ids, name, args, context=None):
        fy_obj = self.pool.get('account.fiscalyear')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        
        code_jour = _('IM')
        arg_jour = ('code','=', code_jour)
        journal_id = journal_obj.search(cr, uid, [arg_jour], context)
        if not journal_id:
            raise osv.except_osv(_('Error'), _('Please create a journal with code %s  !') % (code_jour))
            
        arg_acc = ('code','=','RER')
        account_id = account_obj.search(cr, uid, [arg_acc], context)
        if not account_id:
            raise osv.except_osv(_('Error'), _('Please create a balance account with code "RER"  (Real Estate Result) !'))    
            
        
        for rec in self.browse(cr, uid, ids, context=context):
            per_ids = period_obj.search(cr, uid, [('fiscalyear_id','=', rec.fiscalyear_id.id),('special','=',False)])
            p = len(per_ids)
            amount_p = rec.amount / float(p)
            ref = '-'.join(code_jour, rec.period_id.code)
            args_move = [('journal_id', '=', journal_id),('period_id', '=', rec.period_id.id), ('ref', '=', ref)]
            move_id = move_obj.search(cr, uid, args_move, context)
            
            if not move_id:
                date = per.date_stop
                vals = {
                    'name'       : '/',
                    'ref'        : ref,
                    'journal_id' : journal_id, 
                    'state'      : 'draft',
                    'date'       : date,
                    'period_id'  : per.id,
                    }
                
                move_id = move_obj.create(cr, uid, vals,  context )
            else:
                for move in move_obj.browse(cr, uid, [move_id], context):
                    vals = {
                        'name'       : move.name,
                        'ref'        : move.ref,
                        'journal_id' : move.journal_id.id,
                        'state'      : move.state,
                        'date'       : move.date,
                        'period_id'  : move.period_id.id,
                        }
            
            debit = credit = 0
            if amount_p > 0:
                debit = amount_p
            else:
                credit = -amount_p
                
            v = {
                'debit' : debit,
                'credit' : credit,
                'move_id' : move_id,
                'account_id' : rec.account_id.id,
                }
            v.update(vals) 
            
            move_line_obj.create(cr, uid, v, context )
            
            v = {
                'debit' : credit,
                'credit' : debit,
                'move_id' : move_id,
                'account_id' : account_id
                }
            v.update(vals)
            move_line_obj.create(cr, uid, v, context )
                
            

location_income_tax()

class stock_location(osv.osv):
    _inherit = "stock.location"

    def _get_tax_res(self, cr, uid, ids, name, args, context=None):
        res = {}
        data = {}
        for loc in self.browse(cr, uid, ids, context=context):
            values = {}

            sql = """
            select distinct a.code,a.name as account,a.company_id ,t.name
                from location_income_tax l,
                    account_account a,
                    account_account_type t
                where location_id = %s
                and a.id = l.account_id
                and t.id = user_type
                order by t.name desc, a.code
                """ % loc.id
            cr.execute(sql)
            accounts = cr.fetchall()
            for ac in accounts:
                values[ac[0]] = {}


            sql = """
            select distinct f.code as fy
                from location_income_tax l,
                    account_fiscalyear f
                where location_id = %s
                and f.id = l.fiscalyear_id
                order by f.code
                """ % loc.id
            cr.execute(sql)
            fiscal_years = cr.fetchall()
            for fy in fiscal_years:
                for ac in accounts:
                    values[ac[0]][fy[0]]={}

            sql = """
            select a.code as account, f.code as year , sum(amount) as amount
                from location_income_tax l,
                    account_fiscalyear f,
                    account_account a
                where location_id = %s
                and f.id = l.fiscalyear_id
                and a.id = l.account_id
                group by a.code, f.code 
                order by a.code, f.code
            """ % loc.id
            cr.execute(sql)
            vals = cr.fetchall()
            for val in vals:
                values[val[0]][val[1]] = val[2]

            res[loc.id] = (accounts, fiscal_years, values)
        return res


    _columns = {
        'income_tax_move_ids'  : fields.one2many('location.income.tax','location_id','Income Tax Statement'),
        'tax_res'  : fields.function(_get_tax_res, method=True, type='dict', string='Tax Result Dict',),
}

stock_location()
