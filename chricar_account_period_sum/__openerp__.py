# -*- coding: utf-8 -*-
# ChriCar Beteiligungs- und Beratungs- GmbH
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
{
    "name" : "Account Period Sum",
    "version" : "0.9.5",
    "author"  : "ChriCar Beteiligungs- und Beratungs GmbH" ,
    "website" : "http://www.chricar.at/ChriCar",
        "description"  : """BETA Quality - Proof of concept
        This module adds period sums for moves_lines
        of account_moves with state posted
        *) on update from draft to posted
           hence: account_move_lines must NOT be added to account_moves with state posted.
        *) balance carried forward is calculated for all subsequent fiscal years
           no account_move_lines are generated for these sums
           these sums always represent the balance of the preceding fiscal year.
        *) on creation of new fiscal years -> balance carried forward
        *) on change of deferral_method in general accounts
           it's subject to another check if and when changes of this field are allowed.
           IMHO not if at least one fiscal year is closed.
        *) the name of fiscal years not ending on Dec 31st is year-period (YYYY-MM) of the end of the fiscal year
        *) for every fiscal year beginning in the same calendar year a period sum with the name YYYY00 will be created,
           but associated to the correct fiscal year.
        *) the period sums will be deleted if the matching account_periods are deleted.

    standardizes account_period name generation to comply with this naming.

    OpenERP needs Closing the fiscal year to show correct balances.
       This module introduces a special journal is_opening_balance. All moves of this journal will not be added to the period sum
       because there is a special period yyyy00 which is automatically and permanently updated with the opening balance.
       If opening balance already exists, it is neccessary to install this module, mark the journal as "Is Opening Balance Journal"
       and update the module to get correct period sums.

    Things to come:
    * eventually - adapting the accounting reporting to use this sums (2c2?)
    """,
    "category" : "Generic Modules/Others",
    "depends" : ["base", "account", "c2c_account_closing_remarks", "chricar_view_id"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["chricar_account_period_sum_view.xml","wizard/chart.xml","security/rule.xml","security/ir.model.access.csv","report_chart.xml"],
    "active": False,
    "installable": True
}
