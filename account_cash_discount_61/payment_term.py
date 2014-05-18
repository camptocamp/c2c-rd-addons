# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
from openerp.osv import fields, osv


class account_payment_term(osv.osv):
    _inherit = "account.payment.term"
    _columns = {
         'is_discount': fields.boolean('Is Cash Discount', help="Check this box if this payment term is a cash discount. If cash discount is used the remaining amount of the invoice will not be paid")
    }
account_payment_term()


class account_payment_term_line(osv.osv):
    _inherit = "account.payment.term.line"

    _columns = {
        'is_discount': fields.related('payment_id','is_discount', type='boolean', string='Is Cash Discount', readonly=True) ,
        'discount': fields.float('Discount (%)', digits=(4,2), ),
        'discount_income_account_id': fields.property(type='many2one', relation='account.account', string='Discount Income Account',  view_load=True, 
              help="This account will be used to post the cash discount income"),
        'discount_expense_account_id': fields.property(type='many2one', relation='account.account', string='Discount Expense Account',  view_load=True,
              help="This account will be used to post the cash discount expense"),
    }

    def onchange_discount(self, cr, uid, ids, discount):
        if not discount: return {}
        # FIXME FGF 20140212
        result = {}
        result = {'value': { 'value_amount': round(1-(discount/100.0),2), }}
        return result

account_payment_term_line()
