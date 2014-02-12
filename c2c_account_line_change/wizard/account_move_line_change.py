# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

class account_move_line_change(osv.osv_memory):
    _name = "account.move.line.change"
    _description = "Changes accounts in posted moves lines"
    _logger = logging.getLogger(_name)

    def _get_account(self, cr, uid, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        line = self.pool.get('account.move.line').browse(cr, uid, record_id, context=context)
        self._logger.debug('get_account  `%s` `%s` `%s` `%s`', context, record_id, line.account_id.id,line.account_id.type, line.account_id.user_type.id)
        return  {'account_id' : line.account_id.id, 
                 'account_type' : line.account_id.type, 
                 'account_user_type' : line.account_id.user_type.id,
                     'period_id' : line.period_id.id, 
                     'period_state' : line.period_id.state,}

    _columns = {
        'account_id'       : fields.many2one('account.account','Current Account' ),
        'account_type'     : fields.char('Internal Type', size=16),
        'account_user_type': fields.many2one('account.account.type', 'Account Type'),
        'account_new_id'   : fields.many2one('account.account','New Account' ),
        'period_id'        : fields.many2one('account.period','Period' ),
        'period_state'     : fields.char('Period State', size =16 ),

    }

    def default_get(self, cr, uid, fields_list, context=None):
        res = super(account_move_line_change, self).default_get(cr, uid, fields_list, context=context)
        res.update(self._get_account(cr, uid, context=context))
        return res


    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        line = self.pool.get('account.move.line').browse(cr, uid, record_id, context=context)
        if line.state != 'valid':
            raise osv.except_osv(_('Warning !'),'This wizard is for valid posted moves only. You must modify draft moves directly')
        if line.period_id.state != 'draft':
            raise osv.except_osv(_('Warning !'),'Currently this wizard is for open periods only.')
        if line.account_id.type != 'other':
            raise osv.except_osv(_('Warning !'),'Currently this wizard is for account type "Other".')
        self._logger.debug('view_init `%s` `%s` `%s`', context, record_id, line.account_id.id)
        return False
        

    def update_account_move_line(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.move.line')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        self._logger.debug('context `%s`', context)
        self._logger.debug('data `%s`', data)
        new_account_id = data['account_new_id']
        if not new_account_id or new_account_id == data['account_id']:
            raise osv.except_osv(_('Error'),'You must define an account different from the original')
        update_check = False
        check = True
        context.update({'account_id':  new_account_id})
        
        
        vals = {}
        line_obj = self.pool.get('account.move.line')
        record_ids = context and context.get('active_ids', False)
        self._logger.debug('new context `%s`', record_ids)
        line = line_obj.browse(cr, uid, record_ids, context=context)
        
        vals['account_id'] =  new_account_id
        self._logger.debug('new context `%s` `%s` `%s` `%s`', record_ids, context, vals, update_check)
        
        line_obj.write(cr, uid, record_ids, vals, context, check, update_check)
        return {'type': 'ir.actions.act_window_close'}
 
account_move_line_change()

