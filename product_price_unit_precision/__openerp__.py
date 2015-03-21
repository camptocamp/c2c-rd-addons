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

"name" : "Product Price Unit Precision",
"version" : "1.1",
"author" : "ChriCar Beteiligungs- und Beratungs- GmbH",
"category": 'Accounting & Finance',
'complexity': "normal",
"description": """
Allows to specify independent decimal precision.
=================================================

This module allows to set the following precisions for
    * price_unit
    * sub_total
for the following tables
    * purchase
    * sale
    * invoice

for obvious reasons the price_units should have the same precision in all modules

OpenERP calculates
quantity * price_unit = value(net)
and this should return the same value in all objects

Hence SO/PO and invoice should have the same precision to be consistent.
Invoice must have in any case the max(SO/PO precision)


""",
'website': 'http://www.camptocamp.com',
"depends" : ["account","sale","purchase"],
'init_xml': [],
'data': ["product_data.xml"],
'demo_xml': [],
'installable': False,
'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
