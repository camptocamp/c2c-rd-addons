# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    23-Jan-2013 (GK) created
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
from osv import fields, osv
import time
from tools.translate import _

class account_period(osv.osv) :
    _inherit = "account.period"

    def kz() :
        return "0.00" ##################
    # end def kz

    def generate_U30(self, cr , uid, ids, context=None):
        for period in self.browse(cr, uid, ids) :
            template_obj  = self.pool.get("xml.template")
            template_ids  = template_obj.search(cr, uid, [("name", "=", "U30 VAT declaration")])
            if not template_ids :
                raise osv.except_osv \
                    ( _("Customization Error !")
                    , _("No Template '%s' defined") % template_name
                    )
            template_id = template_ids[0]
            xml = template_obj.generate_xml \
                (cr, uid
                , template_id
                , period = period
                , paket_nr=time.strftime("%y%m%d%H")
                , datum=time.strftime("%Y-%m-%d")
                , uhrzeit=time.strtime("%H:%M:%S")
                , jahrmonat_beginn=period.date_start[0:7]
                , jahrmonat_ende=period.date_stop[0:7]
                , vst="lab3"
                , are="J"
                , repo="J"
                , kz = kz
                )
            template_obj.attach_xml \
                ( cr, uid
                , template_id
                , attach_to   = period
                , xml         = xml
                , name        = period.code + "_U30"
                , fname       = period.code + "_U30" + ".xml"
                , description = "U30 VAT declaration for period"
                , context     = None
                )
    # end def generate_U30
# end class account_period
account_period()
