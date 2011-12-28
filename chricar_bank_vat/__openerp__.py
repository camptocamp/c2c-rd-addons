# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 Camptocamp Austria (<http://www.camptocamp.at>)
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
     "name"         : "ChriCar Bank Account VAT + Analytic",
     "version"      : "1.0",
     "author"       : "ChriCar Beteiligungs- und Beratungs GmbH",
     "website"      : "http://www.chricar.at/ChriCar",
     "description"  : """
Adds VAT to bank statement lines
does not support
* mulitple VAT per line
       """,
     "category"     : "Accounting & Finance",
     "depends"      : ["account",],
     "init_xml"     : [],
     "demo_xml"     : [],
     "update_xml"   : ["bank_account_vat_view.xml"],
     "active"       : False,
     "installable"  : True
}

