# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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
import time
from osv import fields, osv
from tools.translate import _
import logging
import one2many_sorted

class sale_order(osv.osv):
    _inherit = "sale.order"
  
    _columns = {
        'categ_id': fields.many2one('product.category','Category', help="Select category to be displayed"),
        'order_line_portal_sorted' : one2many_sorted.one2many_sorted
              ( 'sale.order.line'
              , 'order_id'
              , 'Order Lines Sorted'
              , search = [('product_id.display_portal_ok', '=', True)]
              , states={'draft': [('readonly', False)]}
              , order  = 'product_id.categ_id.name, product_id.name'
              ),
        }
sale_order()

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'display_portal_ok': fields.boolean('Display in Partner Portal', help="Determines if the product can be visible in the list of product within a selection from a sale order line."),
    }
product_template()

