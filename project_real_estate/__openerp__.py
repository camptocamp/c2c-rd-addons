# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligung und Beratung GmbH (<http://www.chricar.at>)
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
    'name': 'Real Estate Project',
    'version': '1.0',
    'category': 'Others',
    'description': """
This module allows to manage real estate projects
Tasks get attributes to allow planning of
* Investment -> depreciation
* Expenses
** commercial law
** tax law (in Austria 
""",
    'author': 'ChriCar Beteiligung und Beratung GmbH',
    'depends': [
"chricar_top"
,"chricar_tenant"
,"chricar_invoice"
,"chricar_room"
,"chricar_equipment"
,"chricar_budget_lines"
,"project_notes"
,"project_date"
,"project_gantt_webkit"
      ],
    'update_xml': ['project_view.xml'],
    #'update_xml': ['product_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
