# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
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
import netsvc
from tools.misc import UpdateableStr, UpdateableDict

class stock_location(osv.osv):
    _inherit = "stock.location"

    def _get_points(self, cr, uid, ids, name, args, context=None):
        res = {}
        for loc in self.browse(cr, uid, ids, context=context):
            points = ''
            if loc.yield_rate and loc.capacity:
                # capacity = ha
                points = round(loc.yield_rate/(loc.capacity*10000)*100,0)
            res[loc.id] = points
        return res

    _columns = {
    'yield_rate'         : fields.float   ('Yield Rate', help="Ertragsmesszahl"),
    'yield_points'       : fields.function(_get_points, method=True, type='float', string='Points'),
    }


stock_location()
