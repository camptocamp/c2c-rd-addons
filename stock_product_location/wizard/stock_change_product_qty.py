# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
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

from openerp.osv import orm

class stock_change_product_qty(orm.TransientModel):
    _inherit = "stock.change.product.qty"

    def default_get(self, cr, uid, fields, context=None):
        """ Overriden method to set product or category default location.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        product_id = context and context.get('active_id') or False
        res = super(stock_change_product_qty, self).default_get(cr, uid,
                                        fields, context=context)
        if not res:
            res = {}
        if 'location_id' in fields and product_id:
            product_obj = self.pool.get('product.product')
            product = product_obj.browse(cr, uid, product_id, context=context)
            res['location_id'] = (product.property_stock_location.id or
                                  product.categ_id.property_stock_location.id or
                                  False)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
