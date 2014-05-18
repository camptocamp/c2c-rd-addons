#  -*- coding: utf-8 -*-
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
#----------------------------------------------------------
# Price Unit
#----------------------------------------------------------
class c2c_product_price_unit(osv.osv):
    _name = "c2c_product.price_unit"
    _description = 'Product Price Unit'
    _columns = {
       'code'               : fields.char    ('PU', size=3,  translate=True, help="a 3 char code to pe placed next to the price"),
       'coefficient'        : fields.integer ('Coefficient', required=True, help="Values will be calculated as price / coefficient "),
       'name'               : fields.char    ('Price per Unit', size=32, required=True, translate=True, help="Enter something like: Price for 100 units"),
    }
    _order = "coefficient asc,name"

    def get_coeff(self, cr, uid, price_unit_id, context=None):
    #def get_coeff(self, cr, uid, price_unit_id):
        if not context:
            context = {}

        coeff = 1.0
        if price_unit_id:
            cr.execute('select coefficient from c2c_product_price_unit where id=%s' , (price_unit_id,))
        #res = cr.fetchone()[0] or 1.0
            coeff = cr.fetchone()[0]
        return coeff

    def get_default_id(self, cr, uid, context=None):
        if context is None:
            context = {}

        #if not price_unit_id:
        cr.execute('select min(id) from c2c_product_price_unit where coefficient=1' )
        #res = cr.fetchone()[0] or 1.0
        price_unit_id = cr.fetchone()[0] or ''
        return price_unit_id


c2c_product_price_unit()


#----------------------------------------------------------
# Product INHERIT
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = "product.template"


    def _get_default_id(self, cr, uid, price_unit_id, context=None):
        pu = self.pool.get('c2c_product.price.unit')
        if not pu: return
        return pu.get_default_id(cr, uid, price_unit_id, context)

    _columns = {
        'price_unit_id'    :fields.many2one('c2c_product.price_unit','Price Unit'),
        'standard_price_pu':fields.float(string='Cost Price PU',digits_compute=dp.get_precision('Purchase Price') , \
                            help='Price using "Price Units"') ,
        'list_price_unit_id'    :fields.many2one('c2c_product.price_unit','Price Unit'),
        'list_price_pu'    :fields.float(string='List Price PU',digits_compute=dp.get_precision('Sale Price'), \
                            help='Price using "Price Units"'),
        'standard_price'   :fields.float(string='Cost Price',  digits=(16, 8), help="Product's cost for accounting stock valuation. It is the base price for the supplier price."),
        'list_price'       :fields.float('Sale Price', digits=(16, 8), help="Base price for computing the customer price. Sometimes called the catalog price."),

    }
    def init(self, cr):
        cr.execute("""
  update product_template set standard_price_pu=standard_price  where standard_price_pu is null;
        """)
        cr.execute("""
  update product_template set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
        """)
        cr.execute("""
  update product_template set list_price_pu=list_price  where list_price_pu is null;
        """)
        cr.execute("""
  update product_template set list_price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where list_price_unit_id is null;
        """)

    _columns = {
        'price_unit_id'    :fields.many2one('c2c_product.price_unit','Price Unit', required=True),
        'standard_price_pu':fields.float(string='Cost Price PU',digits_compute=dp.get_precision('Purchase Price') , required=True, \
                            help='Price using "Price Units"') ,
        'list_price_unit_id'    :fields.many2one('c2c_product.price_unit','Price Unit', required=True),
        'list_price_pu'    :fields.float(string='List Price PU',digits_compute=dp.get_precision('Sale Price'), \
                            help='Price using "Price Units"'),
        'standard_price'   :fields.float(string='Cost Price', required=True, digits=(16, 8), help="Product's cost for accounting stock valuation. It is the base price for the supplier price."),
        'list_price'       :fields.float('Sale Price', digits=(16, 8), help="Base price for computing the customer price. Sometimes called the catalog price."),

    }
    _defaults = {
        'price_unit_id'   : _get_default_id,
        'standard_price_pu': 0.0,
        'list_price_unit_id'   : _get_default_id,
        'list_price_pu': 0.0,
        'standard_price': 0.0,


    }
    def init(self, cr):
        cr.execute("""
  update product_template set standard_price_pu=standard_price  where standard_price_pu is null;
        """)
product_template()

class product_product(osv.osv):
    _inherit = "product.product"
    def onchange_price_unit(self, cr, uid, ids, field_name,price_pu, price_unit_id):
        if  price_pu and  price_unit_id:
            pu = self.pool.get('c2c_product.price_unit').browse(cr, uid, price_unit_id)
            price = price_pu / float(pu.coefficient)
            return {'value': {field_name : price}}
        return False

product_product()
