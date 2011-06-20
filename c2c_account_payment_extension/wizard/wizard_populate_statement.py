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
#
##############################################################################
import wizard
import pooler
    
class PopulateStatement(wizard.interface):
    """Populate the current statement with selected payment lines"""

    field_search = \
        {'lines' : 
            {'string'   : 'Payment Lines'
            , 'type'    : 'many2many'
            , 'relation': 'payment.line'
            }
        }
    form_search = '''<?xml version="1.0"?>
<form string="Populate Statement (click NEW icon to search for unreconciled moves)">
    <field name="lines" colspan="4" height="300" width="800" nolabel="1""/>
</form>'''
    
    def _search_entries(self, cr, uid, data, context=None):
        pool          = pooler.get_pool(cr.dbname)
        line_obj      = pool.get('payment.line')
        statement_obj = pool.get('account.bank.statement')
    
        statement = statement_obj.browse(cr, uid, data['id'], context=context)
    
        domain = \
            [ ('move_line_id.reconcile_id', '=', False)
            , ('order_id.mode.journal.id', '=', statement.journal_id.id)
            , '|'
            , ('move_line_id.reconcile_id', '=', False)
            , ('order_id.mode', '=', False)
            ]
        line_ids = line_obj.search(cr, uid, domain)
        field_search['lines']['domain'] = "[('id','in',%s)]" % list(set(line_ids))
        return {}
    # end def _search_entries
    
    def _populate_statement(self, cr, uid, data, context=None):
        line_ids = data['form']['lines'][0][2]
        if not line_ids:
            return {}
        if context is None:
            context = {}
    
        pool          = pooler.get_pool(cr.dbname)
        line_obj      = pool.get('payment.line')
        statement_obj = pool.get('account.bank.statement')
        statement_line_obj = pool.get('account.bank.statement.line')
        currency_obj  = pool.get('res.currency')
        statement_reconcile_obj = pool.get('account.bank.statement.reconcile')
    
        statement = statement_obj.browse(cr, uid, data['id'], context=context)
    
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            ctx = context.copy()
            ctx['date'] = line.ml_maturity_date
            amount = currency_obj.compute \
                (cr, uid, line.currency.id, statement.currency.id, line.amount_currency, context=ctx)
            reconcile_id = statement_reconcile_obj.create \
                ( cr, uid
                , {'line_ids': [(6, 0, [line.move_line_id.id])]}
                , context=context
                )
            statement_line_obj.create \
                (cr, uid
                , { 'name'         : (line.order_id.reference or '?') +'. '+ line.name # Typically: type=='payable' => amount>0  type=='receivable' => amount<0
                  , 'amount'       : -amount
                  , 'type'         : line.order_id.type=='payable' and 'supplier' or 'customer'
                  , 'partner_id'   : line.partner_id.id
                  , 'account_id'   : line.move_line_id.account_id.id
                  , 'statement_id' : statement.id
                  , 'ref'          : line.communication
                  , 'reconcile_id' : reconcile_id
                  }
                , context=context
                )
        return {}
    # end def _populate_statement
    
    states = \
        { 'init': 
            { 'actions': [_search_entries]
            , 'result': 
                { 'type'   : 'form'
                , 'arch'   : form_search
                , 'fields' : field_search
                , 'state'  : 
                    [ ('end', '_Cancel')
                    , ('add', '_Add', '', True)
                    ]
                }
            }
        , 'add': 
            { 'actions': []
            , 'result': 
                { 'type'   : 'action'
                , 'action' : _populate_statement
                , 'state'  : 'end'
                }
            }
        }

PopulateStatement('populate_statement_ext')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: