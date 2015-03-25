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

'name': 'Product Price Unit',
'version': '0.7',
'category': 'Warehouse Management',
'description': """
Attention the module must be installed and upgraded immediately to complete all modifications

This module allows to define price units
    * price per unit (default)
    * price per 100
    * price per 1000
    * price in cents ...
Example: gasoline is quoted 1 liter i= 115,5 cents or 1,115 €
    diodes 4.99€/1000 Units

The module hides the original price fields and fills these with converted values.
Advantage - no change of the underlying logic of the base model for computation.
Users of the group "Product Price Unit Manager" will see the orginal price fields

Tested with sales/purchase installed

Forms Layout not optimized for group "Product Price Unit Manager" - this is mainly for debugging

ToDo:
    * all onchange on product_id must return default price_unit_id (done for SO/PO,INV)
    * all wizards must transfer price_unit_id and unit_price_pu (many do not work now)
    * all "create" must transfer price_unit_id and unit_price_pu
    * defaults for
        * price_unit_id
        * price_unit_pu (from price_unit)
    * functions using price_unit must probably use price_unit_pu
    * c2c_product.price_unit.xml must be loaded in product.py
before running the update statements
currenty the module must be updated immediately to fill price_unit_id
    * Product
        * Button Udate standard price (average costing)
    * Request For Quotation
        * Form
        * Report
    * Purchase Order
        * Report
    * Leads
    * Quatations
    * Sales Order
        * Form small layout issue
        * Report
    * Warehouse
        * Forms
        * Reports
    * Price Lists
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': ['product', 'purchase', 'hr_expense','account_anglo_saxon', 'c2c_stock_accounting', 'c2c_product_price_unit_id'],
'data': [
              
              'purchase_view.xml',
              'sale_view.xml',
              'stock_view.xml',
              'account_invoice_view.xml',
              'wizard/stock_partial_picking_view.xml',
            ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
