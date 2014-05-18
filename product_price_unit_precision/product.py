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

# FIXME remove logger lines or change to debug
 
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp



class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    
    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Purchase Price Unit')),
    }

purchase_order_line()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    _columns = {
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Sale Price'), readonly=True, states={'draft': [('readonly', False)]}),
        }
        
sale_order_line()
        
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
            
    _columns = {
       'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Invoice Price Unit')),
    }
                
account_invoice_line()
