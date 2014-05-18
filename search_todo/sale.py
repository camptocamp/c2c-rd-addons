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

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _uninvoiced_lines(self, cr, uid, ids, name, arg, context=None):
        if not ids:
            return {}
        res = {}
        for order in self.browse(cr,uid,ids):
            to_invoice = False
            #if order.amount_total and order.amount_total > 0.0 and order.order_line:
            if order.amount_total and order.amount_total > 0.0 :
                for line in order.order_line:
                    if line.invoiced != True and line.price_unit and line.price_unit >0.0 :
                        to_invoice = True
            res[order.id] = to_invoice
                    
        return res

    _columns = {
        'uninvoiced_lines': fields.function(_uninvoiced_lines, method=True, string='Uninvoiced Lines', type='boolean', store=True),
    }

sale_order()
