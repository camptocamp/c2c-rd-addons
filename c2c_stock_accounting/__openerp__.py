# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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
    'name': 'Stock Accounting',
    'version': '0.7',
    'category': 'Warehouse Management',
    'description': """
************** Attention ***************
* Must be intalled without demo data
* the module must be installed and upgraded immediately to complete all modifications
************** Attention ***************

This module adds stock accounting features
* historical evaluation
* stock evaluation matches financial accounting
* analytic account - to create analytc moves derived from stock_moves

ToDo
* valuation field - define at company level (product > function field)
* show value for products
** reuse stock.product.py get_product_available - impossible to inherit / modify sql statement
* stock reports
** partly DONE report/report_stock_move.py - need in/out values for internal locations too
* generate analytic lines       
""",
    'author': 'Camptocamp Austria',
    'depends': ['product','purchase','sale', 'stock', ],
    'update_xml': ['security/stock_security.xml',
                   'stock_view.xml',
       ],
    #'update_xml': ['product_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
