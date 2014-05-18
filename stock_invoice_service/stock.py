# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

# FIXME remove logger lines or change to debug
 
from openerp.osv import fields, osv
import openerp.netsvc
from openerp.tools.translate import _
import time
import logging


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _invoice_hook(self, cr, uid, picking, invoice_id):
        res = super(stock_picking, self)._invoice_hook(cr, uid, picking, invoice_id)

        obj_sale_order_line = self.pool.get('sale.order.line')
        obj_invoice_line = self.pool.get('account.invoice.line')
        states=['confirmed', 'done', 'exception']

        if picking.sale_id.order_policy == 'picking': # to be sure as this might have changed ?!
            for line in picking.sale_id.order_line:
                lines = []
                if line.product_id.type == 'service':  # FIXME consumable
                    if line.invoiced:
                        continue
                    elif (line.state in states):
                        lines.append(line.id)
                created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines)
                obj_invoice_line.write(cr, uid, created_lines, {'invoice_id':invoice_id}) 

        return res

      
stock_picking()
    


