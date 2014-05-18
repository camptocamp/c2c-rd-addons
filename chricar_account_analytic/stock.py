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
from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging

#----------------------------------------------------------
# Stock Picking
#----------------------------------------------------------
class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _logger = logging.getLogger(__name__)

    def _get_account_analytic_invoice(self, cr, uid, picking, move_line):
        analytic_id = super(stock_picking,self)._get_account_analytic_invoice(cr, uid, picking, move_line)

        self._logger.debug('_get_account_analytic_invoice FGF:  %s ', analytic_id)
        self._logger.debug('_get_account_analytic_invoice FGF:  %s ', picking)
        return analytic_id

    def _invoice_line_hook(self, cr, uid, move_line, invoice_line_id):
        self._logger.debug('analytic _invoice_line_id FGF:  %s ', invoice_line_id)
        inv_line_obj = self.pool.get('account.invoice.line')
        inv_line = inv_line_obj.browse(cr,uid,invoice_line_id)
        if not inv_line.account_analytic_id and inv_line.account_id.analytic_account_id:
            analytic_id = inv_line.account_id.analytic_account_id.id
            inv_line_obj.write(cr, uid, invoice_line_id, {'account_analytic_id' : analytic_id})

        return  super(stock_picking, self)._invoice_line_hook(cr, uid, move_line, invoice_line_id)


stock_picking()
