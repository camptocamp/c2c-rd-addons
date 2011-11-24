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
import decimal_precision as dp

import math
#from _common import rounding
import re  
from tools.translate import _
        
import sys


#----------------------------------------------------------
# Sale Line INHERIT
#----------------------------------------------------------
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'price_unit_id'    : fields.many2one('c2c_product.price_unit','Price Unit', required=True),
        'price_unit_pu'    : fields.float(string='Unit Price',digits_compute=dp.get_precision('Sale Price') , required=True, \
                            help='Price using "Price Units"') ,
        'price_unit'       : fields.float(string='Unit Price internal', required=True, digits=(16, 8), \
                            help="""Product's cost for accounting stock valuation. It is the base price for the supplier price."""),
    }

    def init(self, cr):
      cr.execute("""
          update sale_order_line set price_unit_pu = price_unit  where price_unit_pu is null;
      """)
      cr.execute("""
          update sale_order_line set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
      """)

    #def product_id_change_c2c_pu(self, cr, uid, ids, pricelist, product, qty=0,
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False,context={}):
       res = {}
       res['value'] = super(sale_order_line, self).product_id_change( cr, uid, ids, pricelist, product, qty, 
            uom, qty_uos, uos, name, partner_id, 
            lang, update_tax, date_order, packaging, fiscal_position, flag,context)['value']
       print >>sys.stderr,'sale a',   res['value']  
       if product:
           prod = self.pool.get('product.product').browse(cr, uid, product)
           price_unit_id = prod.list_price_unit_id.id
           print >>sys.stderr,'sale pu',   price_unit_id, product, u'prod.name'
           res['value']['price_unit_id'] = price_unit_id
     
           if res['value']['price_unit'] and qty:
               coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
               res['value']['price_unit_pu'] = res['value']['price_unit'] * coeff * qty
               print >>sys.stderr,'sale 2',coeff, res['value']['price_unit'],   res['value']  
       return res

    def onchange_price_unit(self, cr, uid, ids, field_name,qty, price_pu, price_unit_id):
        if  price_pu and  price_unit_id and qty:
            coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
            price = price_pu / float(coeff) * qty
            return {'value': {field_name : price}}
        return False

sale_order_line()

class sale_order(osv.osv):
    _inherit = "sale.order"

    # FIXME define ship line fields like in purchase order
    # should store price_unit_id for sales

    # FIXME define inv line fields like in purhcase order
    def invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        def _get_line_qty(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos_qty or 0.0
                return line.product_uom_qty
            else:
                return self.pool.get('procurement.order').quantity_get(cr, uid,
                        line.procurement_id.id, context=context)

        def _get_line_uom(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                if line.product_uos:
                    return line.product_uos.id
                return line.product_uom.id
            else:
                return self.pool.get('procurement.order').uom_get(cr, uid,
                        line.procurement_id.id, context=context)

        create_ids = []
        sales = {}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.invoiced:
                if line.product_id:
                    a = line.product_id.product_tmpl_id.property_account_income.id
                    if not a:
                        a = line.product_id.categ_id.property_account_income_categ.id
                    if not a:
                        raise osv.except_osv(_('Error !'),
                                _('There is no income account defined ' \
                                        'for this product: "%s" (id:%d)') % \
                                        (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    a = prop and prop.id or False
                uosqty = _get_line_qty(line)
                uos_id = _get_line_uom(line)
                pu = 0.0
                if uosqty:
                    pu = round(line.price_unit * line.product_uom_qty / uosqty,
                            self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price'))
                fpos = line.order_id.fiscal_position or False
                a = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, a)
                if not a:
                    raise osv.except_osv(_('Error !'),
                                _('There is no income category account defined in default Properties for Product Category or Fiscal Position is not defined !'))
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'origin': line.order_id.name,
                    'account_id': a,
                    'price_unit': pu,
                    'price_unit_pu': line.price_unit_pu,
                    'price_unit_id': line.price_unit_id.id,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                    'note': line.notes,
                    'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                })
                cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                self.write(cr, uid, [line.id], {'invoiced': True})
                sales[line.order_id.id] = True
                create_ids.append(inv_id)
        # Trigger workflow events
        wf_service = netsvc.LocalService("workflow")
        for sid in sales.keys():
            wf_service.trg_write(uid, 'sale.order', sid, cr)
        return create_ids


sale_order()




