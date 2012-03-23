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
import netsvc
from tools.translate import _
import logging

class stock_journal(osv.osv):
    _inherit = 'stock.journal'

    _columns = {
       'reopen_posted':  fields.boolean('Allow Update of Posted Pickings',
            help="Allows to reopen posted pickings, as long no invoice is created or no other moves for the products of this picking are posted"),
        }

stock_journal()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def allow_reopen(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('stock.move')
        for pick in self.browse(cr, uid, ids, context):
            if not pick.stock_journal_id.reopen_posted:
                raise osv.except_osv(_('Error'), _('You cannot reset to draft pickings of this journal ! Please check "Allow Update of Posted Pickings" in Warehous Configuration / Stock Journals'))
            if pick.invoice_state == 'invoiced':
                raise osv.except_osv(_('Error'), _('You cannot reset to draft invoiced picking !'))
            if pick.move_lines:
                for move in pick.move_lines:
                    # FIXME - not sure if date or id has to be checked or both ? especially if average price is used
                    later_ids = move_line_obj.search(cr, uid, [('product_id','=',move.product_id.id),('state','=','done'),('date','>',move.date)])
                    if later_ids:
                        raise osv.except_osv(_('Error'), _('You cannot reopen picking, because product "%s" of this picking has already later posted moves !') % move.product_id.name)
        return True
    

    def action_reopen(self, cr, uid, ids, context=None):
        return True


#    def button_reopen(self, cr, uid, ids, context=None):
#        _logger = logging.getLogger(__name__)   
#        self.allow_reopen(cr, uid, ids, context)
#        _logger.info('FGF picking allow open  '   )
#        self.write(cr, uid, ids, {'state':'draft'})
#        _logger.info('FGF picking draft  '   )
#        self.log_picking(cr, uid, ids, context=context)
#        _logger.info('FGF picking log'   )

        
    
stock_picking()
    


