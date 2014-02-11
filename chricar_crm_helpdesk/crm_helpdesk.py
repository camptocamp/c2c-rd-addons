# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-18 23:44:30+02
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
from openerp.osv import fields, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta


class crm_helpdesk(osv.osv):
    """ Helpdesk Cases """

    def _date_warning(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for case in self.browse(cursor, user, ids, context=context):
            deadline = datetime.now()
            if case.date_deadline:
                deadline = datetime.strptime(case.date_deadline, '%Y-%m-%d')
            dl = 0
            if case.days_lead:
                dl = case.days_lead
            dw = 0
            if case.days_warning:
                dw = case.days_warning
            date_warning = deadline  - relativedelta(days = dl + dw)
            res[case.id] = date_warning
        return res   
        
    _inherit = "crm.helpdesk"
    _columns = {
        'days_lead': fields.integer('Lead Days',help='Days before deadline date an action has to be taken (Term of notice)'),
        'days_warning': fields.integer('Warning Days',help='Days before beginning of lead time to allow action in time'),
        'date_warning': fields.function(_date_warning, method=True, string='Date Warning', type='date', store=True,help='Date the case is/has to be listed in ToDo'),
        'partner_id': fields.many2one('res.partner', 'Partner Contact'),
      }
    _defaults = {
        'days_lead': lambda *a: 0,
        'days_warning': lambda *a: 7,
    }

crm_helpdesk()
