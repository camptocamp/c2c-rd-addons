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
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging
import openerp.addons.decimal_precision as dp


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"    


    def _parcel_qty(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            if sale.product_packaging and sale.product_packaging.qty:
                res[sale.id] = sale.product_uom_qty / sale.product_packaging.qty 
            else:
                res[sale.id] = None
        return res

    _columns = {
        'product_uos_qty_helper': fields.float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}),
        'parcel_qty': fields.function(_parcel_qty, string='Parcel Qty', type='float'),
        'content_qty':fields.related('product_packaging','qty',type='float',string='Content Qty',readonly=True, store=True),

    }

    def product_id_change_helper(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        _logger = logging.getLogger(__name__)
        _logger.debug('FGF sale uos' )

        qty_helper =  qty
        if product and uos and qty_uos != 0 :
            _logger.debug('FGF sale uom,uos ,qty, qty_uos %s,%s,%s,%s' %( uom,uos, qty, qty_uos ))
            product_obj = self.pool.get('product.product')
            for prod in product_obj.browse(cr, uid, [product], context):
                 qty_helper = qty_uos / (prod.uos_coeff or 1)
                 #qty_helper = qty_uos / 0.004
            
        _logger.debug('FGF sale uos qty_helper %s' % (qty_helper) )

        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty_helper,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        _logger.debug('FGF sale uos res %s' % (res) )
        res['value']['product_uom_qty'] = qty_helper
        return res    
            
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        _logger = logging.getLogger(__name__)
        _logger.debug('FGF sale uos product %s qty %s' % (product,qty))

        #FIXME - must set product_packaging and qty to the minimum multiple found in product_packaging
        product_obj = self.pool.get('product.product')
        qty2= qty
        if product:
          for products in product_obj.browse(cr, uid, [product], context):
            if products.packaging and products.packaging[0].qty and qty == 1 and products.packaging[0].qty != 1 :
                qty2 = products.packaging[0].qty
        _logger.debug('FGF sale uos product %s qty2 %s' % (product,qty2))
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty2,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        res['value']['product_uos_qty_helper'] = res['value']['product_uos_qty']
        _logger.debug('FGF sale uos res %s' % (res) )
        return res    


sale_order_line()

