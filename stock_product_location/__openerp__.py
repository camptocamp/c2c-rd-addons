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

'name': 'Stock Product Location',
'version': '0.8',
'category': 'Warehouse Management',
'description': """
This module defines a default stock location for products and product groups.
This will be used 
    * as destination location for purchases, production, and stock update from
product.
    * as source location for sales and internal moves

""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [ 'product','stock','sale','purchase' ],
'data': ['product_view.xml',
  ],
'demo': [],
'contributors': ['Pedro M. Baeza (pedro.baeza@serviciosbaeza.com)'],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
