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
from openerp.osv import fields, orm

class product_template(orm.Model):
    _inherit = 'product.template'
    _columns = {
        'property_stock_location': fields.property(
            relation='stock.location', type='many2one',
            string='Stock Location', method=True, view_load=True,
            help="This location will be proposed as source (sale,internal) or target (purchase,production) location for stock move for this product."\
                 "Leave empty if you want to use the location of this product category"),
    }


class product_category(orm.Model):
    _inherit = 'product.category'
    _columns = {
        'property_stock_location': fields.property(
            relation='stock.location', type='many2one',
            string='Stock Location', method=True, view_load=True,
            help="This location will be proposed as source (sale,internal) or target (purchase,production) location for stock moves of this category"),
               }
