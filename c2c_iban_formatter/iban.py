# -*- coding: utf-8 -*-
##############################################
#
# Copyright (C) Camptocamp Austria
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
import string

import netsvc
from osv import fields, osv
from tools.translate import _

def _format_iban(string):
    '''
    This function removes all characters from given 'string' that isn't a alpha numeric and converts it to upper case.
    '''
    res = ""
    for char in string:
        if char.isalnum():
            res += char.upper()
    iban = res
    res = ""
    while len(iban) > 0 :
        res = res + iban[0:4] + ' '
        iban = iban[4:]

    return res.strip()
  