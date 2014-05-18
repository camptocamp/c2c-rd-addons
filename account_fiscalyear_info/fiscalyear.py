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
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.one2many_sorted as one2many_sorted

class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"

    _columns = {
        'date_balance_resulution'   : fields.date("Balance Resolution")
        , 'date_balance_file_reg'   : fields.date("Balance filed to Commercial Register")
        , 'date_balance_publish'    : fields.date("Balance Publishing")
        , 'date_tax_file'           : fields.date("Tax filed to Authorities")
        , 'date_tax_assessed'       : fields.date("Tax assesed by Authorities")
        , 'date_tax_audit'          : fields.date("Tax Audit")
        , 'date_payroll_tax_audit'  : fields.date("Payroll Tax Audit")
    }
account_fiscalyear()
