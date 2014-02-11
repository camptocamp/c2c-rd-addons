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
import time
from openerp.osv import osv, fields
from openerp.tools.translate import _


class hr_timesheet_sheet(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet"
    
    _columns = {
	'check_sheet': fields.boolean('Sheet Level Check', help="Checks Sign In/Out on sheet level, allowing to enter missing data")
	}

    def _altern_si_so_sheet(self, cr, uid, ids, context=None):
        """ check in check out sequence test
        """
        hr_attendance = self.pool.get('hr.attendance')
        att_ids = hr_attendance.search(cr, uid, [('sheet_id','=',ids),('action', 'in', ('sign_in', 'sign_out'))], order='name ASC', context=context)
        
        last_action = ''
        for att in hr_attendance.browse(cr, uid, att_ids, context):
	    if last_action and att.action == last_action:
	        raise osv.except_osv(_('Error'), _('Sign IN/OUT must alternate: date %s action %s !') % (att.day, att.action))
                return False  
            else:
		last_action = att.action
        return True
    
    _constraints = [(_altern_si_so_sheet, 'Error: Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

hr_timesheet_sheet()

class hr_attendance(osv.osv):
    _inherit = "hr.attendance"
    
    def _altern_si_so(self, cr, uid, ids, context=None):
        """ check must be done on line or sheet level
        """
        sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        
        check_sheet = False
        for att in self.browse(cr, uid, ids, context=context):
            sheet_id = sheet_obj.search(
                    cr, uid, [
                        ('employee_id', '=', att.employee_id.id),
                        ('date_from', '<=', att.name),
                        ('date_to', '>=', att.name),
                        ],
                    limit=1,
                    context=context)
            sheet_id = sheet_id and sheet_id[0] or False
            if sheet_id:
                for sheet in sheet_obj.browse(cr, uid, [sheet_id] , context=context):
		    check_sheet = sheet.check_sheet
	    if check_sheet:
		return True
	    else:
		return super(hr_attendance, self)._altern_si_so(cr, uid, ids, context)

    _constraints = [(_altern_si_so, 'Error: Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

hr_attendance()
