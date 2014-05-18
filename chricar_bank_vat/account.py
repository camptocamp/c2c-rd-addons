# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2011 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging


class account_move_line(osv.osv):
    """
    these fields are not used yet, but necessary to allow data entry in Journal Entries
    automatically generation of tax moves wil require some more code
    """
    _inherit = "account.move.line"
    _logger = logging.getLogger(__name__)
 
    def _get_taxable_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for move in self.browse(cr, uid, ids, context):
            res[move.id] = move.debit - move.credit

        return res
 
    
    _columns = {
        'tax_id': fields.many2one("account.tax","Tax",
            help="VAT for this line, only allowed if no partner specified"),
        'amount': fields.function(_get_taxable_amount, method=True, string='Amount',  digits_compute=dp.get_precision('Account'),
            help="""Amount"""),
        'amount_net': fields.float('Amount Net',  digits_compute=dp.get_precision('Account'),
            help="""Amount Net"""),
        'amount_tax': fields.float('Amount Tax',  digits_compute=dp.get_precision('Account'),
            help="""Amount Tax"""),

    }

account_move_line()
