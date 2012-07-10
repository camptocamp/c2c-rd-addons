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


class sale_order(osv.osv):
    _inherit = "sale.order"
  
    def _get_policy(self, cr, uid, ids, context=None):

       res = list(super(sale_order, self)._columns['order_policy'].selection)
       res.append(('internal','Internal Order'))
       return res 

    def _get_help(self, cr, uid, ids, context=None):

       res = list(super(sale_order, self)._columns['order_policy'].help)
       return res 

       
    _columns = {
       'order_policy': fields.selection(selection=_get_policy, 
                       string='Invoice Policy', 
                       required=True,  
                       readonly=True, states={'draft': [('readonly', False)]},
                       help=_get_help),
    }

sale_order()
