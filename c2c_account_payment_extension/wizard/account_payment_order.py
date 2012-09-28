# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    08-JUN-2012 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# 59 Temple Place - Suite 330, Boston, MA  02111-1.17, USA.
#
###############################################
from osv import osv, fields

class payment_order_create(osv.osv_memory):
    _inherit     = 'payment.order.create'
    _columns     = \
        { 'balance_filter' : fields.boolean
            ( 'Only partners with total liability'
            , help='Will select only partners with a debit-credit < 0 regardless of due date.'
            )
        , 'min_balance'    : fields.float 
            ( 'Minimum Total Amount Due'
            , help="Will select only partners with total payment balance greater than this amount."
            )
        }
    _defaults    = \
        { 'balance_filter' : lambda *a: True
        , 'min_balance'    : lambda *a: 100.0
        }

    def search_entries(self, cr, uid, ids, context=None):
        if context is None : context = {}
        order_obj = self.pool.get('payment.order')
        line_obj  = self.pool.get('account.move.line')
        invoice_obj  = self.pool.get('account.invoice')
        mod_obj   = self.pool.get('ir.model.data')
        obj       = self.browse(cr, uid, ids, context=context)[0]
        payment   = order_obj.browse(cr, uid, context['active_id'], context=context)
        domain    = \
            [ ('reconcile_id', '=', False)
            , ('account_id.type', '=', 'payable')
            # , ('amount_to_pay', '>', 0) # see later in if statements
            ]
        domain   += \
            [ '|'
            , ('date_maturity', '<=', obj.duedate)
            , ('date_maturity', '=', False)
            ]
        ids = line_obj.search(cr, uid, domain, context=context)
        line_ids = []
        for line in line_obj.browse(cr, uid, ids) :
            if line.invoice.payment_block : continue
            if line.move_id.state == 'draft' : continue # FGF no idea why this fails
            if line.partner_id.payment_block : continue
            if (line.partner_id.payment_obey_balance 
                and obj.balance_filter 
                and not ((line.partner_id.debit - line.partner_id.credit) >= obj.min_balance)) : continue
            # FIXME - GKö - currently no bank account invoice - hence records are not selected
            # manual creation puts bank account into invoice
            if (line.invoice and not line.invoice.partner_bank_id):
                if not line.invoice.partner_id.bank_ids and payment.mode.require_bank_account : 
                    continue
                else:
                    invoice_obj.write(cr, uid, line.invoice.id, {'partner_bank_id' : line.invoice.partner_id.bank_ids[0].id })
            line_ids.append(line.id)
        context.update({'line_ids': line_ids})
        model_data_ids = mod_obj.search \
            ( cr, uid
            , [('model', '=', 'ir.ui.view'), ('name', '=', 'view_create_payment_order_lines')]
            , context=context
            )
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        return \
            { 'name'      : ('Entry Lines')
            , 'context'   : context
            , 'view_type' : 'form'
            , 'view_mode' : 'form'
            , 'res_model' : 'payment.order.create'
            , 'views'     : [(resource_id,'form')]
            , 'type'      : 'ir.actions.act_window'
            , 'target'    : 'new'
            }
payment_order_create()
