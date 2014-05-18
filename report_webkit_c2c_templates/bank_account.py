# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.com>).
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
from openerp.osv import osv
from openerp.osv import fields
import os
import openerp.tools
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval as eval

class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {
       'company_bank_id': fields.many2one('res.partner.bank', 'Bank Account',
            help='Bank Account Number, default own company bank account to be printed with webkit',
            domain="[('partner_id','=',partner_id)]"),
       'commercial_register': fields.char('Commercial Register', size=64, help="Commerical Register to be printed on webkit invoice"),
       'registered_office': fields.char('Registered Office', size=64, help="Register Office to be printed on webkit invoice"),
    }
res_company()

class HeaderHTML(osv.osv):
    _inherit = "ir.header_webkit"

    _columns = {
       'report_company_bank_id': fields.many2one('res.partner.bank', 'Bank Account',
            help='Bank Account Number, company bank account to be printed with this webkit template'),
    }
HeaderHTML()
