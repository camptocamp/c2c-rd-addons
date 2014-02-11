# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-07-11 14:41:58+02
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

class chricar_equipment(osv.osv):
     _name = "chricar.equipment"

     _columns = {
       'contract'           : fields.char    ('Contract ', size=64),
       'date_contract'      : fields.date    ('Contract Date'),
       'date_service_last'  : fields.date    ('Last Service'),
       'date_service_next'  : fields.date    ('Next Service'),
       'lease'              : fields.float   ('Lease', digits=(4,2)),
       'name'               : fields.char    ('Name', size=128, required=True),
       'note'               : fields.text    ('Notes'),
       'notice_period'      : fields.integer ('Notice Period', help="Notice period in days"),
       'partner_id'         : fields.many2one('res.partner','Partner', select=True ),
       'room_id'            : fields.many2one('chricar.room','Room', select=True, domain="[('top_id','=',top_id)]"),
       'date_from'          : fields.date    ('From'),
       'date_to'            : fields.date    ('To'),
       'top_id'             : fields.many2one('chricar.top','Top', select=True, required=True),
}
     _defaults = {
       'date_contract'     : lambda *a: '',
       'date_service_last' : lambda *a: '',
       'date_service_next' : lambda *a: '',
       'lease'             : lambda *a: '',
       'notice_period'     : lambda *a: '',
}
     _order = "name"
chricar_equipment()

class chricar_room(osv.osv):
      _inherit = "chricar.room"
      _columns = {
          'equipment_ids': fields.one2many('chricar.equipment','room_id','Equipment'),
      }
chricar_room()
class chricar_top(osv.osv):
      _inherit = "chricar.top"
      _columns = {
          'equipment_ids': fields.one2many('chricar.equipment','top_id','Equipment'),
      }
chricar_top()
class res_partner(osv.osv):
      _inherit = "res.partner"
      _columns = {
          'equipment_ids': fields.one2many('chricar.equipment','partner_id','Equipment'),
      }
res_partner()


