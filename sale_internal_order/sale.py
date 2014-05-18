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
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
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
       self._logger.debug('FGF help %s', res)

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

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _check_internal_order(self, cr, uid, ids, context=None):
        """ Checks whether invoce state mataches order_policy and default partner location type
        @return: True or False
        """
        for pick in self.browse(cr, uid, ids, context=context):
         if pick.state != 'cancel' and pick.sale_id and pick.type == 'out':
          if pick.invoice_state != 'none':
            if  pick.sale_id and pick.sale_id.order_policy == 'internal':
                  raise osv.except_osv(_('Error'), _('Sale order with order policy %s must not have pickings %s with invoice policy %s ')% (pick.sale_id.order_policy,pick.name, pick.invoice_state))
                  return False
            if pick.partner_id and pick.partner_id.property_stock_customer.usage== 'internal':
                  raise osv.except_osv(_('Error'), _('Sale order with order policy %s must not have partners with customer stock usage other than internal ')% (pick.sale_id.order_policy))
                  return False
          else:
            if  pick.sale_id and pick.sale_id.order_policy != 'internal':
                  raise osv.except_osv(_('Error'), _('Sale order with order policy %s must not have pickings %s with invoice policy %s ')% (pick.sale_id.order_policy, pick.name, pick.invoice_state))
                  return False
            if pick.partner_id and pick.partner_id.property_stock_customer.usage == 'customer':
                  raise osv.except_osv(_('Error'), _('Sale order with order policy %s must not have partners with customer stock usage other than internal ')% (pick.sale_id.order_policy))
                  return False
         return True

    def _get_constraints(self, cr, uid, context=None):
        _logger  = logging.getLogger(__name__)
        res = ''
        self._logger.debug('FGF pick constraints a %s', res)
        #res = super(stock_picking, self)._constraints
        self._logger.debug('FGF pick constraints b %s', res)
        c = (self.check_internal_order, 'incorrect invoice state', ['invoice_state'])
        self._logger.debug('FGF pick constraints c %s', c)
        #res.append(c)
        return res
        #FIXME - should be replaced by _get_constraints 
    _constraints = [(_check_internal_order, 'incorrect invoice state', ['invoice_state'])]

stock_picking()

   
