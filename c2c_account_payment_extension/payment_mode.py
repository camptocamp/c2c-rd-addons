# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    08-JUN-2012 (GK) created
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
from openerp.osv import osv, fields

class payment_mode(osv.osv):
    _inherit     = 'payment.mode'
    _description = 'Payment Modes'
    _columns     = \
        { 'amount_partner_min'  : fields.float
            ('Minimum Payment', digits=(16, 2), help="Minimum payment per partner")
        , 'require_bank_account': fields.boolean
            ( 'Require Bank Account'
            , help='Ensure all lines in the payment order have a bank account when proposing lines to be added in the payment order.'
            )
        #,'type': fields.many2one('payment.type', 'Payment type', required=True, help='Select the Payment Type for the Payment Mode.'),
        ,'type': fields.many2one('payment.type', 'Payment type',  help='Select the Payment Type for the Payment Mode.'),
        }
    _defaults = \
        { 'amount_partner_min'   : lambda *a : 100.0
        , 'require_bank_account' : lambda *a : True
        }
payment_mode()
