# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-02-11 16:03:53+01
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

class chricar_inventory(osv.osv):
     _name = "chricar.inventory"
     _columns = \
         { 'active'       : fields.boolean ('Active', readonly=True)
         , 'image'        : fields.binary  ('Image')
         , 'location_id'  : fields.many2one('stock.location','Room', select=True)
         , 'location_old' : fields.char    ('Room Old', size=64, required=True)
         , 'name'         : fields.text    ('Name', required=True, help="Name / Description of the Inventory")
         , 'partner_id'   : fields.many2one('res.partner','Owner', select=True)
         , 'partner_old'  : fields.char    ('Owner Old', size=64)
         , 'position'     : fields.integer ('Position',  required=True)
         , 'position_old' : fields.char    ('Position Old', size=8)
         , 'state'        : fields.char    ('State', size=16, readonly=True)
         , 'value'        : fields.float   ('Value', required=True, digits=(10,2))
         , 'value_ats'    : fields.float   ('Value ATS', digits=(10,2))
         }
     _defaults = \
         { 'active' : lambda *a: True
         , 'state'  : lambda *a: 'draft'
         }
     _order = "location_id, location_old, position, name"
chricar_inventory()

class res_partner(osv.osv):
      _inherit = "res.partner"
      _columns = {'inventory_ids': fields.one2many('chricar.inventory','partner_id','Inventory')}
res_partner()
class stock_location(osv.osv):
      _inherit = "stock.location"
      _columns = {'inventory_ids': fields.one2many('chricar.inventory','location_id','Inventory')}
stock_location()
