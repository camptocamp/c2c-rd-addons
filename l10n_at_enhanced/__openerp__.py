# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) camptocamp.com
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

'name': 'Austria - Accounting enhanced fiscal position',
'version': '1.0',
'author': 'Camptocamp',
'website': 'http://www.camptocamp.com',
'category': 'Localization/Account Charts',
'depends': ['account_chart', 'base_vat', 'l10n_at','xml_template','base_iban'],
'description': """
This module provides an enhanced standard Accounting Chart for Austria which is based on the Template from BMF.gv.at.
=====================================================================================================================
Please keep in mind that you should review and adapt it with your Accountant, before using it in a live Environment.
20130101 enhanced fiscal position configuration by Camptocamp
The fiscal positions defined in l10n_at are set to inactive
20130122 prepare for VAT XML
http://www.bmf.gv.at/EGovernment/FINANZOnline/InformationenfrSoft_3165/Umsatzsteuervoranme_11373/_start.htm
""",
'demo': [],
'data': ['account_tax.xml','wizard/account_vat_view.xml'],
'auto_install': False,
'installable': False
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
