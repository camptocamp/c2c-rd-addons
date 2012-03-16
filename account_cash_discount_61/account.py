# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

 
import netsvc
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _
import logging


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
 

    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        res = super(account_voucher,self).writeoff_move_line_get(cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None)
        _logger = logging.getLogger(__name__)
        _logger.info('reconcile - voucher writeoff A voucher_id, move_id: %s %s' % (voucher_id, move_id ))
        _logger.info('reconcile - voucher writeoff B context: %s' % context)
        _logger.info('reconcile - voucher writeoff: %s' % res)

      

# FGF FIXME
# here we have to include the austrian rules
# 1) the write off has to be splitted aliquoted between
#    VAT
#    Net
#    of the underlying invoice (move)
# 2) it's a "full reconcile"
#
# we search matching reconcile from this move_id in move lines - find move_id - which is stored in account-invoice
        move_obj = self.pool.get('account.move')
        move_line_ob = self.pool.get('account.move.line')
        invoice_obj = self.pool.get('account.invoice')
        ctx = context
       
        #for move_line in move_line_ob.search(cr, uid, [('move_id','=',move_id):
           

       
       
        return res
       
    def action_move_line_create(self, cr, uid, ids, context=None):
        res = super(account_voucher,self).action_move_line_create(self, cr, uid, ids, context)
        _logger = logging.getLogger(__name__)
        _logger.info('reconcile - action_move_line_create  voucher ids %s' % (ids))
        
        
account_voucher()




    
