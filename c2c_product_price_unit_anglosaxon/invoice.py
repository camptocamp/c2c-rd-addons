# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
import logging 

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = super(account_invoice_line, self).move_line_get(cr, uid, invoice_id, context)
        _logger  = logging.getLogger(__name__)
        self._logger.debug('FGF anglo moves %s', res)
        line_tot=0
        line_tot_round=0
        for line in res:
            self._logger.debug('FGF anglo moves Price %s', line['price'])
            line_tot += line['price']
            line['price'] = round(line['price'],2)
            line_tot_round += line['price']
        self._logger.debug('FGF anglo moves total %s', line_tot)
        self._logger.debug('FGF anglo moves total round %s', line_tot_round)
        
        
        return res
    
account_invoice_line()