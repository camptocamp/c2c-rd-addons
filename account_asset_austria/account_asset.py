# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2004-2013 Camptocamp Austria (<http://camptocamp.com>).
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



from osv import osv, fields
import decimal_precision as dp

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

from tools.translate import _

class account_asset_category(osv.osv):
    _inherit = 'account.asset.category'

    _columns = {
        'half_year_rule':fields.boolean('Half Year Depreciation', help='Computes full/half depreciation for usage in fist/second half year'),
        }

    #_defaults['half_year_rule'] : True
              
account_asset_category()


class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'

    _columns = {
        'half_year_rule':fields.boolean('Half Year Depreciation', help='Computes full/half depreciation for usage in fist/second half year'),
        'activation_date': fields.date('Activation Date', readonly=True, states={'draft':[('readonly',False)]},  help='Is used instead of activation date if set'),
        }


              
account_asset_asset()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

