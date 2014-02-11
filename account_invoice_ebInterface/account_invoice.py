# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    31-DEC-2012 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

class account_invoice(osv.osv) :
    _inherit = "account.invoice"

    def invoice_validate(self, cr, uid, ids, context=None):
        self.generate_ebInterface(cr , uid, ids, context=context)
        return super(account_invoice,self).invoice_validate(cr, uid, ids, context=context)
#   def invoice_validate

    def generate_ebInterface(self, cr , uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids) :
            template_obj  = self.pool.get("xml.template")
            template_ids  = template_obj.search(cr, uid, [("name", "=", "ebInterface V4.0")])
            if not template_ids :
                raise osv.except_osv \
                    ( _("Customization Error !")
                    , _("No Template '%s' defined") % template_name
                    )
            template_id = template_ids[0]
            xml = template_obj.generate_xml \
                (cr, uid
                , template_id
                , invoice = invoice
                )
            template_obj.attach_xml \
                ( cr, uid
                , template_id
                , attach_to   = invoice
                , xml         = xml
                , name        = invoice.number + "_ebInterface"
                , fname       = invoice.number + "_ebInterface" + ".xml"
                , description = "ebInterface for invoice"
                , context     = None
                )
    # end def generate_ebInterface
# end class account_invoice
account_invoice()
