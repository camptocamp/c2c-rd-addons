# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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
import pooler
import time
from osv import fields, osv
from tools.translate import _
import netsvc
import logging

class stock_location(osv.osv):
    _inherit = "stock.location"

    _columns = {
        'sequence': fields.integer('Sequence', help="Important when pull pickings are create, the execution order will be decided based on this, low number is higher priority."),
    }

stock_location()

class sale_order(osv.osv):
    _inherit = "sale.order"
    

    _columns = {
        'state_internal': fields.selection([('', 'Unused'), ('calculation', 'Calculation'), ('calculated', 'Calculated')], 'Internal Pull Calcualtion', \
                help="This indicates the status of the internal pull calculation"),
    }


    def order_pull_internal(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        _logger = logging.getLogger(__name__)
        
        product_obj = self.pool.get('product.product')
        location_obj = self.pool.get('stock.location')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        lot_obj = self.pool.get('stock.production.lot')
        company_obj = self.pool.get('res.company')
        shop_obj = self.pool.get('sale.shop')

        if not context.get('company_id'):
            company_id = company_obj._company_default_get(cr, uid, 'stock.company', context=context),
            context['company_id'] = company_id[0]

        order_ids =[]

        move_lines = []
        back_log_lines = []
        loc_ids = []
        for order in self.browse(cr, uid, ids, context):
            if not order.state_internal and order.state == 'progress':
                order_ids.append(order.id)
        # FIXME uncomment# order.write(cr, uid, order_ids,{'state_internal':'calculation'} )

        order_ids2 = (', '.join(map(str,order_ids)))
        cr.execute("""select shop_id, product_id, sum(product_uom_qty) as qty_requested
                   from sale_order_line l,
                        sale_order o
                  where o.id = l.order_id
                    and order_id in (%s)
                  group by o.shop_id, product_id""" % order_ids2)
        for product_qty in cr.dictfetchall():
            _logger.info('FGF sale pull internal %s' % (product_qty))
            product_id = product_qty['product_id']
            shop_id = product_qty['shop_id']
            qty_requested = product_qty['qty_requested']
            for shop in shop_obj.browse(cr, uid, [shop_id], context=context):
                location_dest_id = shop.warehouse_id.lot_output_id.id
                address_id = shop.warehouse_id.partner_address_id and shop.warehouse_id.partner_address_id.id 
            # select source location
            cr.execute("""select id
                   from stock_location
                  where sequence is not null
                  order by sequence""") 
            for loc in cr.fetchall():
                _logger.info('FGF sale location %s ' % (loc))
                location_id = loc[0]
                context['location_id'] = loc[0]
                _logger.info('FGF sale location id %s ' % (context))
                qty_availiable = product_obj.get_product_available(cr, uid, [product_id] , context)
                qty_avail = qty_availiable.get(product_id)
                _logger.info('FGF sale location product %s %s %s ' % (product_id, qty_avail, qty_requested))
                ml = {'shop_id':shop_id, 'location_id':location_id, 'product_id': product_id,}
                if qty_requested > 0 and qty_avail >0:
                  if qty_avail > qty_requested:
                    qty_requested = 0.0
                    ml.update({'product_qty':qty_requested})
                    move_lines.append(ml)
                    if location_id not in loc_ids:
                        loc_ids.append(location_id)
                  elif qty_available > 0 and qty_avail > qty_requested:
                    qty_requested = qty_requested - qty_avail
                    ml.update({'product_qty':qty_avail})
                    move_lines.append(ml)
                    if location_id not in loc_ids:
                        loc_ids.append(location_id)
                
            if qty_requested > 0.0:
                back_log_lines.append({'product_id': product_id, 'product_qty':qty_requested})
        _logger.info('FGF back_log lines %s ' % (back_log_lines))

            
        # now we create a stock_picking for each location
        pick_vals = {
                'origin': _('auto Pull Picking'),
                'type' : 'internal',
                'move_type' : 'direct',
                'invoice_state': 'none',
                'state': 'draft',
                'date_done': time.strftime('%Y-%m-%d %H:%M:%S'),
                #'stock_journal_id': stock_journal_id #FIXME do not know where this comes from
                }

        location_dest_id = 1      # FIXME
        move_vals = {
                'location_dest_id' : location_dest_id,
                }

        sequence_obj = self.pool.get('ir.sequence')
        seq_obj_name =  'stock.picking' 
        for loc in loc_ids:
            pick = pick_vals
            address_id = location_obj.read(cr,uid,loc)['address_id']
            if address_id:
                pick['address_id'] = address_id
            pick['name'] = sequence_obj.get(cr, uid, seq_obj_name)

            # FIXME add the move lines for this location
            stock_moves = {}
            stock_moves.update( move_vals )
            stock_moves['location_id'] = loc
            pick.update( stock_moves )
            _logger.info('FGF sale pick %s ' % (pick)) 
            picking_id = picking_obj.create(cr, uid, pick, context=context)
            for l in move_lines:
                line = dict(l)
                if line['location_id'] == loc:
                    ml = pick
                    prod_lot_id = ''
                    lot_ids = lot_obj.search(cr, uid, [('product_id','=',line['product_id'])])
                    for lot in lot_obj.browse(cr, uid, lot_ids, context=None):
                       if lot.stock_available > 0:
                           prod_lot_id = lot.id
                    mlt = {
                       'name'  : 'x',
                       'product_id' : line['product_id'],
                       'product_uom' : product_obj.read(cr, uid, line['product_id'])['uom_id'][0],
                       'product_qty' : line['product_qty'],
                       'picking_id'  : picking_id,
                       'prodlot_id'  : prod_lot_id,
                       }
                    ml.update(mlt)
                    ml.update(move_vals)
                    _logger.info('FGF sale move line %s ' % (ml)) 
                    move_obj.create(cr, uid, ml,  context=context)

        if back_log_lines:
            _logger.info('FGF back_log lines %s ' % (back_log_lines))
            # FIXME - must write an internal pick

        # FIXME uncomment# order.write(cr, uid, order_ids,{'state_internal':'calculated'} )

        return


sale_order()

class sale_order_pull_internal(osv.osv_memory):
    _name = "sale.order.pull.internal"
    _description = "Create Pull Pickings"
    _columns = {
        'dummy': fields.boolean('Dummy', help='Check the box to group the invoices for the same customers'),
    }
    _defaults = {
        'dummy': False
    }

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        order = self.pool.get('sale.order').browse(cr, uid, record_id, context=context)
        if order.state != 'progress':
            raise osv.except_osv(_('Warning !'),'You can only internal pull pickings from SO in progres.')
        return False


    def make_picking_internal(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        new_pick = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        order_obj.order_pull_internal(cr, uid, context.get(('active_ids'), []), )

#        wf_service = netsvc.LocalService("workflow")
#        for id in context.get(('active_ids'), []):
#            wf_service.trg_validate(uid, 'sale.order', id, 'manual_invoice', cr)
#
#        for o in order_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
#            for i in o.invoice_ids:
#                newinv.append(i.id)
#
        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree6')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
#        result['domain'] = "[('id','in', ["+','.join(map(str,newinv))+"])]"

        return result


            
sale_order_pull_internal()

