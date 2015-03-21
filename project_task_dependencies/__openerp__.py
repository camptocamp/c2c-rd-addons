# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Davide Corio
#    (<http://www.davidecorio.com>).
#    Copyright (C) 2013 Camptocamp SA, Ferdinand Gassauer
#    (<http://www.camptocamp.com>).
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

'name': 'Task Dependencies',
'version': '1.0',
'category': 'Project Management',
'description': """
This module allows the user to set dependencies on project tasks.
Tasks cannot be completed if they have open dependencies.
DO NOT USE GANTT VIEW TO MODIFY DATES (successor tasks dates are not computed)
Needs python-networkx later?
""",
'author': 'Davide Corio, Ferdinand Gassauer',
'website': 'http://www.davidecorio.com, http://www.camptocamp.com',
'summary': 'Task Dependencies',
'depends': ['project'],
'data': ['project_view.xml'],
'installable': False,
'application': False,
'auto_install': False,
}
