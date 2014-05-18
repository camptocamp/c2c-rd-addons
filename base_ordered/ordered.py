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

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _order = 'date_order desc, id desc'

purchase_order()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _order = 'date_order desc, id desc'

sale_order()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _order = 'date desc, id desc'

stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"
    _order = 'date desc, id desc'

stock_move()


class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _order = 'date_invoice desc, id desc'

account_invoice()

class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"
    _order = 'date_start desc, id desc'

account_fiscalyear()

