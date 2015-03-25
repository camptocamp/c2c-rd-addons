# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
"name"         : "ChriCar Account Analytic"
, "version"      : "1.0"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at/ChriCar"
, "description"  : """
Allows to define analytic accounts and their usage for accounts.
It is especially IMPORTANT to assign default analytic accounts to all P&L accounts which are created automatically.

*init* will set all P&L accounts to have mandatory analytic accounts and all other accounts to not allowed.

checks implemented:

    * main - will check/prohibit everything what comes in wrong from other modules

    * ./account/account_move_line.py

    * other checks implemented

    * ./account/account_bank_statement.py
    * ./account/invoice.py

potentially important

    * ./purchase/purchase.py
    * ./sale/sale.py

other - naming !!!

    * analytic_account_id

    * ./account_analytic_plans/account_analytic_plans.py
    * ./account_budget/crossovered_budget.py
    * ./c2c_budget_chricar/c2c_budget_line.py
    * ./report_timesheet/report_timesheet.py
    * account_analytic_id

    * ./account_asset/account_asset.py
    * ./account_voucher/voucher.py
    * ./auction/auction.py
"""
, "category"     : "Accounting & Finance"
, "depends"      : ["account", "chricar_bank_vat", "sale", "stock"]
, "init_xml"     : []
, "demo"         : []
, "data"   : ["account_analytic_view.xml"]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
