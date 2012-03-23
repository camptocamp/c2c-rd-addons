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
from tools.translate import _
import logging
import time




class account_invoice(osv.osv):
    _inherit = "account.invoice"
 
    def _get_state(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)

        res = list(super(account_invoice, self)._columns['state'].selection)
        res.append(('draft_reset','Reset to draft'))
        _logger.info('FGF invoice states  %s' % (res) )

        return res 

    _columns ={
# FIXME the _get_state raises error
#        'state': fields.selection(selection=_get_state, string='State', required=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('draft_reset','Reset to Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Cancelled')
            ],'State', select=True, readonly=True,
            help=' * The \'Draft\' state is used when a user is encoding a new and unconfirmed Invoice. \
            \n* The \'Pro-forma\' when invoice is in Pro-forma state,invoice does not have an invoice number. \
            \n* The \'Open\' state is used when user create invoice,a invoice number is generated.Its in open state till user does not pay invoice. \
            \n* The \'Paid\' state is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
            \n* The \'Cancelled\' state is used when user cancel invoice.'),

    }

    def action_reopen(self, cr, uid, ids, *args):
        context = {} # TODO: Use context from arguments
        account_move_obj = self.pool.get('account.move')
        invoices = self.read(cr, uid, ids, ['move_id', 'payment_ids'])
        move_ids = [] # ones that we will need to update
        for i in invoices:
            if i['move_id']:
                move_ids.append(i['move_id'][0])
                for move in account_move_obj.browse(cr, uid, move_ids):
                    if not move.journal_id.reopen_posted:
                        raise osv.except_osv(_('Error !'), _('You can not reopen invoice of this journal! You need to need to set "Allow Update Posted Entries" first'))
                    
            if i['payment_ids']:
                account_move_line_obj = self.pool.get('account.move.line')
                pay_ids = account_move_line_obj.browse(cr, uid, i['payment_ids'])
                for move_line in pay_ids:
                    if move_line.reconcile_id or (move_line.reconcile_partial_id and move_line.reconcile_partial_id.line_partial_ids):
                        raise osv.except_osv(_('Error !'), _('You can not reopen an invoice which is partially paid! You need to unreconcile related payment entries first!'))

        # First, set the invoices as cancelled and detach the move ids
        self.write(cr, uid, ids, {'move_id': False})
        
        if move_ids:
            # second, invalidate the move(s)
            # account_move_obj.button_cancel(cr, uid, move_ids, context=context)
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            now = time.strftime(' [%Y%m%d %H%M%S]')

            for move in account_move_obj.browse(cr , uid, move_ids):
                # unlink from invoice
                #account_move_obj.unlink(cr, uid, [move.id], context=context)
                name = move.name + now
                account_move_obj.write(cr, uid, [move.id], {'name':name})
                move_copy_id = account_move_obj.copy(cr, uid, move.id)
                name = name + '*'
                cr.execute("""update account_move_line
                                 set debit=credit, credit=debit
                               where move_id = %s;""" % (move_copy_id))
                account_move_obj.write(cr, uid, [move_copy_id], {'name':name})
                account_move_obj.button_validate(cr, uid, [move_copy_id], context=None)
            
              
        self._log_event(cr, uid, ids, -1.0, 'Reopened Invoice')
        return True

    #def action_move_create(self, cr, uid, ids, context=None):
    #    move_obj = self.pool.get('account.move')
    #    move_ids = [] # ones that we will need to update
    #    for inv in self.browse(cr, uid, ids, context=context):
    #        if inv.move_id:
    #            move_ids.append(inv.move_id.id)
    #        else:
    #            super(account_invoice, self).action_move_create(cr, uid, ids, context)
    #    if move_ids:
    #        move_obj.write(cr, uid, move_ids, {'state':'posted'})

    def action_number(self, cr, uid, ids, context=None):
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.internal_number:
                super(account_invoice, self).action_number(cr, uid, ids, context)
        return True


account_invoice()
