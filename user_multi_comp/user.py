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

class res_users_company(osv.osv):
    _name = "res.users.company"
    _description = "User Company Specific Data"
    # may be not all necessary
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_mail': fields.char('Email', size=240, help="Email for this company"),
        'signature': fields.text('Signature', help="Signature for this company"),
        }
    
res_users_company()


class hr_employee(osv.osv):
    _inherit = "res.users"
    _columns = {
        'user_company_ids': one2many_sorted.one2many_sorted('res.users.company', 'user_id', 'Company Data' , order = 'company_id.name')    
                                
        }

hr_employee()