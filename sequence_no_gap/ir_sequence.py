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
import openerp
import logging

class ir_sequence(openerp.osv.osv.osv):
    _inherit = 'ir.sequence'

    def get(self, cr, uid, code, context=None):
	_logger = logging.getLogger(__name__)
	if not context:
            context = {}
        company_id = False
	s = [('code','=',code)]
        seq_id = self.search(cr, uid, s)
        c = False
	if context.get('company_id'):
            company_id =  context['company_id']
	    c = ('company_id','=', company_id)
	    s.append( c )
        if len(seq_id) > 1:
            seq_id = self.search(cr, uid, s)
        
	for seq in self.browse(cr, uid, seq_id):
            if seq.implementation == 'standard':
	        return super(ir_sequence, self).get( cr, uid, code, context=None)
	    else:
                prefix = seq.prefix or ''
                suffix = seq.suffix or ''
                padding = seq.padding or 0
	        number_next = seq.number_next
	        number_increment = seq.number_increment 

         
	_logger.info('FGF seq comp:%s nxt:%s %s' % (company_id,number_next, prefix)) 
	obj = False
	if code in ['stock.picking.internal','stock.picking.in','stock.picking.out']:
	    obj = self.pool.get('stock.picking')
	elif code == 'sale.order':
	    obj = self.pool.get('sale.order')
	elif code == 'purchase.order':
	    obj = self.pool.get('purchase.order')
                
        if not obj:
	   return super(ir_sequence, self).get( cr, uid, code, context=None)
        inc = 1
        _logger.info('FGF seq %s ' % (prefix + str(number_next - inc).rjust(padding,'0') + suffix)) 
	s = [('name','=',prefix + str(number_next - inc).rjust(padding,'0') + suffix)]
	if c:
	   s.append(c)
	last_id = obj.search(cr, uid, s)
	if last_id:	
	   return super(ir_sequence, self).get( cr, uid, code, context=None)
	else:
	   while number_next - inc > 0:
               inc += 1
               _logger.info('FGF seq %s ' % (prefix + str(number_next - inc).rjust(padding,'0') + suffix)) 
	       s = [('name','=',prefix + str(number_next - inc).rjust(padding,'0') + suffix)]
	       if c:
	           s.append(c)
               last_id = obj.search(cr, uid, s)
	       if last_id:
		   return prefix + str(number_next - inc + number_increment).rjust(padding,'0') + suffix
	# we should return a code in any case, if example the preifx is changed
        return super(ir_sequence, self).get( cr, uid, code, context=None)
    
ir_sequence()
