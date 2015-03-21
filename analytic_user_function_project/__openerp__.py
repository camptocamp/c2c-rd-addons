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
'name'        : 'Makes product user relation available in projects'
, 'version'     : '0.7'
, 'category'    : 'Sales Management'
, 'description' : """
This module will use the product from user-product-project (analytic account) relation
for timesheet tasks invoicing)
"""
, 'author'      : 'ChriCar Beteiligungs- und Beratungs- GmbH'
, 'depends'     : [ 'analytic_user_function','project_timesheet' ]
, 'data'  : ['analytic_user_function_view.xml','security/ir.model.access.csv']
, 'demo_xml'    : []
, 'installable': False
, 'application'  : False 
, 'active'      : False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
