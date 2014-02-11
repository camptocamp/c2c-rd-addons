# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
#import pooler
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import openerp.netsvc
import logging

class sale_order(osv.osv):
    _inherit = "sale.order"

    # this is basically a copy of sale_order.action_ship_create with some modifiations
    def action_ship_internal_create(self, cr, uid, ids, location_id, location_dest_id,*args):
        
        wf_service = netsvc.LocalService("workflow")
        picking_id = False
        move_obj = self.pool.get('stock.move')
        proc_obj = self.pool.get('procurement.order')
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids, context={}):
            proc_ids = []
            output_id = order.shop_id.warehouse_id.lot_output_id.id
            picking_id = False
            for line in order.order_line:
                proc_id = False
                date_planned = datetime.now() + relativedelta(days=line.delay or 0.0)
                date_planned = (date_planned - timedelta(days=company.security_lead)).strftime('%Y-%m-%d %H:%M:%S')

                if line.state == 'done':
                    continue
                move_id = False
                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    #location_id = order.shop_id.warehouse_id.lot_stock_id.id
                    if not picking_id:
                        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.internal')
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                            'name': pick_name,
                            'origin': order.name,
                            'type': 'internal',
                            'state': 'draft',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state':  'none',
                            'company_id': order.company_id.id,
                        })
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name': line.name[:64],
                        'picking_id': picking_id,
                        'product_id': line.product_id.id,
                        'date': date_planned,
                        'date_expected': date_planned,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos_qty,
                        'product_uos': (line.product_uos and line.product_uos.id)\
                                or line.product_uom.id,
                        'product_packaging': line.product_packaging.id,
                        'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id,
                        'sale_line_id': line.id,
                        'tracking_id': False,
                        'state': 'draft',
                        #'state': 'waiting',
                        'note': line.notes,
                        'company_id': order.company_id.id,
                    })

            #val = {}

            # this resets type to 'out' - do not know why, better leave it in draft
            #if picking_id:
            #    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

            #for proc_id in proc_ids:
            #    wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

            #if order.state == 'shipping_except':
            #    val['state'] = 'progress'
            #    val['shipped'] = False

            #    if (order.order_policy == 'manual'):
            #        for line in order.order_line:
            #            if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
            #                val['state'] = 'manual'
            #                break
            #self.write(cr, uid, [order.id], val)
        return True
       
sale_order()

class sale_make_internal_ship_wizard(osv.osv_memory):
    _name = "sale.make.internal.ship.wizard"
    _logger = logging.getLogger(_name)
    _columns = {
        'location_id': fields.many2one('stock.location', 'Location', required=True, domain="[('usage', '=', 'internal')]"),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', required=True, domain="[('usage', '=', 'internal')]"),
        }

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        order = self.pool.get('sale.order').browse(cr, uid, record_id, context=context)
        if order.state in  [ 'done','cancel'] :
            raise osv.except_osv(_('Warning !'),'You can not create internal shippings when sales order is done or canceled.')
        for i in order.picking_ids:
            if i.type== 'internal':
                raise osv.except_osv(_('Warning !'),'Internal shipping already created.')
         
        return False

    def make_internal_shippment(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids)[0]
        self._logger.debug('data `%s`', data)
        record_id = context and context.get('active_id', False)
        order_obj = self.pool.get('sale.order')
        order = order_obj.browse(cr, uid, record_id, context=context)
        
        # allow only one internal
        #internal='n'
        #for i in order.picking_ids:
        #    if i.type== 'internal':
        #        internal = 'y'
        #        raise osv.except_osv(_('Warning !'),'Internal shipping already created.')
        
        #if internal == 'n':
            
            #reloacte the source of out picking
        for i in order.picking_ids:
            if i.type== 'out' and i.state not in ['done', 'cancel']:
                #stock_pick_obj = self.pool.get('stock.picking')
                stock_move_obj = self.pool.get('stock.move')
                loc_id = data['location_dest_id'][0]
                for move in i.move_lines:
                    self._logger.debug('stock_pick write `%s` `%s`', loc_id, move.id)
                    stock_move_obj.write(cr, uid, [move.id], {'location_id' :  loc_id } )
        order_obj.action_ship_internal_create(cr, uid, [record_id], data['location_id'][0], data['location_dest_id'][0])
                        
                        
        # open correct shipping window
        pool = pooler.get_pool(cr.dbname)
        mod_obj = pool.get('ir.model.data')
        act_obj = pool.get('ir.actions.act_window')
        xml_id='action_picking_tree6'
        result = mod_obj._get_id(cr, uid, 'stock', xml_id)
        id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
        result = act_obj.read(cr, uid, id)
        result['domain'] = [('type','=','internal'),('sale_id','=', order.id)]

        return result

sale_make_internal_ship_wizard()
                            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
