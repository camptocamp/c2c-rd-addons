# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2010-04-03 21:47:30+02
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
from openerp.osv import fields,osv
#import pooler

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
          'date_weighing'  : fields.datetime('Date Weighing',),
          'consignment_note':fields.char    ('Consignement Note Number', size=32, help="Number of Consignement Note (AWB,CIM,CMR,CDT,MDT)  http://www.tis-gdv.de/tis/bedingungen/trpdoku/inhalt.htm#1"),
          'number_weighing': fields.char    ('Number Weighing', size=16),
          'tractor_number' : fields.char    ('License Number Tractor', size=16),
          'trailer_number' : fields.char    ('License Number Trailer', size=16),
          'tractor_gross'  : fields.float   ('Tractor Gross Weight', digits=(5,0)),
          'tractor_net'    : fields.float   ('Tractor Net Weight', digits=(5,0)),
          'tractor_tare'   : fields.float   ('Tractor Tare Weight', digits=(5,0)),
          'trailer_gross'  : fields.float   ('Trailer Gross Weight',digits=(5,0)),
          'trailer_net'    : fields.float   ('Trailer Net Weight', digits=(5,0)),
          'trailer_tare'   : fields.float   ('Trailer Tare Weight', digits=(5,0)),
          'total_net'      : fields.float   ('Total Net', digits=(5,0)),
          'total_gross'    : fields.float   ('Total Gross', digits=(5,0)),
          'seal'           : fields.char    ('Seals', size=32),
          'sample'         : fields.char    ('Sample Number', size=32),
          'print_net_only' : fields.boolean ('Print Only Net Weight'),
    }

#    def _get_number_weighing(self, cr, uid, moves, context=None):
#        result = {}
#        for m in moves:
#            if m.total_gross > 0.0 and (not m.number_weighing or m.number_weighing == 0.0) :
#                m.number_weighing = self.pool.get('ir.sequence').get(cr, uid, 'number.weighing')
#                return result

    def on_change_weight(self, cr, uid, ids, tractor_gross=False,tractor_tara=False,trailer_gross=False,trailer_tara=False,number_weighing=False):

        result = {}
        if not tractor_gross:
            tractor_gross = 0.0
        if not trailer_gross:
            trailer_gross = 0.0
        tractor_net = 0.0
        trailer_net = 0.0

        if tractor_gross and tractor_tara:
            tractor_net = tractor_gross - tractor_tara
        if trailer_gross and trailer_tara:
            trailer_net = trailer_gross - trailer_tara

        result['tractor_net'] = tractor_net
        result['trailer_net'] = trailer_net
        result['total_net'] = tractor_net + trailer_net
        result['total_gross'] = tractor_gross + trailer_gross
        if tractor_gross + trailer_gross > 0.0:
            result['date_weighing'] = time.strftime('%Y-%m-%d %H:%M:%S')
            if not number_weighing:
            # FIXME - non blocking solution !
                result['number_weighing'] = self.pool.get('ir.sequence').get(cr, uid, 'number.weighing')
            else:
                result['number_weighing'] = number_weighing
        else:
            result['date_weighing'] = ''


        return {'value':result}

stock_picking()
