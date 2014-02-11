# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    19-MAY-2011 (GK) created
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

class ir_attachment (osv.osv):
    _inherit = "ir.attachment"

#    def _ref (self, cr, uid, ids, field_name, arg, context) :
#       res = {}
#       for obj in self.browse (cr, uid, ids) :
#           if obj.res_model and obj.res_id :
#               res[obj.id] = obj.res_model + ",%s" % obj.res_id
#           else :
#                res[obj.id] = False
#       return res
#    # end def _ref

#    _columns  = \
#        { 'ref' : fields.function
#            ( _ref
#            , type     = 'char', size=128
#            , method   = True
#            , string   = 'Migration aid'
#            , store    = True
#            , readonly = True
#            )
#        }

    def _links_get(self, cr, uid, context={}) :
        obj = self.pool.get("res.request.link")
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ["object", "name"], context)
        return [(r["object"], r["name"]) for r in res]
    # ende def _links_get

    _columns  = \
        { 'ref' : fields.reference('Migration aid', selection=_links_get, size=128, readonly=True)}
# end class ir_attachment
ir_attachment()
