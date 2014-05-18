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


class stock_move(osv.osv):
    _inherit = "stock.move"    

    def _parcel_qty(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for stock in self.browse(cursor, user, ids, context=context):
            if stock.product_packaging and stock.product_packaging.qty:
                res[stock.id] = stock.product_qty / stock.product_packaging.qty 
            else:
                res[stock.id] = None
        return res

    _columns = {
        'parcel_qty': fields.function(_parcel_qty, string='Parcel Qty', type='float'),
        'content_qty':fields.related('product_packaging','qty',type='float',string='Content Qty',readonly=True),
    }

stock_move()

class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    def _product_pack_available(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            pack_qty = ''
            if line.product_id.packaging and line.product_id.packaging[0].qty and line.product_id.packaging[0].qty != 0:
                pack_qty = line.product_qty / line.product_id.packaging[0].qty
            res[line.id] = pack_qty
        return res
                    
    def _product_pack_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            pack_name = ''
            if line.product_id.packaging and line.product_id.packaging[0].ul :
                pack_name = line.product_id.packaging[0].ul.name + ' '+_('á')+' '+ str(line.product_id.packaging[0].qty)
            res[line.id] = pack_name
        return res
                                
                                
    _columns = {
       'pack_name' : fields.function(_product_pack_name, type='char', string='Pack Name'),
       'pack_qty_available': fields.function(_product_pack_available,
                type='float',  digits_compute=dp.get_precision('Product UoM'),
                string='Packs On Hand',)
                }
                                 
stock_inventory_line()
