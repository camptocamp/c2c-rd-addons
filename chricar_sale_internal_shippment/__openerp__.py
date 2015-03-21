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

'name': 'Sale order internal picking',
'version': '0.9',
'category': 'Sales Management',
'description': """
This module adds an extra internal picking to sale order on request
Purpose
SO
-> internal: shiping products to company location at customer site
-> out: from company location at customer site to customer
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [ 'base','sale','stock' ],
'data': ['sale_view.xml','wizard/make_ship_internal.xml',
  ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
