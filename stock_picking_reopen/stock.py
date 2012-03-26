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
import time
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
        account_invoice_obj = self.pool.get('account.invoice')
        for pick in self.browse(cr, uid, ids, context):
            if pick.stock_journal_id and not pick.stock_journal_id.reopen_posted:
                raise osv.except_osv(_('Error'), _('You cannot reset to draft pickings of this journal ! Please check "Allow Update of Posted Pickings" in Warehous Configuration / Stock Journals'))
            if pick._columns.get('invoice_ids'):
                ids2 = []
                for inv in pick.invoice_ids:
                    if inv.state in ['draft','cancel']:
                       ids2.append(inv.id) 
                    else:
                       raise osv.except_osv(_('Error'), _('You cannot reset a picking with an open invoice [%s] to draft ! You must reopen the invoice first (install modul account_invoice_reopen' % inv.number))
                account_invoice_obj.unlink(cr, uid, ids2) 
                if ids2:
                    self.write(cr, uid, [pick.id], {'invoice_state':'2binvoiced'})
            elif pick.invoice_state == 'invoiced':
                raise osv.except_osv(_('Error'), _('You cannot reset an invoiced picking to draft !'))
            if pick.move_lines:
                for move in pick.move_lines:
                    # FIXME - not sure if date or id has to be checked or both if average price is used
                    if move.product_id.cost_method == 'average':
                      later_ids = move_line_obj.search(cr, uid, [('product_id','=',move.product_id.id),('state','=','done'),('date','>',move.date),('price_unit','!=',move.price_unit)])
                      if later_ids:
                        later_prices = []
                        for later_move in move_line_obj.browse(cr, uid, later_ids):
                            later_prices.append(later_move.price_unit)
                            raise osv.except_osv(_('Error'), _('You cannot reopen this picking, because product "%s" of this picking has already later posted moves with different cost price(s) %s  then the current [%s] to be reopened! Recalculation of avarage price is not supported') % (move.product_id.name, later_prices, move.price_unit))
        return True
    

    def action_reopen(self, cr, uid, ids, context=None):
        """ Changes picking and move state from done to confirmed.
        @return: True
        """
        move_line_obj = self.pool.get('stock.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_obj = self.pool.get('account.move')
        report_xml_obj = self.pool.get('ir.actions.report.xml')
        attachment_obj = self.pool.get('ir.attachment')

        now = ' ' + _('Invalid') + time.strftime(' [%Y%m%d %H%M%S]')
        for pick in self.browse(cr, uid, ids):
            ml_ids = []
            for ml in pick.move_lines:
                ml_ids.append(ml.id)
            move_line_obj.write(cr, uid, ml_ids, {'state':'confirmed'})
            # we have to handle real time accounting stock moves
            #FIXME - performance, should be an id - link to picking 
            #aml_ids = account_move_line_obj.search(cr, uid, [('picking_id','=',pick.id)])
            aml_ids = account_move_line_obj.search(cr, uid, [('ref','=',pick.name)])
            move_ids = []
            for aml in account_move_line_obj.browse(cr, uid, aml_ids):
                if aml.move_id.id not in move_ids:
                    move_ids.append(aml.move_id.id)
                account_move_line_obj.write(cr, uid, [aml.id], {'ref': aml.ref + now})
            for move in account_move_obj.browse(cr, uid, move_ids):
                account_move_obj.write(cr, uid, [move.id], {'name': move.name + now})
                move_copy_id = account_move_obj.copy(cr, uid, move.id,)
                account_move_obj.write(cr, uid, [move_copy_id], {'name': move.name + now + '*' })
                cr.execute("""update account_move_line
                                 set debit=credit, credit=debit,
                                 ref = ref||'*'
                               where move_id = %s;""" % (move_copy_id)) 
                # rename attachments (reports)
            # for some reason datas_fname has .pdf.pdf extension
            report_ids = report_xml_obj.search(cr, uid, [('model','=', 'stock.picking'), ('attachment','!=', False)])
            for report in report_xml_obj.browse(cr, uid, report_ids):
                aname = report.attachment.replace('object','pick')
                aname = eval(aname)+'.pdf'
                attachment_ids = attachment_obj.search(cr, uid, [('res_model','=','stock.picking'),('datas_fname', '=', aname),('res_id','=',pick.id)])
                for a in attachment_obj.browse(cr, uid, attachment_ids):
                    vals = {
                        'name': a.name.replace('.pdf', now+'.pdf'),
                        'datas_fname': a.datas_fname.replace('.pdf.pdf', now+'.pdf.pdf')
                           }
                    attachment_obj.write(cr, uid, a.id, vals)

            self.log_picking(cr, uid, ids, context=context)  
            
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
    


