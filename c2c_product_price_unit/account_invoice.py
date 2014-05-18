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
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _logger = logging.getLogger(__name__)

    def _get_default_id(self, cr, uid, price_unit_id, context=None):
        self._logger.debug('invoice pi_id `%s`', price_unit_id)
        pu = self.pool.get('c2c_product.price.unit')
        if not pu: return
        res =  pu.get_default_id(cr, uid, price_unit_id, context)
        self._logger.debug('invoice default price_unit_id `%s`', res)
        return res

    _columns = {
        'price_unit_id'    : fields.many2one('c2c_product.price_unit','Price Unit' ),
        'price_unit_pu'    : fields.float(string='Unit Price',digits_compute=dp.get_precision('Sale Price'),  \
                            help='Price using "Price Units"') ,
        'price_unit'       : fields.float(string='Unit Price internal',  digits=(16, 8), \
                            help="""Product's cost for accounting stock valuation."""),
    }
    _defaults = {
        'price_unit_id'   : _get_default_id,
    }

    def init(self, cr):
        cr.execute("""
            update account_invoice_line set price_unit_pu = price_unit  where price_unit_pu is null;
        """)
        cr.execute("""
            update account_invoice_line set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
        """)

    def product_id_change_c2c_pu(self, cr, uid, ids, product, uom, qty=0, name='',
           type=False, partner_id=False, fposition_id=False, price_unit_pu=False,
           address_invoice_id=False, currency_id=False, company_id=None,price_unit_id=None):
        res = {}
        self._logger.debug('invoice `%s` `%s`', price_unit_id, price_unit_pu)

        if product :
            context ={}
            res['value'] = super(account_invoice_line, self).product_id_change( cr, uid, ids, product, uom, qty, name,
                type, partner_id, fposition_id, price_unit_pu, address_invoice_id, currency_id, context)['value']
            prod = self.pool.get('product.product').browse(cr, uid, product)
            if type in ['out_invoice','out_refund']:
                price_unit_id = prod.list_price_unit_id.id
            if not price_unit_id:
                price_unit_id = prod.price_unit_id.id

            coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
            price_unit_pu = res['value']['price_unit'] *coeff
            self._logger.debug('invoice res `%s`', res['value'])

            res['value']['price_unit_id'] = price_unit_id
            res['value']['price_unit_pu'] = price_unit_pu

        return res

    def onchange_price_unit(self, cr, uid, ids, field_name, qty, price_pu, price_unit_id):
        res = {}
        if  price_pu and  price_unit_id and qty:
            coeff = self.pool.get('c2c_product.price_unit').get_coeff(cr, uid, price_unit_id)
            price = price_pu / float(coeff)
            self._logger.debug('invoice res q `%s` `%s` `%s` `%s` `%s`', field_name,qty,price_pu,price_unit_id,price)
            return {'value': {field_name : price}}
        return res

    def create(self, cr, uid, vals, context=None, check=True):
        if not vals.get('price_unit_pu') and vals.get('price_unit'):
            vals['price_unit_pu'] = vals['price_unit']
        return super(account_invoice_line, self).create(cr, uid, vals, context=context)


account_invoice_line()


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _refund_cleanup_lines(self, cr, uid, lines):
        for line in lines:
            if line.get('price_unit_id'):
                line['price_unit_id'] = line['price_unit_id'][0]
        res = super(account_invoice, self)._refund_cleanup_lines(cr, uid, lines)
        if res:
            resd = res[0][2]
            resd['price_unit_id'] =  line['price_unit_id']
            res = [(res[0][0], res[0][1], resd)]
        return res


account_invoice()
