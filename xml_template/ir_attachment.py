# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    26-JUL-2011 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from openerp.osv import fields, osv
from openerp.tools.translate import _

class ir_attachment_ref(osv.osv):
    _name           = "ir.attachment.ref"
    _description    = "Attachment Reference"

    def _links_get(self, cr, uid, context={}) :
        obj = self.pool.get("res.request.link")
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ["object", "name"], context)
        return [(r["object"], r["name"]) for r in res]
    # ende def _links_get

    _columns  = \
        { "ir_attachment_id" : fields.many2one("ir.attachment", "Attachment", required=True, ondelete="cascade")
        , "name"             : fields.reference('Reference', selection=_links_get, size=128, required=True)
        }
    _sql_constraints = \
        [( "ir_attachment_ref_name_index"
         , "unique (name,ir_attachment_id)"
         , "The Reference has to be unique!"
         )
        ]
# end class ir_attachment_ref
ir_attachment_ref()

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"

    _columns  = \
        {"reference_ids"  : fields.one2many("ir.attachment.ref", "ir_attachment_id", "References")}
# end class ir_attachment
ir_attachment()
