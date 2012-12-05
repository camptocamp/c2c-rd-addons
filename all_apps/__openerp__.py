# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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


{
    'name': 'All apps',
    'version': '1.0',
    'category': 'Others',
    'description': """
installs all apps
""",
    'author': 'Camptocamp Austria',
    'depends': [
"account_accountant"
,"account_voucher"
,"base_calendar"
,"contacts"
,"crm"
,"event"
,"hr"
,"hr_evaluation"
,"hr_expense"
,"hr_holidays"
,"hr_recruitment"
,"hr_timesheet_sheet"
,"mail"
,"mrp"
,"note"
,"point_of_sale"
,"project"
,"project_gtd"
,"project_issue"
,"purchase"
,"sale"
,"stock"
     ],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
