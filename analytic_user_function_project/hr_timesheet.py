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
import datetime
from osv import osv, fields
import sys


class hr_analytic_timesheet(osv.osv):
    _name = "hr.analytic.timesheet"
    _table = 'hr_analytic_timesheet'


    def _getEmployeeProduct(self, cr, uid, context=None):
        if context is None:
            context = {}
        print >> sys.stderr, 'context timesheet', context

        res = super(hr_analytic_timesheet,self)._getEmployeeProduct(self, cr, uid, context=None) 
        return res

hr_analytic_timesheet()