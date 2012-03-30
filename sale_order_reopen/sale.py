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


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def allow_reopen(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)

        _logger.info('FGF sale_order reopen %s' % (ids))
        for order in self.browse(cr, uid, ids, context):
            if order.picking_ids:
                for pick in order.picking_ids:
                    if pick.state not in ['draft','cancel']: # very restrictive
                        raise osv.except_osv(_('Error'), _('You cannot reset this Sale Order to draft, because picking %s %s is not in state draft or cancel ')% (pick.name, pick.state))

            if order.invoice_ids:
                for inv in order.picking_ids:
                    if inv.state not in ['draft','cancel']: # very restrictive
                        raise osv.except_osv(_('Error'), _('You cannot reset this Sale Order to draft, because invoice %s %s is not in state draft or cancel ')% (inv.name, inv.state))

        return true

    

    def action_reopen(self, cr, uid, ids, context=None):
        """ Changes SO from to draft.
        @return: True
        """
        _logger = logging.getLogger(__name__)

        _logger.info('FGF sale_order action reopen %s' % (ids))
        account_invoice_obj = self.pool.get('account.invoice')
        stock_picking_obj = self.pool.get('stock.picking')
        report_xml_obj = self.pool.get('ir.actions.report.xml')
        attachment_obj = self.pool.get('ir.attachment')

        now = ' ' + _('Invalid') + time.strftime(' [%Y%m%d %H%M%S]')
        for order in self.browse(cr, uid, ids):
            # FIXME must not cancel canceld resources
            picking_ids = stock_picking_obj.search(cr, uid, [('state','!=','cancel')])
            stock_picking_obj.cancel_assign(cr, uid, picking_ids)
            invoice_ids = account_invoice_obj.search(cr, uid, [('state','!=','cancel')])
            account_invoice_obj.action_cancel(cr, uid, invoice_ids)
            

            # for some reason datas_fname has .pdf.pdf extension
            report_ids = report_xml_obj.search(cr, uid, [('model','=', 'sale.order'), ('attachment','!=', False)])
            for report in report_xml_obj.browse(cr, uid, report_ids):
                aname = report.attachment.replace('object','pick')
                aname = eval(aname)+'.pdf'
                attachment_ids = attachment_obj.search(cr, uid, [('res_model','=','sale.order'),('datas_fname', '=', aname),('res_id','=',order.id)])
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

        
    
sale_order()
    


