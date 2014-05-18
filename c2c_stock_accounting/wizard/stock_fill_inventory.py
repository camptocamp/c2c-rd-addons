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

from openerp.osv import fields, osv
import logging
from openerp.tools.translate import _

class stock_fill_inventory(osv.osv_memory):
    _inherit = "stock.fill.inventory"
    _logger = logging.getLogger(__name__)

    def fill_inventory(self, cr, uid, ids, context=None):    
        if not context:
            context = {}
        if ids and len(ids):
            ids_1 = ids[0]
        inventory_id =  context['active_ids'] and context['active_ids'][0]
        if ids_1 and inventory_id:
          self._logger.debug('FGF inventory %s %s '% (ids_1,inventory_id))
          fill_inventory = self.browse(cr, uid, ids_1, context=context)
          
          if fill_inventory.location_id:
            inv_obj = self.pool.get('stock.inventory')
            inv_date = inv_obj.read(cr, uid, inventory_id,['date'],context)['date']
            self._logger.debug('FGF fill location %s'% (fill_inventory.location_id.id))
            self._logger.debug('FGF fill date %s'% (inv_date))
            context['inv_date'] = inv_date
            res = self.fill_inventory_modified(cr, uid, ids, context)
            self._logger.debug('FGF fille inventory res %s'% (res))
            inventory_obj = self.pool.get('stock.inventory')
            inventory_obj.write(cr, uid, inventory_id , {'recursive' : fill_inventory.recursive, 'location_id': fill_inventory.location_id.id})
            self._logger.debug('FGF fill inventory write ')

          inventory_line_obj = self.pool.get('stock.inventory.line')   
          if not fill_inventory.display_with_zero_qty:
            ids_zero = inventory_line_obj.search(cr, uid, [('inventory_id','=', inventory_id), ('product_qty','=', '0')])
            self._logger.debug('FGF fill zero ids %s' % (ids_zero))
            inventory_line_obj.unlink(cr, uid, ids_zero)
          ids_update = inventory_line_obj.search(cr, uid, [('inventory_id','=', inventory_id)])
          ids2 = ','.join([str(id) for id in ids_update])
          if ids_update:
            cr.execute("""update stock_inventory_line
                         set product_qty_calc = product_qty
                       where id in (%s)""" % ids2)
            
        #return res
        return {'type': 'ir.actions.act_window_close'}
        
    def fill_inventory_modified(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        this is a FULL compy of the stock/wizard/fill_inventory.py
           except that the search is modified to reflect the inventory date
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventory_line_obj = self.pool.get('stock.inventory.line')
        location_obj = self.pool.get('stock.location')
        product_obj = self.pool.get('product.product')
        stock_location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        if ids and len(ids):
            ids = ids[0]
        else:
             return {'type': 'ir.actions.act_window_close'}
        fill_inventory = self.browse(cr, uid, ids, context=context)
        res = {}
        res_location = {}

        if fill_inventory.recursive:
            location_ids = location_obj.search(cr, uid, [('location_id',
                             'child_of', [fill_inventory.location_id.id])], order="id",
                             context=context)
        else:
            location_ids = [fill_inventory.location_id.id]

        res = {}
        flag = False

        for location in location_ids:
            datas = {}
            res[location] = {}
            if context.get('inv_date') and context['inv_date']:
                move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done'),('date','<=',context['inv_date'])], context=context)
            else:
                move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done')], context=context)

            for move in move_obj.browse(cr, uid, move_ids, context=context):
                lot_id = move.prodlot_id.id
                prod_id = move.product_id.id
		if  move.location_dest_id.id == move.location_id.id :
	            qty = 0.0
		elif move.location_dest_id.id == location:
                    qty = uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
                else:
                    qty = -uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)


                if datas.get((prod_id, lot_id)):
                    qty += datas[(prod_id, lot_id)]['product_qty']

                datas[(prod_id, lot_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': qty, 'product_uom': move.product_id.uom_id.id, 'prod_lot_id': lot_id}

            if datas:
                flag = True
                res[location] = datas

        if not flag:
            raise osv.except_osv(_('Warning !'), _('No product in this location.'))

        for stock_move in res.values():
            for stock_move_details in stock_move.values():
                stock_move_details.update({'inventory_id': context['active_ids'][0]})
                domain = []

                if fill_inventory.set_stock_zero:
                    stock_move_details.update({'product_qty': 0})

                for field, value in stock_move_details.items():
                    domain.append((field, '=', value))

                line_ids = inventory_line_obj.search(cr, uid, domain, context=context)

                if not line_ids:
                    inventory_line_obj.create(cr, uid, stock_move_details, context=context)

                inventory_line_obj = self.pool.get('stock.inventory.line')




        # return {'type': 'ir.actions.act_window_close'}
        return res


stock_fill_inventory()



