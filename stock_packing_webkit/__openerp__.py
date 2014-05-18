# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Ferdinand Gassauer (ChriCar Beteiligungs- und Beratungs- GmbH)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
{ 'sequence': 500,
"name"         : "Webkit Report Stock Packing"
, "description"  : """
Stock picking using Webkit,

Address label with option to position address left, right
using address lebel field with addressee's country specific zip position

shows address in internal tree view"""
, "version"      : "0.9"
, "depends"      : 
[ "stock"
, "report_webkit"
, "c2c_partner_address_label"
, "delivery"
, "one2many_sorted"
]
, "category"     : "Warehouse Management"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.camptocamp.com/"
, "data"         : ["stock_packing_webkit_view.xml", "stock_packing_view.xml"]
, "installable"  : True
, 'application'  : False
, "auto_install" : False
}
