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

from openerp.osv import osv, fields
#import openerp.addons.decimal_precision as dp

import re  
from openerp.tools.translate import _
        
        
#----------------------------------------------------------
#  generel Interest
#----------------------------------------------------------

class account_company_interest(osv.osv):
    _name = "account.company.interest"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'), 
        'name'      : fields.char('Interest Name', size=32),
        'interest_rate_ids' : fields.one2many('account.company.interest.rate', 'company_interest_rate_id', 'Interest Rates'),
    }
     
account_company_interest()

class account_company_interest_rate(osv.osv):
    _name = "account.company.interest.rate"
    _columns = {
        'company_interest_rate_id': fields.many2one('account.company.interest', 'Interest Rate'),     
        'interest_rate_debit': fields.float('Interest Debit', required=True,   digits=(7,4)),
        'interest_rate_credit': fields.float('Interest Credit', required=True,  digits=(7,4) ),
        'date_from': fields.date('Date From',required=True),
        'date_to': fields.date('Date To'),
     }
account_company_interest_rate()

#----------------------------------------------------------
#  Account specific Interest
#----------------------------------------------------------
class account_account_interest(osv.osv):
    _name = "account.account.interest"
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),     
        'account_id': fields.many2one('account.account', 'Account', required=True, ondelete="cascade"),
        'interest_rate_debit': fields.float('Interest Debit', required=True,   digits=(7,4)),
        'interest_rate_credit': fields.float('Interest Credit', required=True,  digits=(7,4) ),
        'date_from': fields.date('Date From',required=True),
        'date_to': fields.date('Date To'),
     }
account_account_interest()

class account_account(osv.osv):
    _inherit = "account.account"
    _columns = {
         'account_interest_ids'         : fields.many2many('account.company.interest','account_company_interest_rel','account_id','account_company_interest_id', 'General Interest Rates'),
         'account_account_interest_ids' : fields.one2many('account.account.interest', 'account_id', 'Interest Rates'),
    }
account_account()