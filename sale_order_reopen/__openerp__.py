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

{
    "name" : "Sale Order Reopen",
    "version" : "1.1",
    "author" : "Camptocamp Austria",
    "category": 'Sales Management',
    'complexity': "normal",
    "description": """
Allows reopening of sale orders.
================================

This module allows i
* to reopen (set to Quotation) Sale Orders in state progress and cancel
as associated pickings or invoices are canceled if possible.
* to set hanging sales orders to done.

    """,
    'website': 'http://www.camptocamp.com',
    "depends" : ["sale","stock_picking_reopen","account_invoice_reopen"],
    'init_xml': [],
    'update_xml': ['sale_view.xml','sale_workflow.xml' ],
    'demo_xml': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
