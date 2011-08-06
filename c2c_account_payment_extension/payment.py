# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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

from osv import osv, fields
#import decimal_precision as dp

import re  
from tools.translate import _

#----------------------------------------------------------
#  Payment type - minimum payment 
# Idea payment should only take place if the acrued amount exceeds this limit
#----------------------------------------------------------
class payment_type(osv.osv):
    _inherit='payment.type'
    _description='Payment types'
    _columns = {
        'amount_partner_min': fields.float('Minimum Payment', help="Minimum payment per partner", digits=(16, 2)),
    }
payment_type()
       
#----------------------------------------------------------
#  Partner
#----------------------------------------------------------
class res_partner(osv.osv):
    _inherit='res.partner'
    _columns={
       'payment_block': fields.boolean('Payment Block', help="Do not include invoices of this account in payment selection"),
    }
    _defaults = {'payment_block': lambda *a: False}
res_partner()    

#----------------------------------------------------------
#  Invoice
#----------------------------------------------------------
class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
        'payment_block': fields.boolean('Payment Block', help="Do not include this invoice in payment selection"),
    }
    _defaults = {'payment_block': lambda *a: False}
account_invoice()           
    
