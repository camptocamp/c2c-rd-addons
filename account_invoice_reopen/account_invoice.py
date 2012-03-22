# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

# FIXME remove logger lines or change to debug
 
from osv import fields, osv


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_reopen(self, cr, uid, ids, *args):
        context = {} # TODO: Use context from arguments
        account_move_obj = self.pool.get('account.move')
        invoices = self.read(cr, uid, ids, ['move_id', 'payment_ids'])
        move_ids = [] # ones that we will need to update
        for i in invoices:
            if i['move_id']:
                move_ids.append(i['move_id'][0])
            if i['payment_ids']:
                account_move_line_obj = self.pool.get('account.move.line')
                pay_ids = account_move_line_obj.browse(cr, uid, i['payment_ids'])
                for move_line in pay_ids:
                    if move_line.reconcile_id or (move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids):
                        raise osv.except_osv(_('Error !'), _('You can not reopen an invoice which is partially paid! You need to unreconcile related payment entries first!'))

        # First, set the invoices as cancelled and detach the move ids
        self.write(cr, uid, ids, {'state':'draft'})
        if move_ids:
            # second, invalidate the move(s)
            # account_move_obj.button_cancel(cr, uid, move_ids, context=context)
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            account_move_obj.write(cr, uid, move_ids, {'state':'draft'})
        self._log_event(cr, uid, ids, -1.0, 'Reopened Invoice')
        return True

    def action_move_create(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('account.move')
        move_ids = [] # ones that we will need to update
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.move_id:
                move_ids.append(inv.move_id.id)
            else:
                super(account_invoice, self).action_move_create(cr, uid, ids, context)
        if move_ids:
            move_obj.write(cr, uid, move_ids, {'state':'posted'})

    def action_number(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.internal_number:
                super(account_invoice, self).action_number(cr, uid, ids, context)


account_invoice()
