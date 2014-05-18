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
#import openerp.addons.decimal_precision as dp

import re
from openerp.tools.translate import _



#----------------------------------------------------------
#  Product
#----------------------------------------------------------


class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
         'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', states={'done': [('readonly', True)]}, help="Production lot is used to put a serial number on the production", select=True),
    }


mrp_production()
