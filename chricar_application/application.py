
#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-03-27 16:34:25+01
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

class chricar_application(osv.osv):
     _name = "chricar.application"

     _columns = {
       'active'             : fields.boolean ('Active', readonly=True),
       'author'             : fields.char    ('Author', size=128, required=True),
       'name'               : fields.char    ('Application Name', size=64, required=True),
       'partner_id'         : fields.many2one('res.partner','Partner', select=True, required=True),
       'prefix'             : fields.char    ('Prefix', size=16, required=True),
       'state'              : fields.char    ('State', size=16, readonly=True),
       'website'            : fields.char    ('Web Site', size=64, required=True),
}
     _defaults = {

       'active'            : lambda *a: True,
       'author'            : lambda *a: 'ChriCar Beteiligungs- und Beratungs- GmbH',
       'state'             : lambda *a: 'draft',
       'website'           : lambda *a: 'http://www.chricar.at/ChriCar',
}
     _order = "name"
chricar_application()

class res_partner(osv.osv):
      _inherit = "res.partner"
      _columns = {
          'application_ids': fields.one2many('chricar.application','partner_id','Application'),
      }
res_partner()

