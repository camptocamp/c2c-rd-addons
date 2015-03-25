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

'name': 'Toggle display of product with 0 Values in stock location analysis',
'version': '1.0',
'category': 'Warehouse Management',
'description': """
Add check to prohibit printing products with Real and Future Value = 0 

****************************************************
REQUIRES patch for filter (and sort) function fields - please see
http://www.camptocamp.com/en/blog/2011/10/sort-and-filter-options-for-function-fields-in-openerp
****************************************************

""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [ 'stock'],
'data': [
'wizard/stock_location_product_view.xml',
  ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
