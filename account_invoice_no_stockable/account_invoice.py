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

# FIXME remove logger lines or change to debug
 
from osv import fields, osv
from tools.translate import _
import logging
import time



class account_journal(osv.osv):
    _inherit = "account.journal"

    _columns = {
        'product_in_line': fields.selection([('forbidden', 'Forbidden'),('allowed','Allowed'), ('mandatory', 'Mandatory'),],
		  'Product in Inv. Line', size=16, required=True,
		  help="Invoices lines coding requirements for stockable products"),
	}
    _defaults = {
        'product_in_line': 'forbidden',
            }

account_journal()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
   
    def _check_product_in_line(self,cr,uid,ids,context=None):
        for line in self.browse(cr, uid, ids, context=context):
	  if line.product_id.type <> 'service':
	    if line.product_id and line.invoice_id.journal_id.product_in_line == 'forbidden':
	        raise osv.except_osv(_('Error !'), _('Stockable products are not allowed for this journal: %s !') % line.invoice_id.journal_id.name) 
		return False
	    if not line.product_id and line.invoice_id.journal_id.product_in_line == 'mandatory':
	        raise osv.except_osv(_('Error !'), _('Stockable product is required for this journal: %s !') % line.invoice_id.journal_id.name) 
		return False
        return True

    _constraints = [
        (_check_product_in_line, 'Error ! Violating product coding guideline ', ['product_id']),
	]

account_invoice_line()    
