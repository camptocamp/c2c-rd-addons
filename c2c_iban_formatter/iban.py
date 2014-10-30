# -*- coding: utf-8 -*-
##############################################
#
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from stdnum import iban
import logging


class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"

    def _format_iban(self, cr, uid, acc_number):
        '''
        This function removes all characters from given 'string' that isn't a alpha numeric and converts it to upper case, checks checksums and groups by 4
        '''
        res = ''
        if acc_number:
            _logger = logging.getLogger(__name__)
            _logger.dbug('FGF acc_number %s' % (acc_number))
            try:
                a = iban.validate(acc_number)
            except:
                raise osv.except_osv(_('Error!'), (_('%s is not a valid IBAN.') % (acc_number)))
            res = iban.format(a) 
        return res

    def onchange_acc_id(self, cr, uid, ids, acc_number, context=None):
        result = {}
        if acc_number:
             for acc in  self.browse(cr, uid, ids, context=context):
                 if acc.state == 'iban':
                     result['acc_number'] = self._format_iban(cr, uid, acc_number)
             
        return {'value': result}
     
 
res_partner_bank() 
