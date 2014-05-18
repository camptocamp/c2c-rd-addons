# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
 
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _logger = logging.getLogger(__name__)
    
    def _reconcile(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context):
            r = True
            if l.reconcile_id and not l.account_id.reconcile:
		r = False
        return r
    
    def _new_constraints(self, cr, uid, ids, context=None):
        self._logger.debug('constraints start')
        model_obj = self.pool.get('ir.model')
        model_ids = model_obj.search(cr, uid, [('name','=','account.move.line')])
        constraints = []
        for m in model_obj.browse(cr, uid, model_ids):
            if m._constraints:
                constraints = m._constraints   
                self._logger.debug('constraints %s', constraints)
        s = "(_reconcile,_('You must not reconcile moves on account '),['reconcile_id'])"
        self._logger.debug('constraints string %s', s)
        constraints.append(s)
        self._logger.info('new constraints %s', constraints)
        return constraints
 
# FIXME       
#    _constraints = _new_constraints
    _constraints = [(_reconcile,_('You must not reconcile moves on account'),['reconcile_id'])]

    
account_move_line()
