# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 2010-10-22 ferdinand: lines to pay must have partner_id
#
##############################################################################
import wizard
import pooler
from tools.misc import UpdateableStr
import time

class wizard_payment_order(wizard.interface):
    """
    Create payment lines corresponding to the account move line
    to pay according to the date provided by the user and the mode-type payment of the order.
    Hypothesis:
    - Small number of non-reconciled move line , payment mode and bank account type,
    - Big number of partner and bank account.

    If a type is given, unsuitable account move lines are ignored.
    """
    form_search  = UpdateableStr()
    field_search = \
        { 'entries': 
            { 'string'   : 'Entries'
            , 'type'     : 'many2many'
            , 'relation' : 'account.move.line'
            }
        , 'communication2': 
            { 'string' :'Communication 2'
            , 'type'   :'char'
            , 'size'   : 64
            , 'help'   :'The successor message of payment communication.'
            }
        }
    
    field_duedate = \
        {'duedate' :
            { 'string'   : 'Due Date'
            , 'type'     : 'date'
            , 'required' : True
            }
        , 'amount' :
            { 'string'   : 'Amount'
            , 'type'     : 'float'
            , 'help'     : 'Next step will automatically select payments up to this amount.'
            }
        , 'balance_filter' :
            { 'string'   : 'Only partners with total liability'
            , 'type'     : 'boolean'
            , 'default'  : lambda *a: True
            , 'help'     : 'Will select only partners with a debit-credit < 0 regardless of due date.'
            }
        , 'min_balance' :
            { 'string'   : 'Minimum Total Amount Due'
            , 'type'     : 'float'
            , 'help'     : 'Will select only partners with total payment balance greater than this amount.'
            }
        }
    form_duedate='''<?xml version="1.0" encoding="utf-8"?>
<form string="Search Payment lines" col="2">
  <field name="duedate" />
  <field name="amount" />
  <field name="balance_filter" />
  <field name="min_balance"/>
</form>'''
    
    def _get_defaults(self, cr, uid, data, context=None):
        pool = pooler.get_pool(cr.dbname)
        order_obj = pool.get('payment.order')
        order = order_obj.browse(cr, uid, data['id'], context=context)
        field_duedate['duedate']['default'] = \
            lambda *a: time.strftime('%Y-%m-%d')
        field_duedate['min_balance']['default'] = \
            lambda *a: order.mode.type.amount_partner_min if order.mode and order.mode.type else 0.0
        return {}
    # end def _get_defaults
    
    def _search_entries(self, cr, uid, data, context=None):
        search_due_date = data['form']['duedate']
        amount          = data['form']['amount']
        balance_filter  = data['form']['balance_filter']
        min_balance     = data['form']['min_balance']
    
        pool      = pooler.get_pool(cr.dbname)
        order_obj = pool.get('payment.order')
        line_obj  = pool.get('account.move.line')
    
        payment = order_obj.browse(cr, uid, data['id'], context=context)
        ctx = ''
        if payment.mode:
            ctx = '''context="{'journal_id': %d}"''' % payment.mode.journal.id
    
        # Search for move line to pay:
        domain = \
            [ ('reconcile_id', '=', False)
            , ('account_id.type', '=', payment.type)
            , ('amount_to_pay', '<>', 0)
            , ('partner_id', '!=', ''  )
            , '|'
            , ('date_maturity', '<', search_due_date)
            , ('date_maturity', '=', False)
            ]
        #fg 20100809 - deaktiviert - no data found ???
        #if payment.mode:
        #    domain = [('payment_type','=',payment.mode.type.id)] + domain
        line_ids = line_obj.search(cr, uid, domain, order='date_maturity', context=context)
        ids = []
        for line in line_obj.browse(cr, uid, line_ids) :
            if line.partner_id.payment_block : continue
            if line.invoice.payment_block    : continue
            if line.partner_id.payment_obey_balance and balance_filter and not ((line.partner_id.debit - line.partner_id.credit) >= min_balance) : 
                continue
            ids.append(line.id)
        line_ids = ids
        field_search['entries']['domain'] = "[('id','in',%s)]" % line_ids
        form_search.string = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Populate Payment">
  <separator string="click New/Add icon to search for unreconciled moves" colspan="4"/>
  <field name="entries" colspan="4" height="300" width="800" nolabel="1" %s/>
  <separator string="Extra message of payment communication" colspan="4"/>
  <field name="communication2" colspan="4"/>
</form>''' % ctx
    
        selected_ids = []
        if amount:
            if payment.mode and payment.mode.require_bank_account:
                line2bank = line_obj.line2bank(cr, uid, line_ids, payment.mode.id, context)
            else:
                line2bank = None
            # If user specified an amount, search what moves match the criteria taking into account
            # if payment mode allows bank account to be null.
            for line in line_obj.browse(cr, uid, line_ids, context):
                if abs(line.amount_to_pay) <= amount:
                    if line2bank and not line2bank.get(line.id):
                        continue
                    amount -= abs(line.amount_to_pay)
                    selected_ids.append(line.id)
            return {'entries': selected_ids}
        else:
            return {'entries': line_ids}
    # end def _search_entries
    
    def _create_payment(self, cr, uid, data, context=None):
        line_ids = data['form']['entries'][0][2]
        if not line_ids: return {}
    
        pool         = pooler.get_pool(cr.dbname)
        order_obj    = pool.get('payment.order')
        line_obj     = pool.get('account.move.line')
        user_obj     = pool.get('res.users')
        currency_obj = pool.get('res.currency')
        payment_obj  = pool.get('payment.line')
    
        payment = order_obj.browse(cr, uid, data['id'], context=context)
        t = payment.mode and payment.mode.type.id or None
        line2bank = line_obj.line2bank(cr, uid, line_ids, t, context)
       
        # not all move lines have a currency set so we do a best guess
        user = user_obj.browse(cr, uid, uid)
        if user.company_id:
            currency_id = user.company_id.currency_id.id
        else:
            currency_id = currency_obj.search(cr, uid, [('rate','=',1.0)])[0]
    
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            if payment.date_prefered == "now": #no payment date => immediate payment
                date_to_pay = False
            elif payment.date_prefered == 'due':
                date_to_pay = line.date_maturity
            elif payment.date_prefered == 'fixed':
                date_to_pay = payment.date_planned
    
        # FIXME performance issue here 200 records 75 seconds !!!
            payment_obj.create \
                (cr, uid
                , { 'move_line_id'    : line.id
                  , 'amount_currency' : line.amount_to_pay
                  , 'bank_id'         : line2bank.get(line.id)
                  , 'order_id'        : payment.id
                  , 'partner_id'      : line.partner_id and line.partner_id.id or False
                  , 'communication'   : (line.ref and line.name!='/' and line.ref+'. '+line.name) or line.ref or line.name or '/'
                  , 'communication2'  : data['form']['communication2']
                  , 'date'            : date_to_pay
                  , 'currency'        : line.invoice.currency_id and line.invoice.currency_id.id or currency_id
                  , 'account_id'      : line.account_id.id
                  }
                , context=context
                )
        return {}
    # end def _create_payment

    states = \
        { 'init': 
            { 'actions': [_get_defaults]
            , 'result': 
                { 'type'   : 'form'
                , 'arch'   : form_duedate
                , 'fields' : field_duedate
                , 'state'  :
                    [ ('end','_Cancel')
                    , ('search','_Search', '', True)
                    ]
                }
            }
        , 'search': 
            { 'actions': [_search_entries]
            , 'result': 
                { 'type'   : 'form'
                , 'arch'   : form_search
                , 'fields' : field_search
                , 'state'  : 
                    [ ('end','_Cancel')
                    , ('create','_Add to payment order', '', True)
                    ]
                }
            }
        , 'create': 
            { 'actions': []
            , 'result': 
                { 'type'   : 'action'
                , 'action' : _create_payment
                , 'state'  : 'end'
                }
            }
        }

wizard_payment_order('populate_payment_ext')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: