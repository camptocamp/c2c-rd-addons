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
from openerp.osv import fields, osv
import time
from openerp.tools.translate import _

class account_period(osv.osv) :
    _inherit = "account.period"

    def kz(self, period, code) :
        cr      = self.cr
        uid     = self.uid
        aml_obj = self.pool.get("account.move.line")
        atc_obj = self.pool.get("account.tax.code")
        atc_ids = atc_obj.search(cr, uid, [("code", "=", code.replace("KZ", ""))])
        aml_ids = aml_obj.search(cr, uid, [("period_id", "=", period.id), ("tax_code_id", "in", tuple(atc_ids))])  # vereinbarte entgelte, hängt von Firmenart ab, currency_id
        if not aml_ids :
            return "0.00"
        else :
            return "%f0.2" % sum(l.tax_amount for l in aml_obj.browse(cr, uid, aml_ids))
    # end def kz

    def generate_u30(self, cr , uid, ids, context=None):
        self.cr  = cr
        self.uid = uid
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
                , period   = period
                , paket_nr = time.strftime("%y%m%d%H")
                , datum    = time.strftime("%Y-%m-%d")
                , uhrzeit  = time.strftime("%H:%M:%S")
                , beginn   = period.date_start[0:7]
                , ende     = period.date_stop[0:7]
                , vst      = "000"
                , are      = "J"
                , repo     = "J"
                , kz       = self.kz
                , tax_nr   = "123456789"
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
    # end def generate_u30
# end class account_period
account_period()
