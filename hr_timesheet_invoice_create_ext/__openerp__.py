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
'name'        : 'Adds fields for invoice creation from task work'
, 'version'     : '0.7'
, 'category'    : 'Sales Management'
, 'description' : """
This module will allow to spezify
    * search for partner
    * invoice date, journal
    * automatic calculation of "Clearing period" and setting this as reference
    * prefix for analytic account name
    * remove the default date of today as prefix for analytic account name
    * group all projects in ONE invoice per partner
"""
, 'author'      : 'ChriCar Beteiligungs- und Beratungs- GmbH'
, 'depends'     : [ 'hr_timesheet_invoice' ]
, 'data'  : ['hr_timesheet_invoice_view.xml', 'wizard/hr_timesheet_invoice_create_view.xml']
, 'demo_xml'    : []
, 'installable': False
, 'application'  : False 
, 'active'      : False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
