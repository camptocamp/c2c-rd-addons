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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools.sql import drop_view_if_exists
import logging


def init(self, cr):
    drop_view_if_exists(cr, 'hr_expense_report')


#----------------------------------------------------------
#  Account Invoice Line INHERIT
#----------------------------------------------------------
class hr_expense_line(osv.osv):
    _inherit = "hr.expense.line"
    _logger = logging.getLogger(__name__)

    def _get_price_unit_id(self, cr, uid, context):
        self._logger.debug('%s', context)
        return

    _columns = {
        'price_unit_id'    : fields.many2one('c2c_product.price_unit','Price Unit'),
        'price_unit_pu'    : fields.float(string='Unit Price',digits_compute=dp.get_precision('Cost Price'),  \
                            help='Price using "Price Units"') ,
        'unit_amount'      : fields.float(string='Unit Price internal',  digits=(16, 8), \
                            help="""Cost internal amount"""),
    }

    _defaults = {
        'price_unit_id'   : _get_price_unit_id,
    }

    def init(self, cr):
        cr.execute("""
            update hr_expense_line set price_unit_pu = unit_amount  where price_unit_pu is null;
        """)
        cr.execute("""
            update hr_expense_line set price_unit_id = (select min(id) from c2c_product_price_unit where coefficient=1) where price_unit_id is null;
        """)

    def onchange_price_unit(self, cr, uid, ids, field_name,price_pu, price_unit_id):
        if  price_pu and  price_unit_id:
            pu = self.pool.get('c2c_product.price_unit').browse(cr, uid, price_unit_id)
            price = price_pu / pu.coefficient
            return {'value': {field_name : price}}
        return {}

hr_expense_line()
