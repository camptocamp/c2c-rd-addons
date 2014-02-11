
# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2012 ChriCar (http://www.chricar.at)
#   @author Ferdinand Gassauer
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import fields,osv
#import pooler



class chricar_account_move_line_igel_transfer(osv.osv_memory):
    _name = "chricar.account.move.line.igel.transfer"
    _description = "Transfer imported Igel Moves"
    _columns = {
        'dummy': fields.boolean('Dummy', help=''),
    }
    _defaults = {
        'dummy': False
    }

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        igel_moves = self.pool.get('chricar.account.move.line.igel').browse(cr, uid, record_id, context=context)
        #if order.state != 'progress':
        #    raise osv.except_osv(_('Warning !'),'You can only internal pull pickings from SO in progres.')
        return False

    def but_autodetect(self, cr, uid, ids, context=None):
        igel_obj = self.pool.get('chricar.account.move.line.igel')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        new_pick = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        igel_obj.autodetect(cr, uid, context.get(('active_ids'), []), )
        return

    def but_transfer_igel_moves(self, cr, uid, ids, context=None):
        igel_obj = self.pool.get('chricar.account.move.line.igel')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        new_pick = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        igel_obj.transfer_igel_moves(cr, uid, context.get(('active_ids'), []), )
        return

chricar_account_move_line_igel_transfer()
