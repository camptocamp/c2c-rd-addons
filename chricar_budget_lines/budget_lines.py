# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-08-21 15:12:07+02
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
from datetime import *
from openerp.osv import fields,osv
from dateutil.relativedelta import *
import openerp.addons.decimal_precision as dp
import logging


# ************************
# c2c_budget-item
# ************************
class c2c_budget_item(osv.osv):
     _inherit = 'c2c_budget.item'
     _columns = {
       'is_cash' :fields.boolean('Is Cash Flow', help="Check this if this budget item is cash flow relevant (not for P&L only like depreciation"),
       'is_p_l'  :fields.boolean('Is P&L', help="""Check this if this budget item is P&L relevant (not for CF only like Investments)"""),
}
     _defaults = {
      'is_cash'     : lambda *a: True,
      'is_p_l'      : lambda *a: True,
}
c2c_budget_item()

# ************************
# c2c_budget-version
# ************************
class c2c_budget_version(osv.osv):
     _inherit = 'c2c_budget.version'
     _columns = {
       'budget_version_next_id' : fields.many2one ('c2c_budget.version','Budget Version of Next Year', help="This version will be used if production or sales date planning concern already the next year"),
       'budget_version_prev_id' : fields.many2one ('c2c_budget.version','Budget Version of Provious Year', help="This version will be used if production or sales date planning still concern the previous year"),
       'is_current'             : fields.boolean  ('Is Current Budget'),
}

c2c_budget_version()

# ************************
# c2c_budget-line
# ************************
class c2c_budget_line(osv.osv):
     _inherit = 'c2c_budget.line'

     def on_change_date(self, cr, uid, ids, date_planning):
        period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',date_planning),('date_stop','>=',date_planning )])
        result ={}
        if len(period_ids):
           period_id=period_ids[0]
           result['period_id'] = period_id
        result['date_due'] = date_planning
        return {'value':result}

     def _amount_cash(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            a = 0.0
            if line.budget_item_id.is_cash:
               a = line.amount
            res[line.id] = a
        return res
        
     def _amount_cash_cum (self,cr, uid, ids, name, arg, context=None):
        result = {}
        for plan in self.browse (cr, uid, ids) :
            date_due = plan.date_planning
            if plan.date_due:
                date_due = plan.date_due
            if not date_due:
                date_due = plan.period_id.date_stop
            cr.execute("""select sum(l.amount) 
                            from c2c_budget_line l,
                                 c2c_budget_item i,
                                 account_period p
                            where i.is_cash = True
                              and i.id = l.budget_item_id
                              and p.id = l.period_id
                              and coalesce(l.date_due,l.date_planning,p.date_stop) <= to_date( '%s','YYYY-MM-DD')
                              and coalesce(l.date_due,l.date_planning,p.date_stop) >= current_date
                              and l.budget_version_id = %s;
             """ % (date_due,plan.budget_version_id.id))
            res = cr.fetchone()
            amount_cum = (res and res[0]) or False
            result[plan.id] = amount_cum
        return result
    #end def _amount_cash_cum

     def _amount_p_l(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            a = 0.0   
            if line.budget_item_id.is_p_l:
               a = line.amount
            res[line.id] = a
        return res

     def _is_current(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = False
            if line.budget_version_id.is_current and line.budget_item_id.is_cash:
                res[line.id] = True 
        return res
        
     def _is_current_version(self, cr, uid, ids, context=None):
        res = {}
        f = self.pool.get('c2c_budget.line').search(cr, uid,[('budget_version_id','in',ids)])
        for line in self.pool.get('c2c_budget.line').browse(cr,uid,f,context={}):
            res[line.id] = False
            if line.budget_version_id.is_current and line.budget_item_id.is_cash:
                res[line.id] = True
        return res

     def _is_cash(self, cr, uid, ids, context=None):
        res = {}
        f = self.pool.get('c2c_budget.line').search(cr, uid,[('budget_item_id','in',ids)])
        for line in self.pool.get('c2c_budget.line').browse(cr,uid,f,context={}):
            res[line.id] = False
            if line.budget_version_id.is_current and line.budget_item_id.is_cash:
                res[line.id] = True
        return res
        
     _columns = {
       'amount_cash'        : fields.function (_amount_cash, method=True, string='Cash' , digits_compute=dp.get_precision('Budget')),
       'amount_cash_cum'    : fields.function (_amount_cash_cum, method=True, string='Cash Cum' , digits_compute=dp.get_precision('Budget')),
       'amount_p_l'         : fields.function (_amount_p_l, method=True, string='P&L'  , digits_compute=dp.get_precision('Budget')),
       'date_due'           : fields.date     ('Date Due', help="This date will be used for cashflow planning"),
       'date_planning'      : fields.date     ('Date Planning'),
       'is_current'         : fields.function (_is_current, method=True, type="boolean", string="Is Current",
                                store = {
                                  'c2c_budget.version': (_is_current_version,['is_current'], 10),
                                  'c2c_budget.item': (_is_cash,['is_cash'], 10)}
                                              ),
                                    
       'state'              : fields.selection([('draft','Draft'), ('planned','Planned'), ('product','Product'), ('done','Done'),('cancel','Canceled')], 'Status',
help="""Draft is exceptionally used to represent lines having not reached planned state.
Planned is used to be included in budget sums.
Product is used internally by product budget.
Done is set automatically or manualy if the line materialized."""),

}
     _defaults = {
      'state'     : lambda *a: 'planned',
}
c2c_budget_line()

# ************************
# Production
# ************************
class chricar_budget_lines_production(osv.osv):
     _name = "chricar.budget_lines_production"
     _table = "chricar_budget_lines_production"
     _inherits = {'c2c_budget.line': 'budget_line_id'}


     def _get_price_unit_id(self, cr, uid, *args):
        cr.execute('select id from c2c_product_price_unit where coefficient = 1')
        res = cr.fetchone()
        return res and res[0] or False

     def _amount_production(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
          q = line.quantity
          if line.budget_id:
            if line.quantity_base == 'surface':
               q = line.budget_id.surface
            if line.quantity_base == 'product_qty':
               q = line.budget_id.product_qty
            res[line.id] = (q * line.price_unit  / line.price_unit_id.coefficient)
        return res

     def _amount_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount_bom = 0.0
            if line.amount_bom:
                amount_bom = line.amount_bom * line.price_factor
            q = line.quantity
            if line.quantity_base == 'surface':
               q = line.budget_id.surface
            if line.quantity_base == 'product_qty':
               q = line.budget_id.product_qty
            res[line.id] = (q * line.price_unit / line.price_unit_id.coefficient)  + amount_bom
        return res

     _columns = {

       'amount_bom'         : fields.float   ('Amount BoM',  digits_compute=dp.get_precision('Budget')),
       'amount_production'  : fields.function(_amount_production, method=True, string='Costs' , digits_compute=dp.get_precision('Budget')),
       'amount_cost'        : fields.function(_amount_total, method=True, string='Subtotal' , digits_compute=dp.get_precision('Budget'), store=True),
       'bom_id'             : fields.many2one('mrp.bom','BoM'),
       'budget_id'          : fields.many2one('chricar.budget','Product', required=True),
       #'budget_item_id'     : fields.many2one('c2c_budget.item','Budget Item', required=True),
       #'budget_line_id'     : fields.many2one('c2c_budget.line','Budget Line', required=True),
       #'date_due'           : fields.date    ('Date Due', required=True, help="This date will be used for cashflow planning"),
       #'date_planning'      : fields.date    ('Date Planning', required=True),
       'location_id'        : fields.many2one('stock.location','Location'),
       #'name'               : fields.char    ('Description',size=200),

       'notes'              : fields.text    ('Notes'),
       'partner_id'         : fields.many2one('res.partner','Partner'),
       'payment_term_id'    : fields.many2one('account.payment.term','Payment Term'),
       'price_factor'       : fields.float   ('Price Factor', required=True, help="Allows adjustment of calculated BoM costs ", digits=(16,2)),
       'price_unit'         : fields.float   ('Price', help="Allows adjustmen of calculated Bom costs ", digits=(16,2)),
       'price_unit_id'      : fields.many2one('c2c_product.price_unit','Price Unit', required=True),
       'quantity'           : fields.float   ('Quantity', digits=(16,2),help="select 'Individual' to update the quantity manually "),
       'quantity_base'      : fields.selection([('surface','Surface'), ('product_qty','Product Quantity'),('individual','Individual')],'Base Quantity', size=16, required=True, help="Select surface or product quantity or individual" ),
       'product_id'         : fields.many2one('product.product','Material-Service',help="Product or service used for production, see also BoM"),

}
     _defaults = {
       'price_factor'      : lambda *a: 1,
       'quantity_base'     : lambda *a: 'surface',
       'price_unit_id'     : _get_price_unit_id,
       'state'             : lambda *a: 'product',
}
     #_order = "date_planning"

     def on_change_date(self, cr, uid, ids, budget_version_id, date_planning,  payment_term_id=False,  ):
        period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',date_planning),('date_stop','>=',date_planning )])
        result ={}
        if len(period_ids):
           period_id=period_ids[0]
           result['period_id'] = period_id
        cr.execute("""select v.id
                        from c2c_budget b,
                             c2c_budget_version v,
                             c2c_budget_version vc
                       where to_date( '%s','YYYY-MM-DD') between b.start_date and b.end_date
                         and b.id = v.budget_id
                         and v.id in (vc.id,vc.budget_version_prev_id,vc.budget_version_next_id)
                         and vc.id= %d ;""" % (date_planning,budget_version_id))
        res = cr.fetchone()
        budget_version_id = (res and res[0]) or False
        if not budget_version_id and date_planning:
#             {
#              'result': {'date_planning': False},
#              'warning' : 'message'
#              }

           budget_version_id = False
           date_planning = False
           result['date_planning'] = date_planning
           raise osv.except_osv(_('Error !'),
                                _('There is no budget version defined for this date'))
        result['budget_version_id'] = budget_version_id
        result['date_due'] = date_planning
        return {'value':result}

     def on_change_quantity_base(self, cr, uid, ids, qty_base=False,surface=False,product_qty=False, price_unit=False, price_unit_id=False, price_factor=False, amount_bom=False):
       #for bud_prod in self.browse(cr, uid, ids ):
        coeff = 1.0
        if price_unit_id:
            pu = self.pool.get('c2c_product.price_unit').browse(cr, uid, [int(price_unit_id)])[0]
            coeff = pu.coefficient
        result ={}
        q = 0.0
        if qty_base == 'surface':
            q = surface
        if qty_base == 'product_qty':
            q = product_qty
        result['quantity'] = q
        result['amount_production'] = q * price_unit / coeff
        result['amount_cost'] = q * price_unit / coeff + amount_bom * price_factor
        result['amount'] = -(q * price_unit / coeff + amount_bom * price_factor)
        return {'value':result}

     def on_change_quantity(self, cr, uid, ids,qty=False,price_unit=False,price_unit_id=False, price_factor=False,amount_bom=False):
        result ={}
        coeff = 1.0
        if price_unit_id:
            pu = self.pool.get('c2c_product.price_unit').browse(cr, uid, [price_unit_id])[0]
            coeff = pu.coefficient
        result['amount_production'] = qty * price_unit / coeff
        result['amount_cost'] = qty * price_unit / coeff + amount_bom * price_factor
        result['amount'] = -(qty * price_unit / coeff + amount_bom * price_factor)
        return {'value':result}

     def on_change_bom(self, cr, uid, ids,amount=False,price_factor=False, amount_bom=False):
        result ={}
        result['amount_cost'] = amount + amount_bom * price_factor
        result['amount'] = -(amount + amount_bom * price_factor)
        return {'value':result}

chricar_budget_lines_production()

# ************************
# Sales
# ************************
class chricar_budget_lines_sales(osv.osv):
     _name = "chricar.budget_lines_sales"
     _table = "chricar_budget_lines_sales"
     _inherits = {'c2c_budget.line': 'budget_line_id'}

     def _get_price_unit_id(self, cr, uid, *args):
        cr.execute('select id from c2c_product_price_unit where coefficient = 1')
        res = cr.fetchone()
        return res and res[0] or False


     def _amount_sales(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
             res[line.id] = (line.quantity * line.price_unit / line.price_unit_id.coefficient)
        return res

     def _amount_total(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount_bom = 0.0
            if line.amount_bom:
                amount_bom = line.amount_bom
            res[line.id] = (line.quantity * line.price_unit / line.price_unit_id.coefficient)  + amount_bom
        return res

     _columns = {
       'amount_bom'         : fields.float   ('Amount BoM',  digits_compute=dp.get_precision('Budget')),
       'amount_sales'             : fields.function(_amount_sales, method=True, string='Sales' , digits_compute=dp.get_precision('Budget')),
       #'amount'       : fields.function(_amount_total, method=True, string='Subtotal' , digits_compute=dp.get_precision('Budget') , store=True),
       'bom_id'             : fields.many2one('mrp.bom','BoM'),
       'budget_id'          : fields.many2one('chricar.budget','Budget', required=True),
       #'budget_line_id'     : fields.many2one('c2c_budget.line','Budget Line', required=True),
       #'budget_item_id'     : fields.many2one('c2c_budget.item','Budget Item',required=True),
       #'date_due'           : fields.date    ('Date Due', required=True, help="This date will be used for cashflow planning"),
       #'date_planning'      : fields.date    ('Date Planning', required=True),
       #'name'               : fields.char    ('Description',size=200),
       'notes'              : fields.text    ('Notes'),
       'partner_id'         : fields.many2one('res.partner','Partner', required=True),
       'payment_term_id'    : fields.many2one('account.payment.term','Payment Term'),
       'price_unit'         : fields.float   ('Price', help="Allows adjustmen of calculated Bom costs ", digits=(16,2)),
       'price_unit_id'      : fields.many2one('c2c_product.price_unit','Price Unit', required=True),

       'quantity'           : fields.float   ('Quantity', digits=(16,2)),
       'auto_generated'     : fields.boolean ('Auto generated',help="Sales automatically generated from production plan"),
       'auto_type'          : fields.char    ('Autogenerated Sales or Cost',size=8),
}
     _defaults = {
       'price_unit_id'     : _get_price_unit_id,
       'state'             : lambda *a: 'product',
}
     #_order = "name"

     def on_change_date(self, cr, uid, ids, budget_version_id,product_id, price_unit_id, date_planning,  payment_term_id=False,  ):
        period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',date_planning),('date_stop','>=',date_planning )])
        result ={}
        if len(period_ids):
           period_id=period_ids[0]
           result['period_id'] = period_id
        cr.execute("""select v.id
                        from c2c_budget b,
                             c2c_budget_version v,
                             c2c_budget_version vc
                       where to_date( '%s','YYYY-MM-DD') between b.start_date and b.end_date
                         and b.id = v.budget_id
                         and v.id in (vc.id,vc.budget_version_prev_id,vc.budget_version_next_id)
                         and vc.id= %d ;""" % (date_planning,budget_version_id))
        res = cr.fetchone()
        budget_version_id = (res and res[0]) or False
        if not budget_version_id and date_planning:
            raise osv.except_osv(_('Error !'),
                                _('There is no budget version defined for this date'))
        result['budget_version_id'] = budget_version_id
        result['date_due'] = date_planning
        result['price_unit_id'] = price_unit_id

        product_obj = self.pool.get('product.product').browse(cr, uid, [product_id])[0]
        product = product_obj.name
        if product_obj.variants:
            product = product +' - '+ product_obj.variants
        result['name'] = product
        return {'value':result}

     def on_change_quantity(self, cr, uid, ids,qty=False,price_unit=False,price_unit_id=False, amount_bom=False):
        result ={}
        coeff = 1.0
        if price_unit_id:
            pu = self.pool.get('c2c_product.price_unit').browse(cr, uid, [price_unit_id])[0]
            coeff = pu.coefficient
        result['amount_sales'] = qty * price_unit / coeff
        result['amount'] = qty * price_unit / coeff + amount_bom
        return {'value':result}

     def on_change_bom(self, cr, uid, ids,amount=False, amount_bom=False):
        result ={}
        result['amount'] = amount + amount_bom
        return {'value':result}

chricar_budget_lines_sales()


class chricar_budget(osv.osv):
      _inherit = "chricar.budget"
      _logger = logging.getLogger(__name__)

      def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'budget_lines_production_ids': [],'budget_lines_sales_ids': [],})
        return super(chricar_budget, self).copy(cr, uid, id, default, context)


      def _amount_costs(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         costs = 0.0
         for p in self.browse(cr, uid, ids, context):
             pid = p.id
             cr.execute("""select sum(amount_cost) from chricar_budget_lines_production p,
                                                   c2c_budget_line l
                                                   where l.id = p.budget_line_id
                                                     and p.budget_id = %d""" % pid)
             res = cr.fetchone()
             costs = (res and res[0]) or False
             result[p.id] = costs
         return result

      def _amount_sales(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         sales = 0.0
         for p in self.browse(cr, uid, ids, context):
             pid = p.id
             cr.execute("""select sum(amount) from chricar_budget_lines_sales s,
                                                   c2c_budget_line l
                                                   where l.id = s.budget_line_id
                                                     and (auto_type is null or auto_type = 'sales')
                                                     and s.budget_id = %d""" % pid)
             res = cr.fetchone()
             sales = (res and res[0]) or False
             result[p.id] = sales
         return result

      def _amount_sales_open(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         sales = 0.0
         for p in self.browse(cr, uid, ids, context):
             pid = p.id
             cr.execute("""select sum(amount) from chricar_budget_lines_sales s,
                                                   c2c_budget_line l
                                                   where l.id = s.budget_line_id
                                                     and (auto_type is null or auto_type = 'sales')
                                                     and s.budget_id = %d""" % pid)
             res = cr.fetchone()
             sales = (res and res[0]) or False
             result[p.id] = round(p.amount - sales,0)
         return result

      def _qty_sales_open(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         sales_qty = 0.0
         for p in self.browse(cr, uid, ids, context):
             pid = p.id
             cr.execute("""select sum(quantity) from chricar_budget_lines_sales s,
                                                   c2c_budget_line l
                                                   where l.id = s.budget_line_id
                                                     and (auto_type is null or auto_type = 'sales')
                                                     and s.budget_id = %d""" % pid)
             res = cr.fetchone()
             qty_sales = (res and res[0]) or False
             result[p.id] = round(p.product_qty - qty_sales,0)
         return result

      def _amount_contribution(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         sales = 0.0
         for p in self.browse(cr, uid, ids, context):
             pid = p.id
             cr.execute("""select sum(amount) from chricar_budget_lines_sales s,
                                                   c2c_budget_line l
                                                   where l.id = s.budget_line_id
                                                     and (auto_type is null or auto_type = 'sales')
                                                     and s.budget_id = %d""" % pid)
             res = cr.fetchone()
             sales = (res and res[0]) or False
             cr.execute("""select sum(amount_cost) from chricar_budget_lines_production p,
                                                   c2c_budget_line l
                                                   where l.id = p.budget_line_id
                                                     and p.budget_id = %d""" % pid)
             res = cr.fetchone()
             costs = (res and res[0]) or False
             result[p.id] = round(sales - costs,0)
         return result

      def _amount_contribution_total(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         sales = 0.0
         for p in self.browse(cr, uid, ids, context):
             pid = p.id
             sales = p.amount
             cr.execute("""select sum(amount_cost) from chricar_budget_lines_production p,
                                                   c2c_budget_line l
                                                   where l.id = p.budget_line_id
                                                     and p.budget_id = %d""" % pid)
             res = cr.fetchone()
             costs = (res and res[0]) or False
             result[p.id] = round(sales - costs,0)
         return result


      _columns = {
          'amount_costs'               : fields.function(_amount_costs, method=True, string='Total Cost' , digits_compute=dp.get_precision('Budget'),
                                         help="Sum of cost from detail below"),
          'amount_sales'               : fields.function(_amount_sales, method=True, string='Sales Detail' , digits_compute=dp.get_precision('Budget'),
                                         help="Sum of sales form details below"),
          'amount_sales_open'          : fields.function(_amount_sales_open, method=True, string='Sales to be Planned' , digits_compute=dp.get_precision('Budget'),
                                         help="Differnce between Sales Planned and Sales Detail Planned"),
          'qty_sales_open'             : fields.function(_qty_sales_open, method=True, string='Quantity to be Planned' , digits_compute=dp.get_precision('Budget'),
                                         help="Production quantity not planned for sale"),
          'amount_contribution'        : fields.function(_amount_contribution, method=True, string='Contribution' , digits_compute=dp.get_precision('Budget'),
                                         help="Planned Detail Sales - Total Planned Costs"),
          'amount_contribution_total'  : fields.function(_amount_contribution_total, method=True, string='Total Contribution Planned' , digits_compute=dp.get_precision('Budget'),
                                         help="Total Planned Sales - Total Planned Costs"),
          'budget_lines_production_ids': fields.one2many('chricar.budget_lines_production','budget_id','Budget Products Production'),
          'budget_lines_sales_ids'     : fields.one2many('chricar.budget_lines_sales','budget_id','Budget Products Sales'),
                 }

      #FIXME

      
      def button_delete_auto_generate_sale_lines(self, cr, uid, ids, context=None):
       self._logger.debug('delete autogenerate `%s`', context)
       for prod_plan in self.browse(cr, uid, ids, context):
        period_obj  = self.pool.get('account.period')
        bls_obj = self.pool.get('chricar.budget_lines_sales')

        # delete exising auto generated for this budget and product
        line_ids = bls_obj.search(cr, uid, [('auto_generated','=',1),
                                            ('budget_id','=',prod_plan.id),
                                         ], context=context)
        self._logger.debug('lines to delete `%s`', line_ids)
        if line_ids:
          toremove = []
          for c2c_lines in bls_obj.browse(cr, uid, line_ids):
              toremove.append(c2c_lines.budget_line_id.id)
          bls_obj.unlink(cr, uid, line_ids )
          self._logger.debug('lines deleted `%s`', line_ids)
          if toremove:
             self._logger.debug('lines c2c to deleted `%s`', toremove)
             self.pool.get('c2c_budget.line').unlink(cr, uid, toremove )
             self._logger.debug('lines c2c deleted `%s`', toremove)
       return True  

        # create new lines for not individually planned sales
      def button_auto_generate_sale_lines(self, cr, uid, ids, context=None):
        # Call delete function instead of copy
       self._logger.debug('autogenerate `%s`', context)
       for prod_plan in self.browse(cr, uid, ids, context):
        period_obj  = self.pool.get('account.period')
        bls_obj = self.pool.get('chricar.budget_lines_sales')

        # delete exising auto generated for this budget and product
        line_ids = bls_obj.search(cr, uid, [('auto_generated','=',1),
                                            ('budget_id','=',prod_plan.id),
                                         ], context=context)
        self._logger.debug('lines to delete `%s`', line_ids)
        if line_ids:
          toremove = []
          for c2c_lines in bls_obj.browse(cr, uid, line_ids):
              toremove.append(c2c_lines.budget_line_id.id)
          bls_obj.unlink(cr, uid, line_ids )
          self._logger.debug('lines deleted `%s`', line_ids)
          self._logger.debug('lines c2c to deleted `%s`', toremove)
          self.pool.get('c2c_budget.line').unlink(cr, uid, toremove )
          self._logger.debug('lines c2c deleted `%s`', toremove)

        amount_sales_open = prod_plan.amount_sales_open
        #if round(amount_sales_open,0) == 0.0:
        #    continue
        sale_from = prod_plan.sale_from
        sale_to = prod_plan.sale_to
        fys = self.pool.get('account.fiscalyear').search(cr, uid,[('date_start','<=',sale_from),('date_stop','>=',sale_from)])
        for fy in self.pool.get('account.fiscalyear').browse(cr, uid, fys):
            fy_date_stop = fy.date_stop
        if not sale_to:
            sale_to = fy_date_stop
        
        period_ids = period_obj.search(cr, uid,[('date_start','<=',sale_to),('date_stop','>=',sale_from)])
        self._logger.debug('periods `%s`', period_ids)
        # find budget item via account
        months = len(period_ids)
        account_sale_id = prod_plan.product_id.property_account_income.id or prod_plan.product_id.categ_id.property_account_income_categ.id
        account_cost_id = prod_plan.product_id.property_account_expense and prod_plan.product_id.property_account_expense_categ.id \
                          or prod_plan.product_id.categ_id.property_account_expense_categ.id
        
        self._logger.debug('account `%s` `%s`', account_sale_id, account_cost_id)
        
        budget_item_ids = []
        if account_sale_id:
            budget_item_ids = self.pool.get('c2c_budget.item').search(cr, uid,[('account', '=', account_sale_id )])
        budget_item_id = 553 # FIXME if nothing is found later
        if budget_item_ids:
            self._logger.debug('budget_item_ids `%s`', budget_item_ids)
            for bid in self.browse(cr, uid, budget_item_ids, context):
               budget_item_id = bid.id 
               
        budget_item_cost_ids = []
        if account_cost_id:
            budget_item_cost_ids = self.pool.get('c2c_budget.item').search(cr, uid,[('account', '=', account_cost_id )])
        budget_item_cost_id = 553 # FIXME if nothing is found later
        if budget_item_cost_ids:
            self._logger.debug('budget_item_cost_ids `%s`', budget_item_cost_ids)
            for bid in self.browse(cr, uid, budget_item_cost_ids, context):
               budget_item_cost_id = bid.id
               
        budget_line_id = 0 # FIXME do we need this ?
        # insert lines
        qty_sales_open = prod_plan.qty_sales_open
        if period_ids and round(qty_sales_open,-1) > 0 :
            amount_monthly = round(amount_sales_open / months,0)
            
            qty_monthly = round(qty_sales_open / months,0)
            for period in period_obj.browse(cr, uid, period_ids, context):
                 if period.date_start <= sale_to and period.date_stop >= sale_to:
                   amount_monthly = amount_sales_open
                   qty_monthly = qty_sales_open
                #if period.date_stop <= fy_date_stop:  # FIXME - should run into next budget
                 budget_version_id = prod_plan.budget_version_id.id
                 if period.date_stop > fy_date_stop:
                      budget_version_id = prod_plan.budget_version_id.budget_version_next_id.id
                 self._logger.debug('create `%s` `%s`', period.id, amount_monthly)
                 #d = period.date_stop.date("%Y %m %d") + timedelta(45)
                 self._logger.debug('date 1  `%s`', period.date_stop)
                 dd = period.date_stop
                 ya = int(dd[0:4])
                 mo = int(dd[5:7])
                 da = int(dd[8:10])
                 self._logger.debug(' `%s` `%s` `%s`', ya,mo,da)
                 d = date(ya,mo,da)  +  timedelta(45)
                 date_due = d.strftime('%Y-%m-%d')
                 self._logger.debug('date 2  `%s`', d)
                 # Sales Line
                 vals = {
                  'budget_id' : prod_plan.id,
                  'budget_version_id': budget_version_id,
                  'partner_id' : prod_plan.budget_version_id.company_id.partner_id.id,
                  'price_unit_id' : prod_plan.product_id.price_unit_id.id,
                  'period_id' : period.id,
                  'budget_item_id' : budget_item_id,
                  'amount' : amount_monthly,
                  'date_planning' : period.date_stop,
                  'date_due' : date_due,
                  'state' : 'product',
                  'auto_generated' : 1,
                  'auto_type' : 'sale',
                  'name' : 'generated '+ prod_plan.product_id.name + ' - ' + (prod_plan.product_id.variants or '') ,
                  'quantity' : qty_monthly,
                  'currency_id' : prod_plan.budget_version_id.currency_id.id,
                        }
                 self._logger.debug('vals    `%s`', vals)
                 bls_obj.create(cr, uid, vals )
                 
                 amount_sales_open -= amount_monthly
                 qty_sales_open -= qty_monthly
        # Inventory Change Line for each sale
        #line_cost_ids = bls_obj.search(cr, uid, [('auto_type','not in',['cost']),
        line_cost_ids = bls_obj.search(cr, uid, [('budget_id','=',prod_plan.id),
                                         ], context=context)
        self._logger.debug('vals cost lines `%s`', line_cost_ids)
        total_qty = prod_plan.product_qty
        if line_cost_ids:
          # value = cost of good sold
          
          total_value_cost = total_qty * prod_plan.product_id.standard_price
            
          for sale_lines in bls_obj.browse(cr, uid, line_cost_ids):
              
              self._logger.debug('sales cost lines `%s`', line_ids)
              amount_cost = -round(total_value_cost * sale_lines.quantity / total_qty,0)
              vals_cost = {
                  'budget_id' : sale_lines.budget_id.id,
                  'budget_version_id': sale_lines.budget_version_id.id,
                  'partner_id' : sale_lines.partner_id.id,
                  'price_unit_id' : prod_plan.product_id.price_unit_id.id,
                  'period_id' : sale_lines.period_id.id,
                  'budget_item_id' : budget_item_cost_id,
                  'amount' : amount_cost,
                  'date_planning' : sale_lines.period_id.date_stop,
                  'date_due' : sale_lines.period_id.date_stop,
                  'state' : 'product',
                  'auto_generated' : 1,
                  'auto_type' : 'cost',
                  'name' : 'generated cost '+ prod_plan.product_id.name + ' - ' + (prod_plan.product_id.variants or '') ,
                  'currency_id' : prod_plan.budget_version_id.currency_id.id,
                  }
              self._logger.debug('vals cost `vals_costs`', vals_cost)
              bls_obj.create(cr, uid, vals_cost )

        # Production cost inventory
        if prod_plan.product_qty and prod_plan.product_id.standard_price:
          # value = cost of production 
          total_value_cost = total_qty * prod_plan.product_id.standard_price
          vals_cost = {
                  'budget_id' : prod_plan.id,
                  'budget_version_id': prod_plan.budget_version_id.id,
                  'partner_id' : prod_plan.budget_version_id.company_id.partner_id.id,
                  'price_unit_id' : prod_plan.product_id.price_unit_id.id,
                  'period_id' : prod_plan.harvest_period_id.id,
                  'budget_item_id' : budget_item_cost_id,
                  'amount' : total_value_cost,
                  'date_planning' : prod_plan.harvest_period_id.date_stop,
                  'date_due' : prod_plan.harvest_period_id.date_stop,
                  'state' : 'product',
                  'auto_generated' : 1,
                  'auto_type' : 'cost',
                  'name' : 'generated production value '+ prod_plan.product_id.name + ' - ' + (prod_plan.product_id.variants or '') ,
                  'currency_id' : prod_plan.budget_version_id.currency_id.id,
                  }
          self._logger.debug('vals cost `%s`', vals_cost)
          bls_obj.create(cr, uid, vals_cost )
        return True

chricar_budget()

#class res_partner(osv.osv):
#      _inherit = "res.partner"
#      _columns = {
#          'budget_lines_ids': fields.one2many('chricar.budget_lines','partner_id','Budget Products Production'),
#      }
#res_partner()
#class stock_location(osv.osv):
#      _inherit = "stock.location"
#      _columns = {
#          'budget_lines_ids': fields.one2many('chricar.budget_lines','location_id','Budget Products Production'),
#      }
#stock_location()

class chricar_budget_line_share(osv.osv):
    _name = "chricar.budget.line.share"
    _description = "Chricar Budget Line Share"
    _auto = False
    _columns = {
      'period_id'          : fields.many2one('account.period', 'Period', required=True),
      'cal_year'           : fields.char    ('Calendar Year',size=8       ,readonly='True'),
      'budget_item_id'     : fields.many2one('c2c_budget.item','Budget Item',required=True),
      'budget_version_id'  : fields.many2one('c2c_budget.version','Budget Version',required=True),
      'analytic_account_id': fields.many2one('account.analytic.account','Analytic Account'),
      'partner_id'         : fields.many2one('res.partner','Partner', required=True),
      'partner_parent_id'  : fields.many2one('res.partner','Owner', required=True),
      'percentage'         : fields.float   ('Percentage', digits=(6,2)    ,readonly=True),
      'valid_from'         : fields.date    ('Valid From',readonly=True),
      'valid_until'        : fields.date    ('Valid Until',readonly=True),
      'state'              : fields.char    ('State', size=16       ,readonly=True),
      'amount_orig'        : fields.float   ('Amount Orig',  digits_compute=dp.get_precision('Budget') ,readonly=True),
      'cash_quote'         : fields.float   ('Cash Quote',  digits_compute=dp.get_precision('Budget') ,readonly=True),
      'cash_quote_future'  : fields.float   ('Cash Quote Future',  digits_compute=dp.get_precision('Budget') ,readonly=True),
      'pl_quote'           : fields.float   ('P&L Quote',  digits_compute=dp.get_precision('Budget') ,readonly=True),
      'date_planning'      : fields.date    ('Date Planning',readonly=True),
      'date_due'           : fields.date    ('Date Due',readonly=True),
      'name'               : fields.char    ('Text', size=256       ,readonly=True),
      'level'              : fields.integer ('Level',readonly=True),
      'consolidation'      : fields.boolean ('Consolidation L1',readonly=True,help="True for direct ownership and partnerships, results (and cash flow) affect directly owner income statement"),
      'consolidation2'     : fields.boolean ('Consolidation L2',readonly=True,help="True for direct ownership and partnerships, results (and cash flow) affect directly owner income statement"),
      'consolidation3'     : fields.boolean ('Consolidation L3',readonly=True,help="True for direct ownership and partnerships, results (and cash flow) affect directly owner income statement"),
      'consolidation_only' : fields.boolean ('Consolidation only',readonly=True,help="Select True to get only records for consolidation"),
      'partner_parent2_id' : fields.many2one('res.partner','Intermediate 1', required=True),
      'partner_parent3_id' : fields.many2one('res.partner','Intermediate 2', required=True),
    }

    _order = 'date_due asc'

    def init(self, cr):
      cr.execute("""
DROP SEQUENCE IF EXISTS chricar_budget_line_share_id_seq CASCADE;
CREATE SEQUENCE chricar_budget_line_share_id_seq;
create or replace view chricar_budget_line_share as
  select 
      nextval('chricar_budget_line_share_id_seq'::regclass)::int as id,
      l.period_id,
      to_char(l.date_planning,'YYYY') as cal_year,
      l.budget_item_id,l.budget_version_id,l.analytic_account_id,
      c.partner_id,c.partner_id as partner_parent_id,
      100 as percentage,null::date as valid_from, null::date as valid_until,
      l.state,l.amount as amount_orig,
      case when i.is_cash is true then l.amount else 0 end as cash_quote ,
      case when i.is_cash is true and l.date_planning > now() then l.amount else 0 end as cash_quote_future ,
      case when i.is_p_l is true then l.amount else 0 end as PL_quote,
      l.date_planning,date_due,l.name, 1 as level,
      True as consolidation,
      null::boolean as consolidation2 ,
      null::boolean as consolidation3,
      null::integer as partner_parent2_id, null::integer as partner_parent3_id,
      True as consolidation_only
    from c2c_budget_line l,
      c2c_budget_version v,
      c2c_budget_item i,
      res_partner p,
      res_company c
    where 
      l.state != 'canceled'
      and p.id=c.partner_id
      and v.company_id = c.id
      and v.id = l.budget_version_id
      and i.id = l.budget_item_id
  union all
  select
      nextval('chricar_budget_line_share_id_seq'::regclass)::int as id,
      l.period_id,
      to_char(l.date_planning,'YYYY') as cal_year,l.budget_item_id,l.budget_version_id,l.analytic_account_id,
      pc.partner_id,pc.partner_parent_id,
      pc.percentage,pc.valid_from,pc.valid_until,
      l.state,l.amount as amount_orig,
      percentage/100 * case when i.is_cash is true then l.amount else 0 end as cash_quote ,
      percentage/100 * case when i.is_cash is true and l.date_planning > now() then l.amount else 0 end as cash_quote_future ,
      percentage/100 * case when i.is_p_l is true then l.amount else 0 end as PL_quote,
      l.date_planning,date_due,l.name, 1 as level,
      pc.consolidation,
      null::boolean as consolidation2 ,
      null::boolean as consolidation3,
      null::integer as partner_parent2_id, null::integer as partner_parent3_id,
      case when pc.consolidation = True then True end as consolidation_only 
    from 
      res_partner_parent_company pc,
      c2c_budget_line l,
      c2c_budget_version v,
      c2c_budget_item i,
      res_partner p,
      res_company c
    where 
      l.state != 'canceled'
      and p.id=pc.partner_id
      and c.partner_id = pc.partner_id
      and v.company_id = c.id
      and v.id = l.budget_version_id
      and i.id = l.budget_item_id
      and l.date_planning between coalesce(pc.valid_from,l.date_planning) and coalesce(pc.valid_until,l.date_planning)
  union all
  select
      nextval('chricar_budget_line_share_id_seq'::regclass)::int as id,
      l.period_id,
      to_char(l.date_planning,'YYYY') as cal_year,l.budget_item_id,l.budget_version_id,l.analytic_account_id,
      pc.partner_id,pc2.partner_parent_id,
      pc.percentage*pc2.percentage/100,pc2.valid_from,pc2.valid_until,
      l.state,l.amount as amount_orig,
      pc.percentage/100 * pc2.percentage/100 * case when i.is_cash is true then l.amount else 0 end as cash_quote ,
      pc.percentage/100 * pc2.percentage/100 * case when i.is_cash is true and l.date_planning > now() then l.amount else 0 end as cash_quote_future ,
      pc.percentage/100 * pc2.percentage/100 * case when i.is_p_l is true then l.amount else 0 end as PL_quote,
      l.date_planning,date_due,l.name, 2 as level,
      pc.consolidation,pc2.consolidation,null, 
      pc.partner_parent_id,null,
      case when pc.consolidation = True and  pc2.consolidation = True then True end as consolidation_only
    from
      res_partner_parent_company pc,
      res_partner_parent_company pc2,
      c2c_budget_line l,
      c2c_budget_version v,
      c2c_budget_item i,
      res_partner p,
      res_company c
    where -- (pc2.consolidation=pc.consolidation or ( pc2.consolidation is null and pc.consolidation is null)) and
      l.state != 'canceled'
      and p.id=pc.partner_id
      and c.partner_id = pc.partner_id
      and pc.partner_parent_id = pc2.partner_id
      and v.company_id = c.id
      and v.id = l.budget_version_id
      and i.id = l.budget_item_id
      and l.date_planning between coalesce(pc.valid_from,l.date_planning) and coalesce(pc.valid_until,l.date_planning)
      and l.date_planning between coalesce(pc2.valid_from,l.date_planning) and coalesce(pc2.valid_until,l.date_planning)
  union all
  select
      nextval('chricar_budget_line_share_id_seq'::regclass)::int as id,
      l.period_id,
      to_char(l.date_planning,'YYYY') as cal_year,l.budget_item_id,l.budget_version_id,l.analytic_account_id,
      pc.partner_id,pc3.partner_parent_id,
      pc.percentage*pc2.percentage/100*pc3.percentage/100, pc3.valid_from,pc3.valid_until,
      l.state,l.amount as amount_orig,
      pc.percentage/100 * pc2.percentage/100 * pc3.percentage/100 * case when i.is_cash is true then l.amount else 0 end as cash_quote ,
      pc.percentage/100 * pc2.percentage/100 * pc3.percentage/100 * case when i.is_cash is true and l.date_planning > now() then l.amount else 0 end as cash_quote_future ,
      pc.percentage/100 * pc2.percentage/100 * pc3.percentage/100 * case when i.is_p_l is true then l.amount else 0 end as PL_quote,
      l.date_planning,date_due,l.name, 3 as level,
      pc.consolidation,pc2.consolidation,pc3.consolidation,
      pc.partner_parent_id,pc2.partner_parent_id,
      case when pc.consolidation = True and pc2.consolidation = True and pc3.consolidation = true then True end as consolidation_only
    from
      res_partner_parent_company pc,
      res_partner_parent_company pc2,
      res_partner_parent_company pc3,
      c2c_budget_line l,
      c2c_budget_version v,
      c2c_budget_item i,
      res_partner p,
      res_company c
    where --((pc2.consolidation=pc.consolidation and pc2.consolidation=pc3.consolidation) or (pc3.consolidation is null and pc2.consolidation is null and pc.consolidation is null)) and
      l.state != 'canceled'
      and p.id=pc.partner_id
      and c.partner_id = pc.partner_id
      and pc.partner_parent_id = pc2.partner_id
      and pc2.partner_parent_id = pc3.partner_id
      and v.company_id = c.id
      and v.id = l.budget_version_id
      and i.id = l.budget_item_id
      and l.date_planning between coalesce(pc.valid_from,l.date_planning) and coalesce(pc.valid_until,l.date_planning)
      and l.date_planning between coalesce(pc2.valid_from,l.date_planning) and coalesce(pc2.valid_until,l.date_planning)
      and l.date_planning between coalesce(pc3.valid_from,l.date_planning) and coalesce(pc3.valid_until,l.date_planning)
;
""")
chricar_budget_line_share()
