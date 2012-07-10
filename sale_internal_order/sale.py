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
  
    def _get_policy(self, cr, uid, context=None):

       res = list(super(sale_order, self)._columns['order_policy'].selection)
       res.append(('internal','Internal Order'))
       return res 

    def _get_help(self, cr, uid, context=None):

       res = super(sale_order, self)._columns['order_policy']
       _logger  = logging.getLogger(__name__)
       self._logger.info('FGF help %s', res)

       return res 

       
    _columns = {
       'order_policy': fields.selection( selection=_get_policy, 
	               string = 'Invoice Policy',
                       required=True,  
                       readonly=True, states={'draft': [('readonly', False)]},
                       #help=_get_help # does not work
		       help="""The Invoice Policy is used to synchronise invoice and delivery operations.
  - The 'Pay before delivery' choice will first generate the invoice and then generate the picking order after the payment of this invoice.
  - The 'Deliver & Invoice on demand' will create the picking order directly and wait for the user to manually click on the 'Invoice' button to generate the draft invoice based on the sale order or the sale order lines.
  - The 'Invoice on order after delivery' choice will generate the draft invoice based on sales order after all picking lists have been finished.
  - The 'Invoice based on deliveries' choice is used to create an invoice during the picking process.
  - The 'Internal Order' will create internal pickings and no invoices"""
		       ),
    }

sale_order()
