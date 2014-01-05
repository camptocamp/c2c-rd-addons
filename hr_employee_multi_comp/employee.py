# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Ferdinand Gassauer)
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
from osv import fields, osv
import one2many_sorted
import logging

class hr_employee_company(osv.osv):
    _name = "hr.employee.company"
    _description = "Employee Company Specific Data"
    # may be not all necessary
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'company_id': fields.many2one('res.company', 'Company'),
        'department_id':fields.many2one('hr.department', 'Department'),
        'address_id': fields.many2one('res.partner.address', 'Working Address'),
        'work_phone': fields.char('Work Phone', size=32, readonly=False),
        'mobile_phone': fields.char('Work Mobile', size=32, readonly=False),
        'work_email': fields.char('Work E-mail', size=240),
        'work_location': fields.char('Office Location', size=32),
        'notes': fields.text('Notes'),
        'parent_id': fields.many2one('hr.employee', 'Manager'),
        'category_ids': fields.many2many('hr.employee.category', 'employee_category_rel', 'emp_id', 'category_id', 'Categories'),
        'child_ids': fields.one2many('hr.employee', 'parent_id', 'Subordinates'),
        'job_id': fields.many2one('hr.job', 'Job'),
        }
    
hr_employee_company()


class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns = {
        'employee_company_ids': one2many_sorted.one2many_sorted('hr.employee.company', 'employee_id', 'Company Data' , order = 'company_id.name')    
                                
        }

hr_employee()