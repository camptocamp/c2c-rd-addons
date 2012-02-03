# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    10-MAR-2011 (GK) created
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
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from osv import fields, osv
from tools.translate import _

class wizard_construct_iban(osv.osv_memory) :
    _name = "res.partner.bank.construct.iban"
    _description = "Convert to IBAN"
    
    def convert(self, cr, uid, ids, context):
        bank_obj         = self.pool.get('res.bank')
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_ids = bank_obj.search(cr, uid, [('country', '!=', False)])
        for bank in bank_obj.browse(cr, uid, bank_ids) :
            partner_bank_ids = partner_bank_obj.search(cr, uid, [('bank', '=', bank.id)])
            for partner_bank in partner_bank_obj.browse(cr, uid, partner_bank_ids):
                partner_bank_obj.convert2iban(cr, uid, [partner_bank.id], context)
    # end def convert
    
#    states = \
#        { 'init' : 
#            { 'actions' : []
#            , 'result'  : 
#                { 'type'   : 'action'
#                , 'action' : convert
#                , 'state'  : 'end'
#                }
#            }
#        }
# end class wizard_construct_iban
wizard_construct_iban()
