# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    20-APR-2011 (GK) created
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
# 59 Temple Place - Suite 330, Boston, MA  02111-1.17, USA.
#
###############################################
{ 'sequence': 500,
"name"        : "Support for payment via electronic banking"
, "version"     : "1.1"
, "author"      : "Swing Entwicklung betrieblicher Informationssysteme GmbH"
, "website"     : "http://www.swing-system.com"
, "description" : 
"""
An additional invoice reference is provided, the so-called "customer data" 
a 12 digit numeric field
(German: Kundendaten)
This reference is used by EDIFACT or SEPA.
"""
, "category"    : "Generic Modules/Payment"
, "depends"     : ["account"]
, "init_xml"    : []
, "demo"        : []
, "data"  : ["account_invoice_view.xml"]
, "test"        : []
, "auto_install": False
, 'installable': False
, 'application'  : False
}
