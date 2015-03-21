# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-18 23:44:30+02
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
{ 'sequence': 500,
"name"         : "Autosearch Check - just an Idea"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.camptocamp.at"
, "description"  : """
This module checks if number of table ressources is large and turns autosearch off
The default is 80 records (~2 screenfull).
Can be modified with act_window._autosearch_check_limit = 160.
In most other cases it makes more sense to allow to enter a query before querying the table.
This check will run periodically and turn off autosearch for ir_act_window where auto_search_check is True.
"""
, "category"     : "Generic Modules/Base"
, "depends"      : ["base"]
, "init_xml"     : ["autosearch_data.xml"]
, "demo"         : []
, "data"   : ["autosearch_view.xml"]
, "auto_install" : False
, 'installable'  : False
, 'application'  : False
}

