# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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
{ 'name'        : 'Timesheet recording for farm'
, 'version'     : '0.9'
, 'category'    : 'HR'
, 'description' : """
Fast recording of working time per day and distribution of hours to lots  
"""
, 'author'      : 'ChriCar Beteiligungs- und Beratungs- GmbH'
, 'depends'     : ['hr_timesheet' ]
, 'update_xml'  : ['hr_timesheet_farm.xml']
, 'demo_xml'    : []
, 'installable' : True
, 'active'      : False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
