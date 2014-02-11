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
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import openerp.addons.one2many_sorted as one2many_sorted
from openerp.tools.translate import _

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
            #res[line.id] = 0
        return res

     def _product_qty_stock(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            #res[line.id] = line.product_id.qty_available
            res[line.id] = line.prod_lot_id.qty_available
        return res

     def _amount_line(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.surface * line.yield_qty) * line.price  / line.price_unit_id.coefficient
        return res

        
     def _amount_qty_stock(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = max( ((line.product_qty_stock * (line.price_expected or line.price) / line.price_unit_id.coefficient) ), 0)
        return res

     def _get_locations(self, cr, uid, context):
        warehouse_obj = self.pool.get('stock.warehouse')
        location_obj = self.pool.get('stock.location')

        location_ids = [] # internal warehouse locations
        wids = warehouse_obj.search(cr, uid, [], context=context)
        for w in warehouse_obj.browse(cr, uid, wids, context=context):
            location_ids.append(w.lot_stock_id.id)

        child_location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', location_ids)])
        location_ids = child_location_ids or location_ids
        #_logger.debug('FGF loaction_ids %s' % (location_ids))
        return location_ids

     def _amount_qty_lot(self, cr, uid, ids, name, args, context=None):
        _logger = logging.getLogger(__name__) 
        res = {}

        location_ids = self._get_locations(cr, uid, context)

        move_obj = self.pool.get('stock.move')
        move_obj = self.pool.get('chricar.report.location.moves')
        for line in self.browse(cr, uid, ids, context=context):
            # uninvoiced pickings 
            amount = 0
            if line.prod_lot_id:
                 move_ids = move_obj.search(cr, uid, [('prodlot_id','=',line.prod_lot_id.id),('state','!=','cancel')])
                 _logger.debug('FGF uninvoiced move_ids %s' % (move_ids))
                 for move in move_obj.browse(cr, uid, move_ids):
                     # FIXME - not all location_ids are at customers , missing identifier
                     if move.location_id.id not in location_ids and move.location_id.usage=='internal' and move.state == 'done':
                         amount += move.product_qty *  (line.price_expected or line.price) / line.price_unit_id.coefficient
                         _logger.debug('FGF loaction %s %s' % (move.product_id.name,move.location_id.name))
   
            res[line.id] = amount                   

        return res


     def _qty_stock_prod_lot(self, cr, uid, ids, name, args, context=None):
         """
         Compute quantity on stock of this lot
         """        
         _logger = logging.getLogger(__name__) 

         location_ids = self._get_locations(cr, uid, context)
         res = {} 
         for line in self.browse(cr, uid, ids, context=context): 
             qty = 0
             if line.prod_lot_id:
                sql = """select -sum(product_qty) 
                            from stock_move
                        where prodlot_id = %s
                            and location_id in  %s""" % ( line.prod_lot_id.id, tuple(location_ids)) 
                _logger.debug('FGF lot qty %s' % (sql))
                cr.execute(sql)
                q = cr.fetchone()
                if q[0]:
                    qty += q[0]

                sql = """select sum(product_qty) 
                            from stock_move
                        where prodlot_id = %s
                            and location_dest_id in  %s""" % ( line.prod_lot_id.id, tuple(location_ids)) 
                cr.execute(sql)
                q = cr.fetchone()
                if q[0]:
                    qty += q[0]
            
             res[line.id] = qty 

         return res


     def _amount_prod_lot(self, cr, uid, ids, name, args, context=None):
         aml = self.pool.get('account.invoice')
         ail = self.pool.get('account.invoice.line')
         move_obj = self.pool.get('stock.move')
         pick_obj = self.pool.get('stock.picking')
         res = {}
         _logger = logging.getLogger(__name__) 
         for line in self.browse(cr, uid, ids, context=context):
           invoice_line_ids = []
           amount = 0
           if line.prod_lot_id:
             #move_ids = move_obj.search(cr, uid, [('prodlot_id','=',line.prod_lot_id.id),('picking_id','>','0')])
             move_ids = move_obj.search(cr, uid, [('prodlot_id','=',line.prod_lot_id.id)])
             #_logger.debug('FGF move_ids %s' % (move_ids))
             for move in move_obj.browse(cr, uid, move_ids):
                 if  move.picking_id :
                   _logger.debug('FGF move pick id %s %s %s' % (move.picking_id.name , move.picking_id.type, move.picking_id.state))
                   if  move.picking_id.invoice_ids :
                    for inv in move.picking_id.invoice_ids:
                      _logger.debug('FGF move pick inv %s %s %s' % (inv.number, inv.type, inv.state))
                      if inv.state in ['open','paid'] and inv.invoice_line:
                        for inv_line in inv.invoice_line:
                          if inv_line.product_id == line.product_id: # FIXME problematic if 2 lots are in one invoice 
                            if inv_line.id not in invoice_line_ids:
                               invoice_line_ids.append(inv_line.id)
           for l in ail.browse(cr, uid, invoice_line_ids):    
                if l.invoice_id.type == 'out_invoice':
                     amount += l.price_subtotal
                else:
                     amount -= l.price_subtotal
           #_logger.debug('FGF move pick inv %s line %s  amount %s cum amount %s' % (inv.number, inv_line.name, inv_line.price_subtotal,amount))
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
            prod_lot_id   = line.prod_lot_id.id
            prod_lot_string = ' and 1=1 '
            if prod_lot_id:
		prod_lot_string = ' and s.prodlot_id = %s ' % prod_lot_id
		
            cr.execute("""select coalesce(sum(product_qty),0) from stock_move s,
                                                       stock_location l,
                                                       stock_location d
                                 where state='done'
                                   %s
                                   and l.usage = 'production'
                                   and l.id = s.location_id
                                   and d.usage != 'production'
                                   and d.id = s.location_dest_id
                                   and product_id = %d
                                   and to_char(date,'YYYY-MM-DD') between '%s' and '%s'""" % (prod_lot_string,product,fy_date_start,fy_date_stop))
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
            if surface_used and surface_used != 0.0  and  harvest and harvest != 0.0:
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
            if surface_used and surface_used != 0.0  and  harvest and harvest != 0.0:
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
            if yield_qty != 0.0  and harvest_net != 0.0:
                 harvest_yield_diff =  ((harvest_net / yield_qty) - 1.0) * 100
            res[line.id]  = harvest_yield_diff
        return res

     def _harvest_done(self, cr, uid, ids, name, args, context=None):
        res = {}
        mrp_production_obj = self.pool.get('mrp.production')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = ''
            mrp_ids=mrp_production_obj.search(cr, uid, [('prodlot_id','=',line.prod_lot_id.id)])
            for mrp in mrp_production_obj.browse(cr, uid, mrp_ids):
                res[line.id] = ' ('+_(mrp.state)+')'
        return res
         
     def _surface_unused(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            surface_remaining = line.surface
            for loc in line.location_ids:
                surface_remaining -= loc.name
            res[line.id]  = surface_remaining

        return res



     _columns = {
       'amount'             : fields.function(_amount_line, method=True, string='Total Sales Planned' ,digits_compute=dp.get_precision('Budget'),
                                    help="Planned Production Quantity * Price"),
       #'budget_version_id'  : fields.integer ('Budget version', required=True),
       'budget_version_id'  : fields.many2one('c2c_budget.version','Budget Version', required=True),
       'location_ids'       : fields.one2many('chricar.budget.surface','budget_id','Location Surface used'),
       'name'               : fields.text    ('Notes'),
       #'partner_id'         : fields.many2one('res.partner','Partner'),
       'price'              : fields.float   ('Price planned', digits=(16,2),help="Planned average price"),
       'price_expected'     : fields.float   ('Price expected', digits=(16,2),help="Expected average price if different from planned price"),
       'price_unit_id'      : fields.many2one('c2c_product.price_unit','Price Unit', required=True),
       'product_id'         : fields.many2one('product.product','Product', select=True, required=True),
       'product_uom'        : fields.many2one('product.uom', 'Product UOM', required=True),
       'product_qty'        : fields.function(_product_qty_line, method=True, string='Planned Quantity' ,digits=(16,0),
                             help="Surface * Yield"),
       'surface'            : fields.float   ('Surface (ha)', digits=(16,2)),
       'surface_unused'     : fields.function(_surface_unused, method=True, string='Surface unused', digits=(16,2), help="Surface not yet assigned"),
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
       'harvest_done'       : fields.function(_harvest_done, method=True, string='Harvest Done' ,type='char', help="Harvested production order state", readonly=True),
       'prod_lot_id'        : fields.many2one('stock.production.lot', 'Production Lot', domain="[('product_id','=',product_id)]"),
       'amount_prod_lot'    : fields.function(_amount_prod_lot, method=True, string='Sales Prod Lot' ,digits_compute=dp.get_precision('Budget'),help="Invoiced production lots"),
       'product_qty_stock'  : fields.function(_qty_stock_prod_lot, method=True, string='Unsold Stock Lot' ,digits_compute=dp.get_precision('Budget'),help="Uninvoiced quantity on stock of this lot"),
       'product_qty_stock_tot'  : fields.related ('product_id', 'qty_available', type="float",  string="Unsold Stock", readonly = True ,help="Uninvoiced quantitiy of this product"),
       'product_qty_lot'    : fields.related ('prod_lot_id','stock_available', type="float",  string="Uninvoiced Lot", readonly = True ,help="Uninvoiced quantitiy of this production lot"),
       'amount_qty_stock'   : fields.function(_amount_qty_stock, method=True, string='Unsold Stock Value' ,digits_compute=dp.get_precision('Budget'),help="Stock Qty * Planned Sale Price"),
       'amount_qty_lot'     : fields.function(_amount_qty_lot, method=True, string='Uninvoiced Lot Value' ,digits_compute=dp.get_precision('Budget'),help="Uninvoiced Lot Qty * Planned Sale Price"),
       'damage_yield'       : fields.float   ('Damage Yield', digits=(16,0),help="The yield reduction assessed by the insurance")       ,
       'damage_rembourse'   : fields.float   ('Damage Rembours', digits=(16,0),help="The remboursement per ha assessed by the insurance")       ,

}
     _defaults = {
       'budget_version_id' : lambda *a: 1,
}
     _order = "name"

     _sql_constraints = [
        ('surface_0', 'CHECK (surface>0)',  'Surface must be greater than 0 !')
        , ('budget_lot_unique_index', 'unique (prod_lot_id)' ,  'Lot must be unique!')
        ]

     def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'location_ids': []})
        budget = self.browse(cr, uid, id, context=context)
        default['name'] = (budget['name'] or '') + '(copy)'
        return super(chricar_budget, self).copy(cr, uid, id, default, context)

     def product_id_change(self, cr, uid, ids, product_id):
         res = {}
         for product in self.pool.get('product.product').browse(cr, uid, [product_id]):
            res = {'product_uom' : product.uom_id.id,
                   'price_unit_id' : product.price_unit_id.id,
                   }

         return {'value': res}



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
            prod_lot_id   = line.budget_id.prod_lot_id.id
            prod_lot_string = ' and 1=1 '
            if prod_lot_id:
		prod_lot_string = ' and s.prodlot_id = %s ' % prod_lot_id

            self._logger.debug('harvest detail `%s` `%s` `%s` `%s`', product, location, fy_date_start, fy_date_stop)
            cr.execute("""select coalesce(sum(product_qty),0)  from stock_move s,
                                                       stock_location l
                                 where state='done'
                                   %s 
                                   and l.usage = 'production'
                                   and l.id = s.location_id
                                   and s.product_id = %d
                                   and s.location_id = %d
                                   and to_char(date_expected,'YYYY-MM-DD') between '%s' and '%s'""" % (prod_lot_string,product,location,fy_date_start,fy_date_stop))
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
            if surface_used_detail and surface_used_detail != 0.0 and harvest_detail and harvest_detail != 0.0:
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
          'budget_ids': one2many_sorted.one2many_sorted('chricar.budget','budget_version_id','Budget Products', order='product_id.name'),
          'budget_production_id': fields.many2one('chricar.budget.production','Budget Produktion'),
      }
c2c_budget_version()
