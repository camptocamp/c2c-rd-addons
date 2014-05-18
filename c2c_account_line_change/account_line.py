# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

from openerp.tools.translate import _

import sys

#----------------------------------------------------------
#  Account Move Line INHERIT
#----------------------------------------------------------
class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _columns = {
        'account_type'     : fields.related('account_id', 'type', type='char', relation='account.account', string='Internal Type'),
        'account_user_type': fields.related('account_id', 'user_type', type='many2one', relation='account.account.type', string='Account Type'),
        'account_new_id'   : fields.many2one('account.account','New Account' ),
        'account_old'      : fields.related('account_id', 'name', type='char', relation='account.account', string='Old Account'),
        'account_old_code' : fields.related('account_id', 'code', type='char', relation='account.account', string='Old Code'),     
    }
 
    def write(self, cr, uid, ids, vals,  context=None, check=True, update_check=True):
        result = {}
        if vals.get('account_new_id'):
            print >> sys.stderr, 'new account', vals
            vals['account_id'] =  vals.get('account_new_id')
            vals['account_new_id'] =  False
            update_check = False
            print >> sys.stderr, 'new accounts ', vals, update_check
        #result = super(account_move_line, self).write(cr, uid, ids, vals, context, check, update_check)
            line_obj= self.pool.get('account.move.line')
            result = line_obj.write(cr, uid, ids, vals, context, check, update_check)
        return result

account_move_line()

