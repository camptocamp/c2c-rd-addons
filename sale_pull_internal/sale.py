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
import time
from osv import fields, osv
from tools.translate import _
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
        'pull_intern_date' : fields.datetime('Creation of internal Pull'),
        'pull_intern' : fields.boolean( 'Include in Pull Pick', help="Automatic will be included in Pull Picking evaluation"),
        'state_internal': fields.selection([('', 'Unused'), ('calculation', 'Calculation'), ('calculated', 'Calculated')], 'Internal Pull Calcualtion', \
                help="This indicates the status of the internal pull calculation"),
    }
    _defaults = {
        'pull_intern' : True,		    
		    }

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'pull_intern_date': False,
            'pull_intern': True,
            'state_internal': False,
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)


    def order_pull_internal(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        _logger = logging.getLogger(__name__)
        now = time.strftime('%Y-%m-%d %H:%M:%S'),
        #_logger.info('FGF sale pull internal context %s' % (context))
        location_dest_id = ''
        if context['form'] and context['form']['location_dest_id']:
            location_dest_id = context['form']['location_dest_id'][0]
        
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
        main_location_id = False
        loc_ids = []
        for order in self.browse(cr, uid, ids, context):
            if order.pull_intern and order.state == 'progress' :
                order_ids.append(order.id)
        #order.write(cr, uid, order_ids,{'state_internal':'calculation'}, context)
        if not order_ids:
            return

        order_ids2 = (', '.join(map(str,order_ids)))
        cr.execute("""select shop_id, product_id, l.name, product_packaging, sum(product_uom_qty) as qty_requested
                   from sale_order_line l,
                        sale_order o
                  where l.order_id in (%s)
                    and l.order_id = o.id
		    and product_id is not null
                  group by o.shop_id, product_id, l.name, product_packaging""" % order_ids2)
        for product_qty in cr.dictfetchall():
            #_logger.info('FGF sale pull internal %s' % (product_qty))
            product_id = product_qty['product_id']
            shop_id = product_qty['shop_id']
            product_packaging = product_qty['product_packaging']
            name = product_qty['name']
            qty_requested = product_qty['qty_requested']
            for shop in shop_obj.browse(cr, uid, [shop_id], context=context):
                if not location_dest_id:
                    location_dest_id = shop.warehouse_id.lot_output_id.id
                address_id = shop.warehouse_id.partner_address_id and shop.warehouse_id.partner_address_id.id 
		loc_fallback_id = shop.warehouse_id.lot_stock_id.id
	    # update source location of auto SO
            # select source location
            cr.execute("""select id
                   from stock_location
                  where sequence > 0
		    and usage='internal'
                  order by sequence""") 
            for loc in cr.fetchall():
                #_logger.info('FGF sale location %s ' % (loc))
                location_id = loc[0]
                context['location_id'] = loc[0]
                context['location'] = loc[0]
                #_logger.info('FGF sale location context %s ' % (context))
                #qty_availiable = product_obj.get_product_available(cr, uid, [product_id] , context)
                qty_available = 0.0
		if product_id:
                  for product in product_obj.browse(cr, uid, [product_id], context):
                      qty_available = product.qty_available 
                #qty_avail = qty_availiable.get(product_id)
                #_logger.info('FGF sale location product %s %s %s ' % (product_id, qty_available, qty_requested))
                ml = {'shop_id':shop_id, 'location_id':location_id,  'location_dest_id':location_dest_id, 'product_id': product_id, 'name': name, 'product_packaging': product_packaging}
                if qty_requested > 0 and qty_available >0:
                  if qty_available >= qty_requested:
                    ml.update({'product_qty':qty_requested})
                    qty_requested = 0.0
                    qty_available -= qty_requested
                    move_lines.append(ml)
                    if location_id not in loc_ids:
                        if not loc_ids:
                            main_location_id = location_id
                        loc_ids.append(location_id)
                    #_logger.info('FGF sale location product available %s %s %s ' % (product_id, qty_available, qty_requested))
                  elif qty_available > 0 and qty_available < qty_requested:
                    qty_requested = qty_requested - qty_available
                    ml.update({'product_qty':qty_available})
                    move_lines.append(ml)
                    if location_id not in loc_ids:
                        if not loc_ids:
                            main_location_id = location_id
                        loc_ids.append(location_id)
                
            if qty_requested > 0.0:
                back_log_lines.append({'product_id': product_id, 'product_qty':qty_requested, 'name':name, 'product_packaging': product_packaging})

            
	# update SO , source location to location_dest_id
	cr.execute("""update stock_move
	                 set location_id = %s
		       where picking_id in (select id 
		                from stock_picking 
		               where sale_id in (%s)
		                 and state != 'done')""" % (location_dest_id, order_ids2))
        # now we create a stock_picking for each location
        pick_vals = {
                'type' : 'internal',
                'move_type' : 'direct',
                'invoice_state': 'none',
                'state': 'draft',
                'date_done': now,
                'max_date': now,
                'min_date': now,
                #'stock_journal_id': stock_journal_id #FIXME do not know where this comes from
                }

        move_vals = {
                'location_dest_id' : location_dest_id,
                'date': now,
                'date_expected': now,
                }

        sequence_obj = self.pool.get('ir.sequence')
        seq_obj_name =  'stock.picking' 
        for loc in loc_ids:
            pick = pick_vals
            for addr in  location_obj.browse(cr,uid,[loc],context):
                address_id = addr.id
                pick['origin'] = _('auto pull picking')+' '+ addr.name
            #if address_id:
            #    pick['address_id'] = address_id
            pick['name'] =  self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.internal') 
            # FIXME add the move lines for this location
            stock_moves = {}
            stock_moves.update( move_vals )
            stock_moves['location_id'] = loc
            pick.update( stock_moves )
            #_logger.info('FGF sale pick %s ' % (pick)) 
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
                       'name'  :  line['name'],
                       'product_id' : line['product_id'],
                       'product_uom' : product_obj.read(cr, uid, line['product_id'])['uom_id'][0],
                       'product_qty' : line['product_qty'],
                       'picking_id'  : picking_id,
                       'prodlot_id'  : prod_lot_id,
                       'product_packaging' : line['product_packaging']
                       }
                    ml.update(mlt)
                    ml.update(move_vals)
                    #_logger.info('FGF sale move line %s ' % (ml)) 
                    move_obj.create(cr, uid, ml,  context=context)

        if back_log_lines:
            #_logger.info('FGF back_log lines %s ' % (back_log_lines))
            pick = pick_vals
            # create residual picking - must be processed manually
            if main_location_id:
                loc = main_location_id
            else:
		loc = loc_fallback_id
            pick['location_id'] = loc
	    if loc:
              for add in location_obj.browse(cr, uid, [loc], context):
                pick['address_id'] = add.address_id.id
	    if pick.get('name'):
	        del pick['name']
            pick['origin'] = _('back log')
            picking_id = picking_obj.create(cr, uid, pick, context=context)
            for l in back_log_lines:
              line = dict(l)
	      if line['product_id']:
                ml = pick
                prod_lot_id = ''
                mlt = {
                       'name'  : line['name'],
                       'product_id' : line['product_id'],
                       'product_uom' : product_obj.read(cr, uid, line['product_id'])['uom_id'][0],
                       'product_qty' : line['product_qty'],
                       'picking_id'  : picking_id,
                       'prodlot_id'  : prod_lot_id,
                       'product_packaging': line['product_packaging'],
                       }
                ml.update(mlt)
                ml.update(move_vals)
                #_logger.info('FGF sale move line %s ' % (ml))
                move_obj.create(cr, uid, ml,  context=context)
	    #picking_obj.action_cancel(cr, uid, [picking_id], context=None)

            
        self.write(cr, uid, order_ids, {'state_internal':'calculated','pull_intern_date':now}, context=None )

        return


sale_order()

class sale_order_pull_internal(osv.osv_memory):
    _name = "sale.order.pull.internal"
    _description = "Create Pull Pickings"
    _columns = {
        'location_dest_id': fields.many2one('stock.location', 'Destination for internal Moves',  domain="[('usage', '=', 'internal')]"),
    }
    _defaults = {
    }


    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        order = self.pool.get('sale.order').browse(cr, uid, record_id, context=context)
        #if order.state != 'progress':
        #    raise osv.except_osv(_('Warning !'),'You can only internal pull pickings from SO in progres.')
        return False


    def make_picking_internal(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('sale.order')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        new_pick = []
        if context is None:
            context = {}
        context['form'] = self.read(cr, uid, ids)[0]
        order_obj.order_pull_internal(cr, uid, context.get(('active_ids'), []), context )

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

