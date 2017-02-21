# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 Camptocamp Austria (<http://www.camptocamp.com>).
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

class account_bank_statement(osv.osv):

    _inherit = "account.bank.statement"

    def _check_duplicate_name(self, cr, user, name, context):
        if name != '/':
            duplicate_ids =  self.search(cr, user, [('name','=', name)], context=context)
            if duplicate_ids:
                raise osv.except_osv(_('Error !'), _('Duplicate account move name "%s" is not allowed') % name)
        return
   
            
#    def write(self, cr, uid, ids, vals, context=None):
#        self._check_duplicate_name(cr, uid, vals.get('name') and  vals['name'] or '/'  , context)
#        result = super(account_bank_statement, self).write(cr, uid, ids, vals, context=context) 
#        return result

    def create(self, cr, uid, vals, context=None):
        self._check_duplicate_name(cr, uid, vals.get('name') and   vals['name'] or '/' , context)
        result = super(account_bank_statement, self).create(cr, uid, vals, context=context) 
        return result


        
    




account_bank_statement()
