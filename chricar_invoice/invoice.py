# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-07-11 14:55:52+02
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

class chricar_invoice(osv.osv):
     _name = "chricar.invoice"

     _columns = {
       'amount'             : fields.float   ('Amount Paid', required=True),
       'amount_quote'       : fields.float   ('Amount Quote', required=True),
       'date_document'      : fields.date    ('Date', required=True),
       'name'               : fields.char    ('Document', size=64, required=True),
       'note'               : fields.text    ('Notes'),
       'partner_id'         : fields.many2one('res.partner','Partner', select=True, required=True),
       'ref'                : fields.char    ('Reference', size=64),
       'room_id'            : fields.many2one('chricar.room','Room', select=True),
       'top_id'             : fields.many2one('chricar.top','Top', select=True, required=True),
}
     _defaults = {
}
     _order = "date_document"

chricar_invoice()

class chricar_room(osv.osv):
      _inherit = "chricar.room"
      _columns = {
          'invoice_ids': fields.one2many('chricar.invoice','room_id','Invoice'),
      }
chricar_room()
class chricar_top(osv.osv):
      _inherit = "chricar.top"
      _columns = {
          'invoice_ids': fields.one2many('chricar.invoice','top_id','Invoice'),
      }
chricar_top()
class res_partner(osv.osv):
      _inherit = "res.partner"
      _columns = {
          'invoice_ids': fields.one2many('chricar.invoice','partner_id','Invoice Real Estate'),
      }
res_partner()

