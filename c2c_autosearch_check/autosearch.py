# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-18 23:44:30+02
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from openerp.osv import fields,osv
import logging

class act_window(osv.osv):
    _inherit = "ir.actions.act_window"
    _autosearch_check_limit = 80
    _logger = logging.getLogger(__name__)

    def run_auto_search_check(self, cr, uid):
        window_obj = self.pool.get('ir.actions.act_window')
        window_ids = window_obj.search \
            ( cr, uid
            , [('auto_search_check', '=', True), ('type', '=', 'ir.actions.act_window')]
            )
        for act_window in window_obj.browse(cr, uid, window_ids) :
            # FIXME add domain to get realistic results ??
            _obj = self.pool.get(act_window.res_model)
            if not _obj : continue
            sql = """SELECT count(*) FROM %s;""" % _obj._table
            cr.execute(sql)
            count = cr.fetchone()
            if count > self._autosearch_check_limit :
                try :
                    window_obj.write(cr, uid, [act_window.id], {'auto_search' : False})
                except :
                    self._logger.debug('!!c2c_autosearch_check!! could not write ir.actions.act_window `%s`', act_window.id)
    # end def run_auto_search_check

    _columns = \
        { 'auto_search_check': fields.boolean
            ('Auto Search Check'
            , help="If selected, the number of records will be checked periodically and autosearch will be turned off for big tables"
            )
        }
    _defaults = {'auto_search_check' : lambda *a : True}
act_window()
