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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.one2many_sorted as one2many_sorted

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _print_uom(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          print_uom = False
          if order.order_line:
            for line in order.order_line:
                   print_uom = True
          res[order.id] =  print_uom
        return res


    def _print_ean(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          print_ean = False
          if order.order_line and order.company_id.print_ean:
            for line in order.order_line:
                if line.product_id.ean13 :
                   print_ean = True
          res[order.id] =  print_ean
        return res

    def _print_code(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            print_code = False
            if order.order_line:
                for line in order.order_line:
                    if line.product_id.default_code:
                        print_code = True
                        res[order.id] =  print_code
        return res
                            
    def _get_cols(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
          cols = 2
          if order.print_uom:
             cols += 2
          if order.print_ean:
             cols += 1
          if order.print_code:
             cols += 1
           
          res[order.id] = cols

        return res


    _columns = {
                 'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
              'incoterm': fields.many2one('stock.incoterms', 'Incoterm', help="Incoterm which stands for 'International Commercial terms' implies its a series of sales terms which are used in the commercial transaction."),

              'print_uom': fields.function(_print_uom, method=True, type='boolean', string='Print UoM if different from UoS',),
              'print_ean': fields.function(_print_ean, method=True, type='boolean', string='Print EAN if available',),
              'print_code': fields.function(_print_code, method=True, type='boolean', string='Print code if available',),
              'cols': fields.function(_get_cols, method=True, type='integer', string='No of columns before totals',),
              'order_line_sorted' : one2many_sorted.one2many_sorted
              ( 'purchase.order.line'
              , 'order_id'
              , 'Order Lines Sorted'
              , states={'draft': [('readonly', False)]}
              , order  = 'product_id.name,name'
              ),
#              'order_line' : one2many_sorted.one2many_sorted
#              ( 'purchase.order.line'
#              , 'order_id'
#              , 'Order Lines Sorted'
#              , states={'draft': [('readonly', False)]}
#              , order  = 'product_id.name,name'
#              ),
              
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        res = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        partner = self.pool.get('res.partner')
        if partner_id :
            supplier = partner.browse(cr, uid, partner_id)
            payment_term_id = supplier.property_payment_term_supplier.id
            if payment_term_id:
               res['value']= {'payment_term': payment_term_id,}
        return res

purchase_order()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'property_payment_term_supplier': fields.property(
            type='many2one',
            relation='account.payment.term',
            string ='Supplier Payment Term',
            view_load=True,
            help="This payment term will be used instead of the default one for the current partner as supplier"),
      }

res_partner()
