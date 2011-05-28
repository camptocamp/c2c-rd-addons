# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- encoding: utf-8 -*-
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
import time
from osv import fields,osv
import pooler

from datetime import datetime
from math import ceil 
import sys


class act_window(osv.osv):
    _inherit = "ir.actions.act_window"
   
    def _auto_search_check(self, cr, uid, ids, context=None):
        model_obj = self.pool.get('ir.model')
        window_obj = self.pool.get('ir.actions.act_window')
        window_ids = window_obj.search(cr, uid, [( 'auto_search_check', '=', True),( 'auto_search', '=', True) ])
        
        for act_window in window_obj.browse(cr,uid, window_ids, context=None):
            # FIXME add domain to get realistic results ??
            cr.execute(""" select count(*) from %s;""" % act_window.res_model._table)
            count = cr.fetchone()
            print >> sys.stderr,'model ', act_window.res_model._table, count
            if count > 80:
                cr.execute(""" update ir_act_window
                        set auto_search = False
                      where id = %s;""" % act_window.id)
                #cr.fetchone()      
        return True

    _columns = {
        'auto_search_check': fields.boolean('Auto Search Check', help="if checked, the number of records will be checked periodicaly and autosearch will be turned off for big tables"),
    }
    def init(self, cr):
       cr.execute("""update ir_act_window
                        set auto_search_check = True
                      where auto_search_check is null;""")
       
       return

act_window()


