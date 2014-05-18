# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
 
from openerp.osv import fields, osv
import openerp.netsvc
from openerp.tools.translate import _
import time
import logging


class mrp_production(osv.osv):
    _inherit = 'mrp.production'


    def allow_reopen(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)
        return True
    

    def action_reopen(self, cr, uid, ids, context=None):
        """ Changes mrp state from done to draft.
        @return: True
        """
        _logger = logging.getLogger(__name__)
        self.allow_reopen(cr, uid, ids, context=None)
        move_line_obj = self.pool.get('stock.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_move_obj = self.pool.get('account.move')
        report_xml_obj = self.pool.get('ir.actions.report.xml')
        attachment_obj = self.pool.get('ir.attachment')

        now = ' ' + _('Invalid') + time.strftime(' [%Y%m%d %H%M%S]')
        for mrp in self.browse(cr, uid, ids):
            _logger.debug('FGF production action reopen mrp %s ' %(mrp.name)   )
            # FIXME
            # current implementation deletes all stock_moves (creates some work
            # to reinsert lots etc)
            # reset to waiting is better but needs complex workflow modification
            # no time to do and test this
            #move_line_obj.write(cr, uid, ml_ids, {'state':'waiting'})
            ml_ids = []
            for ml in mrp.move_lines:
                ml_ids.append(ml.id)
            for ml in mrp.move_lines2:
                ml_ids.append(ml.id)
            for ml in mrp.move_created_ids:
                ml_ids.append(ml.id)
            for ml in mrp.move_created_ids2:
                ml_ids.append(ml.id)
            _logger.debug('FGF production action reopen mrp %s ' %(ml_ids)   )
            #move_line_obj.write(cr, uid, ml_ids, {'state':'waiting'})
            move_line_obj.write(cr, uid, ml_ids, {'state':'draft'})
            # client has also produciton orders without BOM, so we do not want
            # to delete the entered lines, and no new ones will be created
            # automatically
            if mrp.bom_id:
                move_line_obj.unlink(cr, uid, ml_ids)
            # we have to handle real time accounting stock moves
            #FIXME - performance, should be an id - link to production 
            #aml_ids = account_move_line_obj.search(cr, uid, [('production_id','=',mrp.id)])
            aml_ids = account_move_line_obj.search(cr, uid, [('ref','=',mrp.name)])
            _logger.debug('FGF production action reopen move_lines %s ' %(aml_ids)   )
            move_ids = []
            
            for aml in account_move_line_obj.browse(cr, uid, aml_ids):
                if aml.move_id.id not in move_ids:
                    move_ids.append(aml.move_id.id)
                _logger.debug('FGF production action reopen move %s ' %(move_ids)   )
                account_move_line_obj.write(cr, uid, [aml.id], {'ref': aml.ref or '' + now})
                
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
            report_ids = report_xml_obj.search(cr, uid, [('model','=', 'stock.production'), ('attachment','!=', False)])
            for report in report_xml_obj.browse(cr, uid, report_ids):
                if report.attachment: 
                   aname = report.attachment.replace('object','mrp')
                   if eval(aname):
                       aname = eval(aname)+'.pdf'
                       attachment_ids = attachment_obj.search(cr, uid,
                               [('res_model','=','mrp.production'),('datas_fname', '=', aname),('res_id','=',mrp.id)])
                       for a in attachment_obj.browse(cr, uid, attachment_ids):
                          vals = {
                        'name': a.name.replace('.pdf', now+'.pdf'),
                        'datas_fname': a.datas_fname.replace('.pdf.pdf', now+'.pdf.pdf')
                           }
                          attachment_obj.write(cr, uid, a.id, vals)

            #self.write(cr, uid, mrp.id, {'state':'confirmed'})
            self.write(cr, uid, mrp.id, {'state':'draft'})
            wf_service = netsvc.LocalService("workflow")

            wf_service.trg_delete(uid, 'mrp.production', mrp.id, cr)
            wf_service.trg_create(uid, 'mrp.production', mrp.id, cr)

            message = _("Manufacturing order '%s' is reset to waiting") % (
                    mrp.name,)
            self.log(cr, uid, mrp.id, message)            
        return True


#    def button_reopen(self, cr, uid, ids, context=None):
#        _logger = logging.getLogger(__name__)   
#        self.allow_reopen(cr, uid, ids, context)
#        _logger.debug('FGF production allow open  '   )
#        self.write(cr, uid, ids, {'state':'draft'})
#        _logger.debug('FGF production draft  '   )
#        self.log_production(cr, uid, ids, context=context)
#        _logger.debug('FGF production log'   )

        
    
mrp_production()
    


