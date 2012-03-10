# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 Camptocamp Austria (<http://www.camptocamp.com>).
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

import time
from lxml import etree
import decimal_precision as dp

import netsvc
import pooler
from osv import fields, osv, orm
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"
         
    def _amount_discount(self, cr, uid, ids, name, args, context=None):
        res = {}
        amount_discount = 0.0
        for invoice in self.browse(cr, uid, ids, context=context):
	  if invoice.invoice_line:
            for line in invoice.invoice_line:
                amount_discount += line.discount
          res[invoice.id] =  amount_discount     
        return res

    def _print_price_unit_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        invoice_line_obj = self.pool.get('account.invoice.line')
        for invoice in self.browse(cr, uid, ids, context=context):
	  print_price_unit_id = False
          if not 'price_unit_id' in invoice_line_obj._columns:
             res[invoice.id] = False
	  elif invoice.invoice_line:
            for line in invoice.invoice_line:
                if line.price_unit_id and line.price_unit_id.coefficient != 1.0:
		   print_price_unit_id = True
          res[invoice.id] =  print_price_unit_id
        return res

    def _get_client_order_ref(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
	  client_order_ref = ''
	  if invoice.picking_ids:
            for pick in invoice.picking_ids:
                if pick.sale_id.client_order_ref :
		   client_order_ref += pick.sale_id.client_order_ref
          res[invoice.id] = client_order_ref 
        return res
        
    _columns = {
        'amount_discount': fields.function(_amount_discount, method=True, digits_compute=dp.get_precision('Account'), string='Total Discount',),
        'print_price_unit_id': fields.function(_print_price_unit_id, method=True, type='boolean', string='Print column price unit id if not 1',),        
        'client_order_ref': fields.function(_get_client_order_ref, method=True, type='char',size='128', string='Customer Reference of Sale Orders',), 
    }
account_invoice()
