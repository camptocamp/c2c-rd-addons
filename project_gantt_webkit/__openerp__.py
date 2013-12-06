# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

{
    "name" : "Project Gantt Webkit",
    "version" : "1.0",
    "author" : "Camptocamp Austria",
    "category": 'Project',
    'complexity': "easy",
    "description": """
Print Gantt 

Attention:
    * no UTF-8 support
    * only a few tasks supported (API limit?)
    """,
    'website': 'http://www.camptocamp.com',
    "depends" : ["project","report_webkit"],
    'init_xml': [],
    'update_xml': ['project_view.xml'],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
