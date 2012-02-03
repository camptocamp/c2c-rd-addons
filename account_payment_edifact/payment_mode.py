# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    05-AUG-2010 (GK) created
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
from osv import fields, osv
from tools.translate import _

class payment_mode(osv.osv) :
    _inherit = "payment.mode"
    # http://www.unece.org/trade/untdid/d00a/tred/tred4471.htm
    _columns = \
        { 'charges_alloc' : fields.selection
            ([ ( '1', _('Bill back'))
             , ( '2', _('Off invoice'))
             , ( '3', _('Vendor check to customer'))
             , ( '4', _('Credit customer account'))
             , ( '5', _('Charge to be paid by vendor'))
             , ( '6', _('Charge to be paid by customer'))
             , ( '7', _('Optional'))
             , ( '8', _('Off gross quantity invoiced'))
             , ( '9', _('Electric cost recovery factor'))
             , ('10', _('Gas cost recovery factor'))
             , ('11', _('Prior credit balance'))
             , ('12', _('Non-dutiable'))
             , ('13', _('All charges borne by payee'))
             , ('14', _('Each pay own cost'))
             , ('15', _('All charges borne by payor'))
             , ('16', _('All bank charges to be borne by applicant'))
             , ('17', _('All bank charges except confirmation commission to be borne by applicant'))
             , ('18', _('All bank charges to be borne by beneficiary'))
             , ('20', _('Amendment charges to be borne by applicant'))
             , ('21', _('Amendment charges to be borne by beneficiary'))
             , ('22', _('Discount charges to be borne by applicant'))
             , ('23', _('Discount charges to be borne by beneficiary'))
             , ('24', _('All bank charges other than those of the issuing bank to be borne by beneficiary'))
             , ('25', _('Amendment charges other than those of the issuing bank to be borne by beneficiary'))
             , ('26', _('All charges to be paid by the principal of the collection'))
             , ('27', _('All charges to be paid by the drawee of the collection'))
             , ('28', _('All charges to be borne by the drawee except those levied by the remitting bank, to be paid by principal'))
             , ('29', _('All bank charges are to be paid by the principal of the documentary credit collection'))
             , ('30', _('All bank charges to be borne by receiving bank'))
             , ('31', _('All bank charges to be borne by sending bank'))
             , ('32', _('Charges levied by a third bank'))
             , ('33', _('Information charges levied by a third bank'))
             , ('34', _('Total payment borne by patient'))
             , ('35', _('Part payment borne by patient')) 
             , ('ZZZ', _('Mutually defined'))
             ]
            , 'Financial Charges Allocation'
            )
        }
    _defaults = {'charges_alloc'    : lambda *a: '14'}
# end class payment_mode
payment_mode()
