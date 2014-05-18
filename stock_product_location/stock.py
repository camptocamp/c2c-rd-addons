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
from openerp.osv import orm

class stock_move(orm.Model):
    _inherit= "stock.move"

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, address_id=False):
        res = super(stock_move,self).onchange_product_id( cr, uid, ids, prod_id, loc_id,
                            loc_dest_id, address_id)
        if prod_id :
            product_obj = self.pool.get('product.product').browse(cr, uid, prod_id, context=False)
            product_loc_id = product_obj.property_stock_location.id or  product_obj.categ_id.property_stock_location.id or ''
            if loc_id:
               loc = self.pool.get('stock.location').browse(cr, uid, loc_id, context=False)
               if loc.usage == 'supplier':
                   res['value']['location_dest_id'] = product_loc_id
            else:
                   res['value']['location_id'] = product_loc_id
            
        return res
