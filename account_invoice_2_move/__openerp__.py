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

"name" : "Adds links to unreconciled partner moves",
"version" : "1.0",
"author" : "ChriCar Beteiligungs- und Beratungs- GmbH",
"category": 'Accounting & Finance',
'complexity': "normal",
"description": """
link from invoice and partner to unreconciled journal items (move lines)
add search buttons for payables and receivables to search view for journal items
==================================

""",
'website': 'http://www.camptocamp.com',
"depends" : ["account","picking_invoice_rel"],
'init_xml': [],
'data': ['account_invoice_view.xml'],
'demo_xml': [],
'installable': False,
'auto_install': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
