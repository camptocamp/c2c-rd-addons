# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
#    Copyright (C) 2011-2011 Swing Entwicklung betrieblicher Informationssysteme GmbH (<http://www.swing-system.com>)
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
from osv import fields, osv
from tools.translate import _

class account_move(osv.osv):
    _inherit = "account.move"

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise osv.except_osv \
                ( _('Integrity Error !')
                , _('You cannot validate a non-balanced entry!\nMake sure you have configured Payment Term properly !\nIt should contain at least one Payment Term Line with type "Balance" !')
                )
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id, 'journal_id': move.journal_id.id}
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, context=c)
                    # FIXME
                    # some sequences are requested internaly but not defined 
                    # https://bugs.launchpad.net/bugs/737517    
                    #else:
                    #    raise osv.except_osv(_('Error'), _('No sequence defined on the journal !'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name' : new_name})

        cr.execute('UPDATE %s SET state=%s WHERE id IN %s', (self._table, 'posted', tuple(valid_moves)))
        return True
    # end def post

account_move()
