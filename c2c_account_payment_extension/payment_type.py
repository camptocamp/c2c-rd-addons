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


class payment_type(osv.osv):
    _name= 'payment.type'
    _description= 'Payment type'
    _columns= {
        'name': fields.char('Name', size=64, required=True, help='Payment Type', translate=True),
        'code': fields.char('Code', size=64, required=True, help='Specify the Code for Payment Type'),
        'suitable_bank_types': fields.many2many('res.partner.bank.type',
            'bank_type_payment_type_rel',
            'pay_type_id','bank_type_id',
            'Suitable bank types'),
        'active': fields.boolean('Active', select=True),
        'note': fields.text('Description', translate=True, help="Description of the payment type that will be shown in the invoices"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'active': lambda *a: 1,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id
    }

payment_type()

