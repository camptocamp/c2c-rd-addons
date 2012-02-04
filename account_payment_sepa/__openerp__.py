# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    01-APR-2011 (GK) created
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
# 59 Temple Place - Suite 330, Boston, MA  02111-1.17, USA.
#
###############################################
{ "name"        : "Electronic Banking via SEPA"
, "version"     : "1.1"
, "author"      : "Swing Entwicklung betrieblicher Informationssysteme GmbH"
, "website"     : "http://www.swing-system.com"
, "description" : 
"""
SEPA (Single European Payment Area) is a standardization of the ECBS (European Commitee for Banking Standards).
It conforms to the ISO 20022 standard (Finmancial services - universal financial industry message scheme).

This module implements the credit transfer (ISO.pain.001.101).
It generates an XML-file per payment-order and attaches it to the payment order at the time of payment_order.action_open.

For each involved bank BIC/IBAN is required.
"Steuerzahlung" is not implemented.
The "payment day" is, if unspecified or in the past, the file-creation-date.
"""
, "category"    : "Payment module"
, "depends"     : 
    [ "account_payment"
    , "base_iban"
    , "xml_template"
    ]
, "init_xml"    : ["payment_data.xml"]
, "demo_xml"    : []
, "update_xml"  : ["payment_sepa_wizard.xml"]
, "test"        : []
, "active"      : False
, "installable" : True
}
