# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-07-11 12:22:10+02
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

class chricar_room(osv.osv):
     _name = "chricar.room"

     _columns = {
       'top_id'             : fields.many2one('chricar.top','Top', select=True, required=True),
       'name'               : fields.char    ('Name', size=64, required=True),
       'size'               : fields.float   ('Size', digits=(6,2)),
       'height'             : fields.float   ('Height', digits=(4,2)),
       'tv_cable'           : fields.boolean ('TV Cable'),
       'tv_sat'             : fields.boolean ('TV Sat'),
       'telephon'           : fields.boolean ('Telephon'),
       'windows'            : fields.integer ('Windows'),
       'balcony'            : fields.integer ('Balconies'),
       'terrace'            : fields.integer ('Terrace'),
       'garden_access'      : fields.boolean ('Garden Access'),
       'floor'              : fields.selection([('unknown','unknown'),
                                                ('stone','Stone'),
                                                ('wood','Wood'),
                                                ('screed','Screed'),
                                                ('tiles','Tiles'),
                                                ('carpet','Carpet')], 'Floor'),
       'note'               : fields.text    ('Notes'),
       'sequence'           : fields.integer ('Sequence'),
}
     _defaults = {
}
     _order = "sequence"

chricar_room()

class chricar_top(osv.osv):
      _inherit = "chricar.top"
      _columns = {
          'room_ids': fields.one2many('chricar.room','top_id','Rooms'),
      }
chricar_top()


