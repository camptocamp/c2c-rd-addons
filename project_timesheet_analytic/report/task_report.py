# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields,osv
import openerp.tools

class report_timesheet_task_user(osv.osv):
    _inherit = "report.timesheet.task.user"

    def _get_analytic_hours(self, cr, uid, ids, name,args,context):
        result = {}
        for record in self.browse(cr, uid, ids,context):
            last_date = datetime.strptime(record.name, '%Y-%m-%d') + relativedelta(months=1) - relativedelta(days=1)
            rtl_obj = self.pool.get('hr.analytic.timesheet')
            rtl_ids = rtl_obj.search(cr, uid, [('user_id','=',record.user_id.id),('date','>=',record.name),('date','<=',last_date.strftime('%Y-%m-%d'))])
            rtl_hrs = rtl_obj.read(cr, uid, rtl_ids, ['unit_amount','date','user_id'])
            total = 0.0
            for hrs in rtl_hrs:
                total += hrs['unit_amount']
            result[record.id] = total
        return result


    _columns = {
        'analytic_hrs': fields.function(_get_analytic_hours, string="Analyitc Hours", help="including task hours"),
    }

report_timesheet_task_user()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
