# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
from openerp.osv import fields,osv
from openerp.tools.translate import _
import logging
# ************************************
# account_account
# ************************************

class account_account(osv.osv):
    _inherit = "account.account"

    def get_analytic(self, cr, uid, ids, account_id):
        result = {}
        if account_id:
            account = self.browse(cr, uid,  account_id)
            if account.analytic_account_id:
                analytic_id = account.analytic_account_id.id
                # due to inconsistent naming we return both variables
                result = {'value': {
                'analytic_account_id': analytic_id,
                'account_analytic_id': analytic_id,
                }}
        return result



    _columns = {
     'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', select=True,
          help="provide Analytic Account only for default and fixed"),
     'account_analytic_usage': fields.selection([
            ('fixed','Fixed'),
            ('mandatory','Mandatory'),
            ('optional','Optional'),
            ('none','Not allowed'),
            ], 'Analytic Account Usage', help="""This type is used to differenciate types with
special effects in Open ERP:
for P&L accounts
* fixed: will be used and user can not change it
* mandatory: user must supply analytic account
for balance accounts
* optional: user may supply analytic account
* none: no analytic account allowed""",
            ) ,
    }

    def _analytic_account_type(self, cr, uid, ids=False, context=None):

        if ids:
            account = self.browse(cr, uid, ids)
            #if account.account_analytic_usage:
            #    return
            if account.type == 'other' and account.user_type and account.user_type.close_method == 'none':
            # P&L
                return 'mandatory'
            if account.type == 'view':
                return 'none'
            else:
                return

    _defaults = {
      'account_analytic_usage' : _analytic_account_type,
    }

    def onchange_types(self, cr, uid, ids, acc_type, user_type):

        if account.type == 'view' :
            return {'value':{'account_analytic_usage': 'none'}}
        if account.type == 'other' and user_type and account.user_type.close_method == 'none':
            return {'value':{'account_analytic_usage': 'mandatory'}}
        return {}


#
# checks for account_account
#
    def _check_analytic_account_usage(self, cr, uid, ids):
        account = self.browse(cr, uid, ids[0])
        if account.type != 'view' and account.user_type.close_method == 'none' and account.account_analytic_usage not in ('mandatory','fixed'):
            return False
        return True

    def _check_analytic_account_id(self, cr, uid, ids):
        account = self.browse(cr, uid, ids[0])
        if account.type != 'view':
            if account.account_analytic_usage in ('fixed') and not account.analytic_account_id :
                return False
        # FIXME - do we need the following check? -
        #    if account.analytic_account_id and account.account_analytic_usage not in ('fixed','mandatory'):
        #       return False
        return True

    def _check_analytic_account_view(self, cr, uid, ids):
        account = self.browse(cr, uid, ids[0])
        if account.type == 'view' and account.account_analytic_usage != ('none'):
            return False
        return True


    _constraints = [
        (_check_analytic_account_usage,
            'You must assign mandatory or fixed analytic account usage for P&L accounts', ['account_analytic_usage']),
        (_check_analytic_account_view,
            'For views usage must be: Not Allowed', ['analytic_account_id']),
        (_check_analytic_account_id,
            'You must define an analytic account for fixed, else nothing', ['analytic_account_id']),
        ]



    def init(self, cr):
        # We set some resonable values
        # P & L accounts - mandatory
        # other no analytic account
        cr.execute("""
           update account_account
             set account_analytic_usage = (
                  select distinct
                     case when close_method = 'none' and code != 'view' then 'mandatory' when code = 'view'  then null else 'none' end
                    from account_account_type aat
                   where aat.id = user_type)
            where account_analytic_usage is null;
        """)


    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        if not vals.get('account_analytic_usage'):
            usage = 'none'
            if vals.get('type') == 'other' :
                user_type_obj =  self.pool.get('account.account.type').search(cr, uid,[('id','=', vals.get('user_type'))])
                for user_type in self.pool.get('account.account.type').browse(cr, uid, user_type_obj):
                    if user_type.close_method == 'none':
                        usage = 'mandatory'
            vals.update({'account_analytic_usage': usage})

        res = super(account_account, self).create(cr, uid, vals, context)
        return res

    # For account_move_line, invoice_line, banke_statement_line ....
    def add_default(self, cr, uid, ids, vals, context=None):
        res=[]
        if not vals.get('analytic_account_id',False) and  vals.get('account_id',False):
            account_id = vals.get('account_id',False)
            accounts =  self.pool.get('account.account').search(cr, uid, [('id','=',account_id)] )
            for account_obj in self.pool.get('account.account').browse(cr, uid, accounts):
                if account_obj.account_analytic_usage in ['mandatory','fixed'] and account_obj.analytic_account_id:
                    vals['analytic_account_id'] = account_obj.analytic_account_id.id
                    res.append(vals)
                    for res_account in self.browse(cr, uid, ids):
                        res_account = { 'value' : {'analytic_account_id' : account_obj.analytic_account_id.id}}
                        res.append(res_account)
        return res

    def _check_analytic_account_view(self, cr, uid, ids):
        account = self.browse(cr, uid, ids[0])
        if account.type == 'view' and account.account_analytic_usage != ('none'):
            return False
        return True

#
# checks for move lines
#

    def check_analytic_account_exists(self, cr, uid, ids, account_id, analytic_account_id ):
        if account_id:
            account = self.browse(cr, uid,  account_id)
            if account.account_analytic_usage in ('mandatory','fixed') and not analytic_account_id :
                return False
        return True

    def check_analytic_account_fixed(self, cr, uid, ids, account_id, analytic_account_id):

        if account_id:
            account = self.browse(cr, uid,  account_id)
            if analytic_account_id:
                analytic = self.pool.get('account.analytic.account').browse(cr, uid,  analytic_account_id)
                analytic_name = analytic.name
            else:
                analytic_name = _('No analytic account specified')
            if account.account_analytic_usage == 'fixed' and account.analytic_account_id.id != analytic_account_id :
                return False
        return True

    def check_analytic_account_none(self, cr, uid, ids, account_id, analytic_account_id):
        if account_id:
            account = self.browse(cr, uid,  account_id)
            if analytic_account_id and account.account_analytic_usage == 'none':
                return False
        return True

account_account()

# ************************************
# account_move_line
# ************************************
class account_move_line(osv.osv):
    _inherit = "account.move.line"


    def _analytic_account_id(self, cr, uid, ids=False, context=None):
        # FIXME - do not know if this ever will return a valid analytic account
        res = ''
        if ids:
            line = self.browse(cr, uid, ids)
            if not line.analytic_account_id and line.account_id and line.account_id.analytic_account_id:
                res = line.account_id.analytic_account_id.id
        return res

    _columns = {
       # FIXME why readonly ?? FGF 20111231
       #'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True)
    }

    _defaults = {
       'analytic_account_id' :  _analytic_account_id,
    }


    def onchange_account(self, cr, uid, ids, account_id,tax_id, amount, partner_id):

        result = super(account_move_line,self).onchange_account_id( cr, uid, ids, account_id, partner_id)
        if not account_id:
            return {}

        account_obj =  self.pool.get('account.account')
        res = account_obj.get_analytic(cr, uid, ids, account_id)
        if result and res:
            result['value'].update( res['value'])
        elif not result and res:
            result = res

        return result

    def _check_analytic_account_exists(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            if move.move_id.state == 'posted':
                return  account_obj.check_analytic_account_exists(cr,uid,ids,move.account_id.id,move.analytic_account_id.id)
            return True

    def _check_analytic_account_fixed(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            if move.move_id.state == 'posted':
                return  account_obj.check_analytic_account_fixed(cr,uid,ids,move.account_id.id,move.analytic_account_id.id)
            return True

    def _check_analytic_account_none(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            return  account_obj.check_analytic_account_none(cr,uid,ids,move.account_id.id,move.analytic_account_id.id)

    _constraints = [
        (_check_analytic_account_exists,
            'You must assign an analytic account.(move_line) ', ['analytic_account_id']),
        (_check_analytic_account_fixed,
            'You must not alter a fixed analytic account.', ['analytic_account_id']),
        (_check_analytic_account_none,
            'You must not define an analytic account.(accont_move_line)', ['analytic_account_id']),
        ]

    def create(self, cr, uid, vals, context=None, check=True):
        if not vals.get('analytic_account_id') :
            account_id = vals.get('account_id')
            if account_id:
                for account in self.pool.get('account.account').browse(cr, uid, [account_id] , context=context):
                    if account.account_analytic_usage in [ 'fixed', 'mandatory'] and account.analytic_account_id:
                        vals['analytic_account_id'] = account.analytic_account_id.id
        return super(account_move_line, self).create(cr, uid, vals, context=context)

account_move_line()

# ************************************
# Bank stetement line
# ************************************

class account_bank_statement_line(osv.osv):
    _inherit = "account.bank.statement.line"
    _logger = logging.getLogger(__name__)

    def _check_analytic_account_exists(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            return  account_obj.check_analytic_account_exists(cr,uid,ids,move.account_id.id,move.analytic_account_id.id)

    def _check_analytic_account_fixed(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            return  account_obj.check_analytic_account_fixed(cr,uid,ids,move.account_id.id,move.analytic_account_id.id)

    def _check_analytic_account_none(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            return  account_obj.check_analytic_account_none(cr,uid,ids,move.account_id.id,move.analytic_account_id.id)

    _constraints = [
        (_check_analytic_account_exists,
            'You must assign an analytic account.(bank)', ['analytic_account_id']),
        (_check_analytic_account_fixed,
            'You must not alter a fixed analytic account.', ['analytic_account_id']),
        (_check_analytic_account_none,
            'You must not define an analytic account.(bankstatement line)', ['analytic_account_id']),
        ]

    def onchange_account(self, cr, uid, ids, account_id,tax_id, amount, partner_id):
        _logger = logging.getLogger(__name__)

        result = super(account_bank_statement_line,self).onchange_account( cr, uid, ids, account_id,tax_id, amount, partner_id)
        if not account_id:
            return {}

        account_obj =  self.pool.get('account.account')
        res = account_obj.get_analytic(cr, uid, ids, account_id)
        _logger.debug('FGF bank change %s:%s', result, res)

        if result and res:
            result['value'].update( res['value'])
        elif not result and res:
            result = res

        return result


    #def onchange_account_id_analytic(self, cr, uid, ids, account_id, analytic_account_id=False):
    #    #res_account = super(account_bank_statement_line,self).onchange_account(cr, uid, ids, account_id)
    #    res_account = self.onchange_account(cr, uid, ids, account_id)
    #    if account_id:
    #        account_obj = self.pool.get('account.account').browse(cr, uid, account_id)
    #        if (analytic_account_id and account_obj.account_analytic_usage == 'fixed' and analytic_account_id != account_obj.analytic_account_id.id) \
    #              or \
    #              (not analytic_account_id and account_obj.account_analytic_usage in ['fixed']):
    #            analytic_account_id = account_obj.analytic_account_id.id
    #            res_account['value'].update({'analytic_account_id' : analytic_account_id})
    #        if analytic_account_id and account_obj.account_analytic_usage == 'none':
    #            res_account['value'].update({'analytic_account_id' : ''})
    #    return res_account

account_bank_statement_line()


#
# Invoice Line
#
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    _columns = {
       'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True)
    }
    # we need this to fill default analytic for imported invoice lines
    def write(self, cr, uid, ids, vals, context=None):
        if not vals.get('account_analytic_id',False) and  vals.get('account_id',False):
            account_id = vals.get('account_id',False)
            account_obj =  self.pool.get('account.account')
            res = account_obj.get_analytic(cr, uid, ids, account_id)
            vals['account_analytic_id'] = res.get('account_analytic_id',False)

        return super(account_invoice_line, self).write(cr, uid, ids, vals, context)

    def onchange_account(self, cr, uid, ids, product_id, partner_id, inv_type, fiscal_position, account_id, account_analytic_id):
        result = super(account_invoice_line,self).onchange_account_id(cr, uid, ids, product_id, partner_id, inv_type, fiscal_position,account_id)
        if not account_id or account_analytic_id:
            return result
        account_obj =  self.pool.get('account.account')
        res = account_obj.get_analytic(cr, uid, ids, account_id)
        if result and res:
            result['value'].update( res['value'])
        elif not result and res:
            result = res

        return result

    def _check_analytic_account_exists(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            if move.invoice_id.state == 'open':
                return  account_obj.check_analytic_account_exists(cr,uid,ids,move.account_id.id,move.account_analytic_id.id)
            return True

    def _check_analytic_account_fixed(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            if move.invoice_id.state == 'open':
                return  account_obj.check_analytic_account_fixed(cr,uid,ids,move.account_id.id,move.account_analytic_id.id)
            return True

    def _check_analytic_account_none(self, cr, uid, ids):
        for move in self.browse(cr, uid, ids):
            account_obj = self.pool.get('account.account')
            if move.invoice_id.state == 'open':
                return  account_obj.check_analytic_account_none(cr,uid,ids,move.account_id.id,move.account_analytic_id.id)
            return  True

    _constraints = [
        (_check_analytic_account_exists,
            'You must assign an analytic account.(invoiceline)', ['analytic_account_id']),
        (_check_analytic_account_fixed,
            'You must not alter a fixed analytic account.(invoiceline)', ['analytic_account_id']),
        (_check_analytic_account_none,
            'You must not define an analytic account.(invoiceline)', ['analytic_account_id']),
        ]


account_invoice_line()

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _check_analytic_account_exists(self, cr, uid, ids):
        for invoice in self.browse(cr, uid, ids):
            for move in invoice.invoice_line:
                account_obj = self.pool.get('account.account')
                if move.invoice_id.state == 'open':
                    return  account_obj.check_analytic_account_exists(cr,uid,ids,move.account_id.id,move.account_analytic_id.id)
            return True

    def _check_analytic_account_fixed(self, cr, uid, ids):
        for  invoice in self.browse(cr, uid, ids):
            for move in invoice.invoice_line:
                account_obj = self.pool.get('account.account')
                if move.invoice_id.state == 'open':
                    return  account_obj.check_analytic_account_fixed(cr,uid,ids,move.account_id.id,move.account_analytic_id.id)
            return True

    def _check_analytic_account_none(self, cr, uid, ids):
        for  invoice in self.browse(cr, uid, ids):
            for move in invoice.invoice_line:
                account_obj = self.pool.get('account.account')
                if move.invoice_id.state == 'open':
                    return  account_obj.check_analytic_account_none(cr,uid,ids,move.account_id.id,move.account_analytic_id.id)
            return True

    _constraints = [
        (_check_analytic_account_exists,
            'You must assign an analytic account.(invoice)', ['invoice_line']),
        (_check_analytic_account_fixed,
            'You must not alter a fixed analytic account.', ['invoice_line']),
        (_check_analytic_account_none,
            'You must not define an analytic account.', ['invoice_line']),
        ]


account_invoice()

class account_analytic_line(osv.osv):
    _inherit = "account.analytic.line"

    def _get_period(self, cr, uid, ids, name, arg, context):
        result = {}
        for line in self.browse(cr, uid, ids):
            period_id = ''
            if line.move_id and line.move_id.move_id and line.move_id.move_id.period_id:
            #if line.move_id and line.move_id.move_id:
                result[line.id] = line.move_id.move_id.period_id.id
            else:
                period_ids= self.pool.get('account.period').search(cr,uid,[('company_id','=',line.company_id.id),('date_start','<=',line.date),('date_stop','>=',line.date ),('special','!=',True)])
                if len(period_ids):
                    result[line.id] = period_ids[0]

        return result


    _columns = {
        'period_id': fields.function(_get_period, string='Period', method=True, store=True, type='many2one', relation='account.period', select="1")

    }

    def _check_no_view1(self, cr, uid, ids, context=None):
        analytic_lines = self.browse(cr, uid, ids, context=context)
        for line in analytic_lines:
            if line.account_id.type == 'view':
                raise osv.except_osv(_('Error'), _('You cannot post on view account %s %s')% (line.account_id.code,line.account_id.name))

                return False
        return True

    def _check_no_view(self, cr, uid, ids, context=None):
        return True

    _constraints = [
        (_check_no_view1, 'You can not create analytic line on view account.', ['account_id']),
    ]



account_analytic_line()
