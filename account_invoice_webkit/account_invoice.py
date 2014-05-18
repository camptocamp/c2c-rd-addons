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

    def _print_ean(self, cr, uid, ids, name, args, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
          print_ean = False
          if inv.company_id.print_ean and inv.invoice_line:
            for line in inv.invoice_line:
                if line.product_id.ean13 :
                   print_ean = True
          res[inv.id] =  print_ean
        return res

    def _print_code(self, cr, uid, ids, name, args, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
          print_code = False
          if inv.invoice_line and inv.company_id.print_code:
            for line in inv.invoice_line:
                if line.product_id.default_code:
                   print_code = True
          res[inv.id] =  print_code
        return res

    def _get_cols(self, cr, uid, ids, name, args, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
          cols = 4
          if inv.print_ean:
             cols += 1
          if inv.print_code:
             cols += 1
          if inv.print_price_unit_id:
             cols += 1
          if inv.amount_discount != 0:
             cols += 1

          res[inv.id] = cols

        return res


    _columns = {
        'note' : fields.text('Notes'),
        'amount_discount': fields.function(_amount_discount, method=True, digits_compute=dp.get_precision('Account'), string='Total Discount',),
        'print_price_unit_id': fields.function(_print_price_unit_id, method=True, type='boolean', string='Print column price unit id if not 1',),
        'print_ean': fields.function(_print_ean, method=True, type='boolean', string='Print EAN if available',),
        'print_code': fields.function(_print_code, method=True, type='boolean', string='Print code if available',),
        'cols': fields.function(_get_cols, method=True, type='integer', string='No of columns before totals',),
        'print_address_info': fields.related('company_id', 'print_address_info', type ='boolen', relation='res.company', string="Print Address Info", readonly = True),
        'print_cell_borders': fields.related('company_id', 'print_cell_borders', type ='boolen', relation='res.company', string="Print Cell Borders", readonly = True),
        'document_label_position': fields.related('company_id', 'document_label_position', type ='boolen', relation='res.company', string="Document Label Position", readonly = True),
        'invoice_line_sorted' : one2many_sorted.one2many_sorted
        ( 'account.invoice.line'
        , 'invoice_id'
        , 'Invoice Lines Sorted'
        , states={'draft': [('readonly', False)]}
        , order  = 'product_id.name,name'
        )
        
    }
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
        'note' : fields.text('Notes'),
        }

account_invoice_line()
