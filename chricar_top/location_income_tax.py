# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-07-09 16:17:22+02
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from osv import fields,osv
import decimal_precision as dp

class location_income_tax(osv.osv):
     _name = "location.income.tax"
     _description = "Holds data of yearly income statement"
     _columns = {
         'location_id'        : fields.many2one('stock.location','Location', select=True, required=True),
         'fiscalyear_id'      : fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
         'account_id'         : fields.many2one('account.account', 'Account', required=True, ondelete="cascade",domain="[('type', '!=', 'view')]"),
         'amount'             : fields.float('Amount', digits_compute=dp.get_precision('Account'),required=True),
         'note'               : fields.text('Note'),
}
location_income_tax()

class stock_location(osv.osv):
     _inherit = "stock.location"

     _columns = {
       'income_tax_move_ids'  : fields.one2many('location.income.tax','location_id','Income Tax Statement'),
}
stock_location()
