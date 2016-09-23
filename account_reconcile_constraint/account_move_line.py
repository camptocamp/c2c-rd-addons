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

# FIXME remove logger lines or change to info
 
from osv import fields, osv
from tools.translate import _
import logging

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _logger = logging.getLogger(__name__)
    
    
    def _reconcile(self, cr, uid, r_id, context=None):
        _logger = logging.getLogger(__name__)
        _logger.info('FGF reconcile_id: %s', r_id)
        aml = self.pool.get('account.move.line')
        account_id = ''
        partner_id = ''
 
        l_ids = aml.search(cr, uid, [('reconcile_id','=', r_id)])
        _logger.info('FGF line_ids: %s', l_ids)
        if len(l_ids)> 1:
          count = 0
          for l in aml.browse(cr, uid, l_ids, context):
            count += 1
            if count == 1:
                account_id = l.account_id
                account_name = l.account_id.name
                partner_id = l.partner_id 
                partner_name = l.partner_id.name or '*No*'
                if not l.account_id.reconcile:
                    raise osv.except_osv("Reconcile Error Account not allowed", 'Reconcile id: "%s"  Account Name: %s' % (l.reconcile_id.name, l.account_id.name))
            else:
                if account_id != l.account_id:
                    raise osv.except_osv("Reconcile multiple accounts Error", 'Reconcile id: "%s", Acccount Name 1: %s Account Name 2: %s'  % (l.reconcile_id.name, account_name, l.account_id.name))
                if (partner_id or 'None')  != (l.partner_id or 'None'):
                    raise osv.except_osv("Reconcile multiple Partners Error", 'Reconcile id: "%s",  Partner 1: %s Partner 2: %s' % (l.reconcile_id.name, partner_name, l.partner_id.name))


    def write(self, cr, uid, ids, vals, context=None):
        _logger = logging.getLogger(__name__)
        res = super(osv.osv, self).write(cr, uid, ids, vals, context=context)

        _logger.info('FGF write vals: %s', vals)
        if vals.get('reconcile_id') and vals['reconcile_id']: 
            self._reconcile(cr, uid, vals['reconcile_id'], context)

        return res

    
account_move_line()



