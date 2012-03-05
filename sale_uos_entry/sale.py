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
import pooler
import time
from osv import fields, osv
from tools.translate import _
import netsvc
import logging


class sale_order_line(osv.osv):
    _inherit = "sale.orderi.line"    

    _columns = {
                 'product_uos_qty_helper': fields.float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}),
    }

    def product_id_change_helper(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):

        qty_coeff =  qty
        if uos and qty_uos != 0 :
            product_obj = self.pool.get('product.product')
            for product in product_obj.browse(cr, uid, [product], context)
                 qty_coeff = qty_uos_helper / product_obj.uos_coeff
            

        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty_coeff,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        return res    
            
sale_order_line()

