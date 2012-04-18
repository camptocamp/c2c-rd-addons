# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-18 23:44:30+02
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
import time
from osv import fields,osv
import decimal_precision as dp

import logging

class chricar_budget_production(osv.osv):
     _name = "chricar.budget.production"
     _columns = {
          'name'         : fields.char    ('Production Budget', size=64, required=True),
          'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year',required=True),
          'budget_version_ids'   : fields.one2many('c2c_budget.version','budget_production_id','Budget Versions '),
      }

     def copy(self, cr, uid, id, default=None, context=None):
        prod = self.browse(cr, uid, id, context=context)
        default = default or {}

        default['is_current'] = False
        if not default.get('name', False):
            v = ' - v' + time.strftime("%Y-%m-%d")
            default['name'] = prod.name + v  
        res = super(chricar_budget_production, self).copy(cr, uid, id, default, context)
        # FIXME - update budget_versions
        #?? ids = self.search(cr, uid, [('parent_id','child_of', [res])])
        #cr.execute('update budget_version name = name ||' %s ' , is_current=False where budget_production_id in ('+','.join(map(str,ids))+')', [v])
        # udpate new current
        # set budget_version_next_id, = new next
        # set budget_version_pervious_id, = new previous
        return res

chricar_budget_production()

  
class chricar_budget(osv.osv):
     _name = "chricar.budget"
     _logger = logging.getLogger(_name)

     def product_id_change(self, cr, uid, ids,  product, price_unit_id, uom_id):
         prod= self.pool.get('product.product').browse(cr, uid,product)

         pu = prod.price_unit_id.id
         if not price_unit_id:
            price_unit_id = pu

         prod_uom_po = prod.uom_po_id.id
         if not uom_id:
            uom_id = prod_uom_po
         res = {'value': {'price_unit_id':pu,
                          'product_uom': uom,
                         }
               }
         return res


     def _product_qty_line(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.surface * line.yield_qty
        return res

     def _product_qty_stock(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.product_id.qty_available
        return res

     def _amount_line(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.surface * line.yield_qty) * line.price  / line.price_unit_id.coefficient
        return res

        
     def _amount_qty_stock(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.product_qty_stock * line.price / line.price_unit_id.coefficient)
        return res

     def _amount_prod_lot(self, cr, uid, ids, name, args, context=None):
         aml = self.pool.get('account.invoice')
         move_obj = self.pool.get('stock.move')
         pick_obj = self.pool.get('stock.picking')
         res = {}
         _logger = logging.getLogger(__name__) 
         for line in self.browse(cr, uid, ids, context=context):
           amount = 0
	   if line.prod_lot_id:
             #move_ids = move_obj.search(cr, uid, [('prodlot_id','=',line.prod_lot_id.id),('picking_id','>','0')])
             move_ids = move_obj.search(cr, uid, [('prodlot_id','=',line.prod_lot_id.id)])
	     _logger.info('FGF move_ids %s' % (move_ids))
             for move in move_obj.browse(cr, uid, move_ids):
	       if  move.picking_id:
		_logger.info('FGF move pick id %s' % (move.picking_id))
		if move.picking_id and move.picking_id.invoice_ids :
                    for inv in move.picking_id.invoice_ids:
		      _logger.info('FGF move pick inv %s' % (inv))
                      if inv.invoice_line:
			for inv_line in inv.invoice_line:
		          _logger.info('FGF move pick inv line %s' % (inv_line))
                          if inv_line.product_id == line.product_id: # FIXME problematic if 2 lots are in one invoice 
			    if inv.type == 'out_invoice' and inv.state in ['done','paid']:
                               amount += inv_line.price_subtotal
			    else:
                               amount -= inv_line.price_subtotal

	                    _logger.info('FGF move pick inv line amount %s' % (amount))
           res[line.id] = amount
         return res

     def _yield_line(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.surface and line.surface > 0.0:
                res[line.id] = ((line.surface * line.yield_qty) * line.price  / line.price_unit_id.coefficient) / line.surface
            else:
                res[line.id] = 0.0
        return res

     def name_get(self, cr, uid, ids, context=None):
          if not len(ids):
               return []
          reads = self.read(cr, uid, ids, ['product_id','budget_version_id'], context)
          res = []
          for record in reads:
               # FIXME read code from bud version
               #code = record.budget_version_id[0].code
               code = ''
               if not code:
                   code = record['budget_version_id'][1]
               name = record['product_id'][1]
               res.append((record['id'],code + ' ' + name))
          return res
              
     def _harvest(self, cr, uid, ids, name, args, context=None):
        res = {}
        harvest = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            product       = line.product_id.id
            fy_date_start = line.budget_version_id.budget_id.start_date
            fy_date_stop  = line.budget_version_id.budget_id.end_date
            cr.execute("""select coalesce(sum(product_qty),0) from stock_move s,
                                                       stock_location l
                                 where state='done'
                                   and l.usage = 'production'
                                   and l.id = s.location_id
                                   and product_id = %d
                                   and to_char(date_expected,'YYYY-MM-DD') between '%s' and '%s'""" % (product,fy_date_start,fy_date_stop))
            harvest = cr.fetchone()
            self._logger.debug('harvest `%s` `%s` `%s` `%s`', product, fy_date_start, fy_date_stop, harvest[0])
            harvest = harvest[0]
            res[line.id]  = harvest
        return res


     def _harvest_net(self, cr, uid, ids, name, args, context=None):
        res = {}
        self._logger.debug('harvest yield net')
        for line in self.browse(cr, uid, ids, context=context):
            harvest_yield = 0.0
            harvest = 0.0
            surface_used  = line.surface
            if line.harvest_soil:
                harvest = line.harvest * (100 - line.harvest_soil ) /100
            else:
                harvest = line.harvest
            self._logger.debug('harvest yield 2 `%s``%s`', surface_used, harvest)
            if surface_used and surface_used <> 0.0  and  harvest and harvest <> 0.0:
                 harvest_yield = harvest / surface_used
            res[line.id]  = harvest_yield
        return res

     def _harvest_yield(self, cr, uid, ids, name, args  , context=None):
        res = {}
        self._logger.debug('harvest yield 1')
        for line in self.browse(cr, uid, ids, context=context):
	    harvest_yield = 0.0
	    harvest = 0.0
            surface_used  = line.surface
            harvest       = line.harvest
            self._logger.debug('harvest yield 2 `%s` `%s`', surface_used,harvest)
            if surface_used and surface_used <> 0.0  and  harvest and harvest <> 0.0:
                 harvest_yield = harvest / surface_used
            res[line.id]  = harvest_yield
        return res

     def _harvest_yield_diff(self, cr, uid, ids, name, args, context=None):
        res = {}
        self._logger.debug('harvest yield 2')
        for line in self.browse(cr, uid, ids, context=context):
	    harvest_yield_diff = 0.0
            yield_qty  = line.yield_qty
            harvest_net = line.harvest_net
            self._logger.debug('harvest yield 2 `%s` `%s`', yield_qty,harvest_net)
            if yield_qty <> 0.0  and harvest_net <> 0.0:
                 harvest_yield_diff =  ((harvest_net / yield_qty) - 1.0) * 100
            res[line.id]  = harvest_yield_diff
        return res


     _columns = {
       'amount'             : fields.function(_amount_line, method=True, string='Total Sales Planned' ,digits_compute=dp.get_precision('Budget'),
                                    help="Planned Production Quantity * Price"),
       #'budget_version_id'  : fields.integer ('Budget version', required=True),
       'budget_version_id'  : fields.many2one('c2c_budget.version','Budget Version', required=True),
       'location_ids'       : fields.one2many('chricar.budget.surface','budget_id','Location Surface used'),
       'name'               : fields.text    ('Notes'),
       #'partner_id'         : fields.many2one('res.partner','Partner'),
       'price'              : fields.float   ('Price', digits=(16,2),help="Exected average price"),
       'price_unit_id'      : fields.many2one('c2c_product.price_unit','Price Unit', required=True),
       'product_id'         : fields.many2one('product.product','Product', select=True, required=True),
       'product_uom'        : fields.many2one('product.uom', 'Product UOM', required=True),
       'product_qty'        : fields.function(_product_qty_line, method=True, string='Planned Quantity' ,digits=(16,0),
                             help="Surface * Yield"),
       'surface'            : fields.float   ('Surface (ha)', digits=(16,2)),
       'yield_qty'          : fields.float   ('Yield qty/ha', digits=(16,0)),
       'yield_sale'         : fields.function(_yield_line, method=True, string='Sales/ha' ,digits_compute=dp.get_precision('Budget'),
                              help="Planned Sales / Surface"),
       'date_cultivation'   : fields.date    ('Date Cultivation'),
       'sale_from'          : fields.date    ('Sale start', help="""Sale lines will be created aliquot for not individually planned sales""", required=True),
       'sale_to'            : fields.date    ('Sale end'),
       'harvest_period_id'  : fields.many2one('account.period','Harvest Period',help="In this period the harvest will be evaluated using product cost price", required=True),
       'harvest'            : fields.function(_harvest, method=True, string='Harvest' ,digits=(16,0), help="Harvested qty this year", readonly=True),
       'harvest_soil'       : fields.float   ('Soil %', digits=(16,0),help="The percentag of soil")       ,
       'harvest_net'        : fields.function(_harvest_net, method=True, string='Net/ha' ,digits=(16,0), help="Harvested qty net - without soil this year", readonly=True),
       'harvest_yield'      : fields.function(_harvest_yield, method=True, string='Yield/ha' ,digits=(16,0), help="Harvested yield qty this year", readonly=True),
       'harvest_yield_diff' : fields.function(_harvest_yield_diff, method=True, string='Yield Net Diff' ,digits=(16,2), help="Harvested yield Diff", readonly=True),
       'prod_lot_id'        : fields.many2one('stock.production.lot', 'Production Lot', domain="[('product_id','=',product_id)]"),
       'amount_prod_lot'    : fields.function(_amount_prod_lot, method=True, string='Sales Prod Lot' ,digits_compute=dp.get_precision('Budget'),help="Invoiced production lots"),
       'product_qty_stock'  : fields.related ('product_id', 'qty_available', type="float",  string="On Stock", readonly = True ,help="Uninvoiced Stock"),
       'amount_qty_stock'   : fields.function(_amount_qty_stock, method=True, string='Stock Sale Value' ,digits_compute=dp.get_precision('Budget'),help="Stock Qty * Planned Sale Price"),
}
     _defaults = {
       'budget_version_id' : lambda *a: 1,
}
     _order = "name"

     _sql_constraints = [
        ('surface_0', 'CHECK (surface>0)',  'Surface must be greater than 0 !'),
    ]


     def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'location_ids': []})
        budget = self.browse(cr, uid, id, context=context)
        default['name'] = (budget['name'] or '') + '(copy)'
        return super(chricar_budget, self).copy(cr, uid, id, default, context)


chricar_budget()

class chricar_budget_surface(osv.osv):
     _name = "chricar.budget.surface"
     _logger = logging.getLogger(_name)

     def _surface_location(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.location_id.capacity
        return res

     def _harvest(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for line in self.browse(cr, uid, ids, context=context):
	    harvest = 0.0
            product       = line.budget_id.product_id.id
            location      = line.location_id.id
            fy_date_start = line.budget_id.budget_version_id.budget_id.start_date
            fy_date_stop  = line.budget_id.budget_version_id.budget_id.end_date
            self._logger.debug('harvest detail `%s` `%s` `%s` `%s`', product, location, fy_date_start, fy_date_stop)
            cr.execute("""select coalesce(sum(product_qty),0)  from stock_move s,
                                                       stock_location l
                                 where state='done'
                                   and l.usage = 'production'
                                   and l.id = s.location_id
                                   and s.product_id = %d
                                   and s.location_id = %d
                                   and to_char(date_expected,'YYYY-MM-DD') between '%s' and '%s'""" % (product,location,fy_date_start,fy_date_stop))
            harvest = cr.fetchone()
            harvest = harvest[0]
            self._logger.debug('harvest detail 2 `%s` `%s` `%s` `%s` `%s`', product, location, fy_date_start, fy_date_stop, harvest)
            res[line.id]  = harvest
        return res

     def _harvest_yield(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for line in self.browse(cr, uid, ids, context=context):
	    harvest_yield_detail = 0.0  
            surface_used_detail  = line.name
            harvest_detail       = line.harvest
            self._logger.debug('harvest yield detail `%s` `%s` `%s`', name, surface_used_detail, harvest_detail)
            if surface_used_detail and surface_used_detail <> 0.0 and harvest_detail and harvest_detail <> 0.0:
                 harvest_yield_detail = harvest_detail / surface_used_detail
            res[line.id]  = harvest_yield_detail
        return res

     _columns = {
         'budget_id'          : fields.many2one('chricar.budget','Product', required=True),
         'location_id'        : fields.many2one('stock.location','Location', required=True),
         'name'               : fields.float   ('ha used', digits=(16,2), required=True, help="Surface of field used for this product"),
         'surface_location'   : fields.function(_surface_location, method=True, string='ha total' ,digits=(16,2), help="Total surface of field", readonly=True),
         'product_id'         : fields.many2one('product.product','Seed', select=True ),
         'harvest'            : fields.function(_harvest, method=True, string='Harvest' ,digits=(16,0), help="Harvested qty this year on this location", readonly=True),
         'harvest_yield'      : fields.function(_harvest_yield, method=True, string='Yield' ,digits=(16,0), help="Harvested yield qty this year on this location", readonly=True),
         'prodlot_id'         : fields.many2one('stock.production.lot', 'Production Lot', readonly=True),
}

     def on_change_location(self, cr, uid, ids,location_id,surface,surface_location):
        result ={}
        loc = self.pool.get('stock.location').browse(cr, uid, [int(location_id)])[0]
        surface_location = loc.capacity
        result['surface_location'] = surface_location
        if not surface or surface > surface_location :
            result['name'] = surface_location

        return {'value':result}

chricar_budget_surface()

class product_product(osv.osv):
      _inherit = "product.product"
      _columns = {
          'budget_ids': fields.one2many('chricar.budget','product_id','Budget Products'),
      }

      def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'budget_ids': []})
        return super(product_product, self).copy(cr, uid, id, default, context)


product_product()

#class res_partner(osv.osv):
#      _inherit = "res.partner"
#      _columns = {
#          'budget_ids': fields.one2many('chricar.budget','partner_id','Budget Products'),
#      }
#
#res_partner()

class c2c_budget_version(osv.osv):
      _inherit = "c2c_budget.version"
      _columns = {
          'budget_ids': fields.one2many('chricar.budget','budget_version_id','Budget Products'),
          'budget_production_id': fields.many2one('chricar.budget.production','Budget Produktion'),
      }
c2c_budget_version()
