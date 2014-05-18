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

'name': 'Austria - Real Estate minimum chart',
'version': '1.0',
'category': 'Localisation/Account Charts',
'description': """
This module installs a minimum chart of accounts for real estate management tool
No XML data yet - these must be extracted from the database Real Estate templates
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [
   "account", 
   "base_vat", 
   "base_iban",
   "c2c_account_tax_rounding",
 ],
'data': [                
       "l10n_at_chart.xml",
       "l10n_at_tax_code.xml",
       "l10n_at_tax.xml",
       "l10n_at_wizard.xml",
],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
