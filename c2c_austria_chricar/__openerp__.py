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

'name': 'ChriCar Beteiligungs- und Beratungs- GmbH ChriCar',
'version': '1.0',
'category': 'Others',
'description': """
This module installs everything we need for Austrian chricar extension
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [
"c2c_austria_extension"
#,"hr_contract_timesheet" 
,"chricar_budget"
,"chricar_budget_lines"
,"chricar_liquidity_plan"
,"chricar_stock_care"
,"chricar_stock_dispo_production_V1"
,"chricar_stocklocation_moves"
,"chricar_stock_weighing"
#,"chricar_tools_export"
,"chricar_stock_product_by_location"
,"chricar_stock_product_production"
,"chricar_inventory"
,"sale_shipped_rate"
 ],
'data': [       ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
