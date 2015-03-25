# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

'name': 'Product Price Property',
'version': '1.0',
'category': 'Accounting & Finance',
'description': """
Creates a poperty for list and standard price on product (not template).
this allows different prices for variants and companies

ATT - 6.1 has server bug - ir property can not defined on "_inherits" table

Warning : 

- This methode will not work if prices are used through SQL queries in OpenERP. Like
in report.analytic.line.to_invoice or in stock valuation report
- May cause incompatibility in custom module because the data model change

""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [ 'product'],
'data': [
  ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
