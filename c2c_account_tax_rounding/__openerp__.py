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

'name': 'Account Tax - simulate vertical calculation ',
'version': '1.0',
'category': 'Accounting & Finance',
'description': """
Default tax calculation is per line including rounding of tax amount per line.
This module turns off rounding per line and per tax, hence simulation vertical calculation
standard: tax = sum(round(net*tax))  (~decimal)
this: tax = sum(net*tax)  (~float)
WARNING - in extremely rare cases this may also produce another result than 
sum(net)*tax 
which is the desired outcome.
Set "Rounding Precision" in Tax definiton.
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [ 'account'],
'data': [
'account_view.xml',
  ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
