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

{ 'sequence': 500,

"name" : "Sale Invoice manual Link",
"version" : "1.1",
"author" : "ChriCar Beteiligungs- und Beratungs- GmbH",
"category": 'Sale Management',
'complexity': "easy",
"description": """
Allow to add (and remove) invoices to (from) Sale Order manually
=====================================

""",
'website': 'http://www.camptocamp.com',
"depends" : ["c2c_sale_multi_partner"],
'init_xml': [],
'data': ['sale_view.xml'],
'demo_xml': [],
'installable': False,
'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
