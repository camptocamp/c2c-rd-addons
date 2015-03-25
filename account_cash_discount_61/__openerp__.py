# -*- coding: utf-8 -*-
##############################################################################
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

'name': 'Account Cash Discount 6.1',
'version': '0.7',
'category': 'Accounting & Finance',
'description': """
Adds Cash Discount
necessary in Austria (Germany?)

Manual:
    * Define cash discount in Payment Terms
        * one line percent with discount - you should enter 2 for 2%
        * one line balance
this will create  account moves as usual

    * Pay Invoice - enter payment amount
        * select BOTH invoice amounts (net and balance) to pay

    * Periodical Processing - manual reconciliation
        * choose all positions to reconcile

ALWAYS choose "Reconcile with Write-Off"

The reconciliation will
    * gnerate aliquot(!) move lines to correct tax base and tax amount (required)
        * this may generate unexpected discount/write off amounts if one partner has invoices with and without cash discount
        * the situation many be become very complex if many payments, invocies with and without discounts are reconciled
    * assign only ONE reconcile id to alle reconciled lines

Not covered/ToDo:
    * currently supports only one discount line Ex: 14 days 2%, 30 days net (and NOT 14 days 3%, 30 days 2%, 60 net)
    * pay invoice: automatically select all move_lines of an invoice if invoice payment term has is_discount flag set
    * invoice lines: allow to specify amount for discount if not total line amount is subject to cash discount
    * create analytic lines for discount - using the anlalytic accounts of the invoice
    * mapping for accounts (fiscal position)
    * automatic reconciliation
    * multi currency
    * reconcile invoice while entering bank statement line (IMHO does [again] not work as expected)
    * rename "Write Off" button
""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [ 'account_voucher' ],
'data': [
'payment_term_view.xml',
      ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
