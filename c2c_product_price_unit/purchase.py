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
# Purchase Line INHERIT
#----------------------------------------------------------
class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _logger = logging.getLogger(__name__)

    def _get_default_id(self, cr, uid, context=None):
    
        pu = self.pool.get('c2c_product.price_unit')
        #if not pu: return 1.0
        self._logger.debug('purch get default `%s`', pu)
        return pu.get_default_id(cr, uid, context)

    def _get_default_price_unit_pu(self, cr, uid, price_unit_id, context=None):
        pu = self.browse(cr, uid, price_unit_id)
        res  = 0.0
        if not pu:
            return res
        for p in pu:
            res = p.price_unit
        return res

    _columns = \
        { 'price_unit_id' : fields.many2one('c2c_product.price_unit','Price Unit', required=True)
        , 'price_unit_pu' : fields.float
            ( string='Unit Price PU'
            , digits_compute=dp.get_precision('Purchase Price')
            , required=True
            , help='Price using "Price Units"'
            )
        , 'price_unit'    : fields.float
            ( 'Unit Price Internal'
            , required=True
            , digits=(16,8)
            , help="""Product's cost for accounting stock valuation. It is the base price for the supplier price."""),
        }
    _defaults = {
        'price_unit_id'   : _get_default_id,
        'price_unit_pu'   : _get_default_price_unit_pu,
        'price_unit'      : 0.0
        }

    def init(self, cr):
        cr.execute("""
            update purchase_order_line set price_unit_pu = price_unit  where price_unit_pu is null;
        """)
        cr.execute("""
            update purchase_order_line set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
        """)
#        price_unit_obj = self.pool.get('c2c_product.price.unit') 
#        puid = price_unit_obj.search(cr, uid, [('coefficient', '=', 1)])
#        ids = self.search(cr, uid, [('price_unit_pu','=', False)])
#        for pos in self.browse(cr, uid, ids):
#            self.write(cr, uid, pos.id, { 'price_unit_pu': price_unit, 'price_unit_id': puid })
            
            

    def product_id_change_2c2_pu(self, cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=False, fiscal_position=False, date_planned=False,
            name=False, price_unit_pu=False, notes=False, price_unit_id=False ):
        res = {}
        self._logger.debug('purch `%s` `%s`', price_unit_id, price_unit_pu)

        if product:
            prod = self.pool.get('product.product').browse(cr, uid, product)
            res['value'] = super(purchase_order_line, self).product_id_change( cr, uid, ids, pricelist, product, qty, uom,
                partner_id, date_order, fiscal_position, date_planned,
                name, price_unit_pu, notes)['value']
            if not price_unit_id:
                price_unit_id = prod.price_unit_id.id
            coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
            #if not price_unit_pu:
            #     price_unit_pu = prod.price_unit_pu

            self._logger.debug('purch -68a-  `%s` `%s`', price_unit_id, price_unit_pu)
            self._logger.debug('purch -68b-  `%s`', res['value'])

            res['value']['price_unit_id'] = price_unit_id
            res['value']['price_unit_pu'] =  res['value']['price_unit'] * coeff
            #res['value']['price_unit']    = price_unit_pu / float(coeff)
            self._logger.debug('purch -68c-  `%s`', res['value'])
        return res


    def onchange_price_unit(self, cr, uid, ids, field_name,qty,price_pu, price_unit_id):
        self._logger.debug('purch -68c-a  `%s` `%s` `%s`', field_name, price_pu, price_unit_id)
        res = {}
        if  price_pu and  price_unit_id and qty:
            self._logger.debug('purch -68c-b  `%s`', field_name)
            coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
            self._logger.debug('purch -68c-c  `%s` `%s`', field_name,coeff)
            price = price_pu / float(coeff)
            self._logger.debug('purch -68c-d  `%s``%s``%s`', field_name, price, coeff)
            return {'value': {field_name : price}}
        return res

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def inv_line_create(self, cr, uid, a, ol):
        line = super(purchase_order, self).inv_line_create(cr, uid, a, ol)
        self._logger.debug('po line `%s`', line)
        #return (0, False, {
        #    'name': ol.name,
        #    'account_id': a,
        #    'price_unit': ol.price_unit or 0.0,
        #    'price_unit_pu': ol.price_unit_pu or 0.0,
        #    'price_unit_id': ol.price_unit_id.id,
        #    'quantity': ol.product_qty,
        #    'product_id': ol.product_id.id or False,
        #    'uos_id': ol.product_uom.id or False,
        #    'invoice_line_tax_id': [(6, 0, [x.id for x in ol.taxes_id])],
        #    'account_analytic_id': ol.account_analytic_id.id or False,
        #})

        price_unit_pu =  ol.price_unit_pu or 0.0
        self._logger.debug('price_unit_pu `%s`', price_unit_pu)
        self._logger.debug('price_unit_id `%s`', ol.price_unit_id.id)
        #FIXME
        line[2]['price_unit_pu'] = price_unit_pu
        line[2]['price_unit_id'] = ol.price_unit_id.id
        #the 2 values have to be written to the line
        #line['value'].update({'price_unit_pu' : price_unit_pu, 'price_unit_id' : ol.price_unit_id.id })
        self._logger.debug('po line after `%s`', line)
        return line


    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        res = super(purchase_order,self)._prepare_order_line_move( cr, uid, order, order_line, picking_id, context)
        price_unit_id = order_line.price_unit_id.id
        price_unit_pu = order_line.price_unit_pu
        res.update({'price_unit_id' : price_unit_id,'price_unit_pu' : price_unit_pu})
        return res

purchase_order()
