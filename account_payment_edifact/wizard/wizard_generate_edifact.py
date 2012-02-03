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
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from osv import fields, osv
from tools.translate import _

class wizard_generate_edifact(osv.osv_memory) :
    _name = "payment.order.edifact"
    _description = "Generate EDIFACT"

    def payment_send(self, cr, uid, data, context):
        bank_obj = self.pool.get('res.bank')
        bank_ids = bank_obj.search(cr, uid, [])
        bank_obj.retrofit_country(cr, uid, bank_ids)
        
        order_obj = self.pool.get('payment.order')
        order_ids = order_obj.search(cr, uid, [('state', '!=', 'cancel')])
        order_obj.generate_edifact(cr, uid, order_ids, context)
    # end def payment_send
    
#    states = \
#        { 'init' : 
#            { 'actions' : []
#            , 'result'  : 
#                { 'type'   : 'action'
#                , 'action' : _payment_send
#                , 'state'  : 'end'
#                }
#            }
#        }
# end class wizard_generate_edifact

wizard_generate_edifact()

import sys
print >>sys.stderr, ">>>>>>>>>>>>>>>>>>>>>>", dir(wizard_generate_edifact) #################
print >>sys.stderr, ">>>>>>>>>>>>>>>>>>>>>>", wizard_generate_edifact._inherits #################
print >>sys.stderr, ">>>>>>>>>>>>>>>>>>>>>>", wizard_generate_edifact._name #################
