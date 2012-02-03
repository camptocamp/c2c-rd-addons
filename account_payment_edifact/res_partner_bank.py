# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    05-MAR-2011 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
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
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from osv import fields, osv
from tools.translate import _

class res_partner_bank(osv.osv) :
    _inherit = "res.partner.bank"

    def _construct_iban(self, p_bank):
        iban    = False
        account = p_bank.acc_number
        blz     = p_bank.bank.name # no BLZ!
        if p_bank.bank.country :
            country = p_bank.bank.country.code
            if   country == "AT":
                xblz     = "%05i" % int(blz)
                xaccount = "%011i" % int(account)
                prz      = "%02i" % (98 - int(xblz + xaccount + "102900") % 97)
                iban     = ("AT" + prz + xblz + xaccount)
            elif country == "DE":
                xblz     = "%08i" % int(blz)
                xaccount = "%010i" % int(account)
                prz      = "%02i" % (98 - int(xblz + xaccount + "131400") % 97)
                iban     = ("DE" + prz + xblz + xaccount)
        return iban
    # end def _construct_iban

    def _format_iban(self, iban):
        return " ".join([iban[i:i+4] for i in range(0, len(iban), 4)])
    # end def _format_iban

    def convert2iban(self, cr, uid, ids, id):
        for partner_bank in self.browse(cr, uid, ids):
            if partner_bank.state == "iban" or partner_bank.iban: continue # already exists
            iban = self._construct_iban(partner_bank)
            if iban :
                fban = self._format_iban(iban)
                self.write(cr, uid, [partner_bank.id], {'iban' : fban, 'state' : 'iban'})
# end class res_partner_bank
res_partner_bank()

class payment_line(osv.osv):
    _inherit = 'payment.line'
    
    _columns = \
        { 'bank_account_type': fields.related
            ( 'bank_id'
            , 'state'
            , type      = 'char', size=16
            , store     = False
            , relation  = 'res.partner_bank'
            , string    = 'Bank Account Type'
            )
        }

    def convert2iban(self, cr, uid, ids, id):
        partner_bank_obj = self.pool.get('res.partner.bank')
        for payment_line in self.browse(cr, uid, ids):
            partner_bank_obj.convert2iban(cr, uid, [payment_line.bank_id.id], id)

payment_line()

class payment_order(osv.osv):
    _inherit = 'payment.order'

    def convert2iban(self, cr, uid, ids, id):
        payment_line_obj = self.pool.get('payment.line')
        for payment_order in self.browse(cr, uid, ids):
            for payment_line in payment_order.line_ids :
                payment_line_obj.convert2iban(cr, uid, [payment_line.id], id)
payment_order()
