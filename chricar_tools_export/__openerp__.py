# -*- coding: utf-8 -*-
##############################################################################
#
#    Chricar Beteiligungs- und Beratungs- GmbH
#    Copyright (C) 2004-2010 Chricar Beteiligungs- und Beratungs- GmbH,
#    www.chricar.at
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{ 'sequence': 500,

'name': 'ChriCar Export CSV Utilities',
'version': '1.0',
'category': 'Tools',
'description': """
WARNING - it breaks Form Export on GTK https://bugs.launchpad.net/openobject-client/+bug/665733
works on koo and Web
This module provides
    * a field in Objects with a psql statement to export all table data to CSV
which can be reimproted using Form Import.
    * a default list for Form Export with all fields
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': ['base'],
'website': 'http://www.chricar.at',
'data': ['tools_export_view.xml'],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
