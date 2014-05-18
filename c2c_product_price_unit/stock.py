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
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import logging
#----------------------------------------------------------
#  Account Invoice Line INHERIT
#----------------------------------------------------------
class stock_move(osv.osv):
    _inherit = "stock.move"

    def _get_price_unit_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('product_id', False):
            return False
        pu_id = self.pool.get('product.product').browse(cr, uid, context['product_id']).price_unit_id.id
        return pu_id or False


    _columns = {
        'price_unit_id'    : fields.many2one('c2c_product.price_unit','Price Unit'),
        'price_unit_pu'    : fields.float(string='Unit Price',digits_compute=dp.get_precision('Sale Price'),  \
                            help='Price using "Price Units"') ,
        'price_unit'       : fields.float(string='Unit Price internal',  digits=(16, 8), \
                            help="""Product's cost for accounting stock valuation."""),
        'price_unit_sale'  : fields.float(string='Unit Price Sale',  digits=(16, 8), \
                            help="""Product's sale for accounting stock valuation."""),

        'price_unit_sale_id' : fields.many2one('c2c_product.price_unit','Price Unit Sale'),
        'price_unit_coeff':fields.float(string='Price/Coeff internal',digits=(16,8) ),

    }

    _defaults = {
        'price_unit_id'   : _get_price_unit_id,
#        'price_unit_pu'   : _get_price_unit_pu,
#        'price_unit'      : _get_price_unit,
    }

    def init(self, cr):
        cr.execute("""
            update stock_move set price_unit_pu = price_unit  where price_unit_pu is null;
        """)
        cr.execute("""
            update stock_move set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
        """)

    def onchange_price_unit(self, cr, uid, ids, field_name,price_pu, price_unit_id):
        if  price_pu and  price_unit_id:
            pu = self.pool.get('c2c_product.price_unit').browse(cr, uid, price_unit_id)
            price = price_pu / float(pu.coefficient)
            return {'value': {field_name : price}}
        return {}

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, address_id=False):
        context = {}
        res = super(stock_move,self).onchange_product_id( cr, uid, ids, prod_id, loc_id,
                            loc_dest_id, address_id)
        if prod_id :
            prod_obj = self.pool.get('product.product').browse(cr, uid, prod_id)
            pu_id = prod_obj.price_unit_id.id
            standard_price_pu = prod_obj.standard_price_pu
            res['value'].update({'price_unit_id':pu_id, 'price_unit_pu':standard_price_pu})
        return res


stock_move()

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _logger = logging.getLogger(__name__)

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        '''Call after the creation of the invoice line'''
        #res = super(stock_picking,self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)
        self._logger.debug('price unit stock line hook FGF: `%s`', invoice_line_id)
        price_unit_id = ''
        price_unit_pu = ''
        if move_line.price_unit_id:
            price_unit_id =  move_line.price_unit_id.id
        if move_line.price_unit_pu:
            price_unit_pu =  move_line.price_unit_pu
        if not price_unit_id or not price_unit_pu:
            if move_line.purchase_line_id:
                if not move_line.price_unit_id:
                    price_unit_id = self.pool.get('c2c_product.price_unit').get_default_id(cr, uid, None)
                else:
                    price_unit_id = move_line.price_unit_id.id
                coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
                self._logger.debug('price_unit invoice_line-hook coeff: `%s`', coeff)
                price_unit_pu = move_line.price_unit_pu or move_line.price_unit * coeff or ''
            if move_line.sale_line_id:
                coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, move_line.price_unit_sale_id.id)
                price_unit = move_line.price_unit_sale or ''
                price_unit_pu = move_line.price_unit_sale * coeff or ''
                price_unit_id = move_line.price_unit_sale_id.id or ''

        inv_line_obj = self.pool.get('account.invoice.line')
        inv_line_obj.write(cr, uid, invoice_line_id, {'price_unit_id': price_unit_id, 'price_unit_pu': price_unit_pu})

        return  super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)

stock_picking()
