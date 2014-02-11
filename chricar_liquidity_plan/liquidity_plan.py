# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-14 15:55:18+02
#    20-AUG-2009 (GK) partner_comp_accumulated added
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
from openerp.osv import fields,osv
import time
from datetime import datetime, timedelta
from mx import DateTime


class chricar_liquidity_category(osv.osv):
    _name = "chricar.liquidity.category"
    _columns = {
        'name'               : fields.char    ('Category', size=16, required=True, help="Groups Entries"),
               }
chricar_liquidity_category()

class chricar_liquidity_plan(osv.osv):
    _name = "chricar.liquidity_plan"

    def _partner_comp_accumulated (self,cr, uid, ids, field_name, arg, context=None):
        result = {}
        for plan in self.browse (cr, uid, ids) :
            cr.execute("""select sum(amount) from chricar_liquidity_plan
                            where partner_comp_id = %d
                              and date_planning <= to_date( '%s','YYYY-MM-DD');
             """ % (plan.partner_comp_id, plan.date_planning))
            res = cr.fetchone()
            amount_cum_partner = (res and res[0]) or False
            result[plan.id] = amount_cum_partner
        return result
    #end def _partner_comp_accumulated

    def _amount_cum (self,cr, uid, ids, field_name, arg, context=None):
        result = {}
        for plan in self.browse (cr, uid, ids) :
            cr.execute("""select sum(amount) from chricar_liquidity_plan
                            where date_planning <= to_date( '%s','YYYY-MM-DD');
             """ % plan.date_planning)
            res = cr.fetchone()
            amount_cum_partner = (res and res[0]) or False
            result[plan.id] = amount_cum_partner
        return result
    #end def _partner_comp_accumulated

    _columns = {
       'amount_cum'         : fields.function
           ( _amount_cum
           , type = 'float'
           , method = True
           , string = 'Amount Cum'
           ),
       'amount'             : fields.float   ('Amount', required=True, digits=(16,2)),
       #'code'               : fields.char    ('Code old', size=16, required=True),
       'category_id'        : fields.many2one('chricar.liquidity.category','Category',required=True,select=True),
       'date_planning'      : fields.date    ('Date', size=3, required=True),
       'name'               : fields.char    ('Description', size=128, required=True, help="Purpose of cash flow"),
       'partner_comp_id'    : fields.many2one('res.partner','Company',required=True, select=True),
       'partner_comp_accumulated' : fields.function
           ( _partner_comp_accumulated
           , type = 'float'
           , method = True
           , string = 'Amount Cum/Comp'
           ),
       'partner_id'         : fields.many2one('res.partner','Partner' ),
               }
    _defaults = {}
    _order = "date_planning"

chricar_liquidity_plan()
