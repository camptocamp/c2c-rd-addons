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


{ 'sequence': 500,

'name': 'ChriCar Beteiligungs- und Beratungs- GmbH Base',
'version': '1.0',
'category': 'Others',
'description': """
This module installs everything from addons we need for Austrian Base
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [
"account"
,"account_accountant"
,"account_chart"
#,"account_coda"
,"account_followup"
#,"account_invoice_layout"
,"account_payment"
,"account_voucher"
,"analytic"
,"base"
,"base_action_rule"
# ,"base_calendar"
,"base_iban"
# ,"base_report_creator"
# ,"base_report_designer"
,"base_setup"
# ,"base_tools"
,"base_vat"
,"board"
# ,"caldav"
,"crm"
# ,"crm_caldav"
,"crm_claim"
# ,"crm_fundraising"
,"crm_helpdesk"
,"decimal_precision"
,"delivery"
,"document"
#,"document_ftp"
#,"document_webdav"
,"email_template"
,"fetchmail"
,"hr"
,"hr_attendance"
,"hr_contract"
,"hr_evaluation"
,"hr_expense"
,"hr_holidays"
,"hr_payroll"
,"hr_payroll_account"
,"hr_recruitment"
,"hr_timesheet"
,"hr_timesheet_invoice"
,"hr_timesheet_sheet"
,"knowledge"
# ,"mail_gateway"
,"marketing"
,"marketing_campaign"
,"mrp"
#,"mrp_jit"
#,"outlook"
#,"point_of_sale"
#,"process"
,"procurement"
,"product"
,"project"
#,"project_gtd"
,"project_mrp"
,"purchase"
,"purchase_requisition"
# ,"report_designer"
,"report_intrastat"
,"resource"
,"sale"
,"sale_crm"
,"sale_journal"
# ,"sale_layout"
,"sale_order_dates"
# ,"thunderbird"
,"stock"
,"survey"
,"warning"
# ,"wiki"
# ,"wiki_faq"
#,"wiki_quality_manual"
# ,"wiki_sale_faq"
 ],
'data': [       ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
