# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    05-AUG-2010 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1.17, USA.
#
###############################################
{ 'sequence': 500,
"name"        : "Electronic Banking via EDIFACT"
, "version"     : "1.1"
, "author"      : "Swing Entwicklung betrieblicher Informationssysteme GmbH"
, "website"     : "http://www.swing-system.com"
, "description" : 
"""
Generates an UN/EDIFACT file for each payment order to be sent to a bank.

The generation is triggered by a "Confirm Payments" or via wizard "Generate EDIFACT".

The EDIFACT-files are attached to the payment order.

This works for payment within the country as well as for payments to a foreign country.

EDIFACT is specified by http://www.unece.org/trade/untdid/d01a/trmd/paymul_c.htm

The banking accounts must be specified by IBAN/BIC.

For the own bank IBAN/BIC must be specified.

The banking information must be specified for each payment line (sic!).
If no bank-country is specified, this module tries to retrofit the country from the BIC.
If no country can be guessed, an international money transfer is generated.

The bank transfer currency must be the same as the company currency.

Partner addresses are determined according to the function-sequence "invoice"->"default"->"None".

The "payment day" is, if unspecified or in the past, the file-creation-date.

The sum of the transfers to a bank account must not be negative.
If there are such payment lines with negative amount, the lines are summed up for this bank account.

A conversion to ASCII for all texts within the EDIFACT-file is attempted.
"""
, "category"    : "Payment module"
, "depends"     : 
[ "account_payment"
, "base_iban"
, "account_payment_customer_data"
]
, "init_xml"    : []
, "demo"        : []
, "data"  : 
[ 'payment_iban.xml'
, 'res_bank_view.xml'
, 'wizard/generate_edifact_view.xml'
]
, "test"        : []
, "auto_install": False
, 'installable': False
, 'application'  : False
}
