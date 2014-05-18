# -*: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import time
import logging


class product_product(osv.osv):
    _inherit = "product.product"
    _logger = logging.getLogger(__name__)

    # FIXME this should go into stock/product, but SQL is not accessible
    def _get_product_valuation(self, cr, uid, ids, field_name, arg, context=None):
        _logger = logging.getLogger(__name__)

        """ Finds whether product is available or not in particular warehouse.
        @return: Dictionary of values (Valuation)
        """
        if context is None:
            context = {}

        _logger.debug('FGF stock_location_product context %s',context)
        location_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')
        shop_obj = self.pool.get('sale.shop')

        states = context.get('states',[])
        if not states:
            states = ['done']
        what = context.get('what',())
        if what == ():
            what = ('in','out')
        if not ids:
            ids = self.search(cr, uid, [])
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res

        if context.get('shop', False):
            warehouse_id = shop_obj.read(cr, uid, int(context['shop']), ['warehouse_id'])['warehouse_id'][0]
            if warehouse_id:
                context['warehouse'] = warehouse_id

        if context.get('warehouse', False):
            lot_id = warehouse_obj.read(cr, uid, int(context['warehouse']), ['lot_stock_id'])['lot_stock_id'][0]
            if lot_id:
                context['location'] = lot_id

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = location_obj.search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = warehouse_obj.search(cr, uid, [], context=context)
            for w in warehouse_obj.browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids

        # this will be a dictionary of the UoM resources we need for conversion purposes, by UoM id
        uoms_o = {}
        # this will be a dictionary of the product UoM by product id
        product2uom = {}
        for product in self.browse(cr, uid, ids, context=context):
            product2uom[product.id] = product.uom_id.id
            uoms_o[product.uom_id.id] = product.uom_id

        results = []
        results2 = []

        from_date = context.get('from_date',False)
        to_date = context.get('to_date',False)
        date_str = False
        date_values = False
        where = [tuple(location_ids),tuple(location_ids),tuple(ids),tuple(states)]
        where = [tuple(location_ids),tuple(ids),tuple(states)]
        if from_date and to_date:
            date_str = "date>=%s and date<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date<=%s"
            date_values = [to_date]

        prodlot_id = context.get('prodlot_id', False)

    # TODO: perhaps merge in one query.
        if date_values:
            where.append(tuple(date_values))
        _logger.debug('FGF stock_location_product what %s',what)
        _logger.debug('FGF stock_location_product where %s',where)
        if 'in' in what:
            # all moves from a location out of the set to a location in the set
            cr.execute(
                'select sum(move_value_cost), sum(move_value_sale), product_id '\
                'from stock_move '\
                'where '\
                'location_dest_id IN %s '\
                'and product_id IN %s '\
                '' + (prodlot_id and ('and prodlot_id = ' + str(prodlot_id)) or '') + ' '\
                'and state IN %s ' + (date_str and 'and '+date_str+' ' or '') +' '\
                'group by product_id',tuple(where))
            results = cr.fetchall()
#            sql = \
#                ('select sum(move_value_cost), sum(move_value_sale), product_id '\
#                'from stock_move '\
#                'where '\
#                'location_dest_id IN %s '\
#                'and product_id IN %s '\
#                '' + (prodlot_id and ('and prodlot_id = ' + str(prodlot_id)) or '') + ' '\
#                'and state IN %s ' + (date_str and 'and '+date_str+' ' or '') +' '\
#                'group by product_id',tuple(where) )
#
#            _logger.debug('FGF sql %s', sql)
            #for i in results:
            #   _logger.debug('FGF stock_location_product in  %s',i)
        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            cr.execute(
                'select sum(move_value_cost), sum(move_value_sale), product_id '\
                'from stock_move '\
                'where location_id IN %s '\
                'and product_id  IN %s '\
                '' + (prodlot_id and ('and prodlot_id = ' + str(prodlot_id)) or '') + ' '\
                'and state in %s ' + (date_str and 'and '+date_str+' ' or '') + ' '\
                'group by product_id',tuple(where))
            results2 = cr.fetchall()
            #for i in results2:
            #   _logger.debug('FGF stock_location_product out  %s',i)

        #TOCHECK: before change uom of product, stock move line are in old uom.
        context.update({'raise-exception': False})
        # Compute the incoming vlaues
        for value_cost, value_sale, prod_id in results:
            res[prod_id] += value_cost
        # Compute the outgoing values
        for value_cost, value_sale, prod_id in results2:
            res[prod_id] -= value_cost
        return res

    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        ctx = dict(context)
        ctx['from_date'] = context.get('from_date1',False)
        ctx['to_date'] = context.get('to_date1',False)
        res=super(product_product, self)._product_available(cr, uid, ids, field_name, arg, context=ctx)
        return res


    def _get_product_valuation1(self, cr, uid, ids, field_name, arg, context=None):
        ctx1 = dict(context)
        ctx1['from_date'] = context.get('from_date1',False)
        ctx1['to_date'] = context.get('to_date1',False)
        res=self._get_product_valuation(cr, uid, ids, field_name, arg, context=ctx1)
        return res

    def _get_product_valuation2(self, cr, uid, ids, field_name, arg, context=None):
        ctx2 = dict(context)
        ctx2['from_date'] = context.get('from_date2',False)
        ctx2['to_date'] = context.get('to_date2',False)
        res=self._get_product_valuation(cr, uid, ids, field_name, arg, context=ctx2)
        return res

    def _get_valuation_diff(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = product.valuation1 - product.valuation2
        return res


    def _get_avg_price(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            if product.qty_available >0 and product.valuation1 >0 :
                res[product.id] = product.valuation1 / product.qty_available
            else:
                res[product.id] = 0
        return res

    def _get_expense_account(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] =  product.property_account_expense.id  or product.categ_id.property_account_expense_categ.id or None
        return res

    def _get_product_expense(self, cr, uid, ids, context=None):
        _logger  = logging.getLogger(__name__)
        _logger.debug('FGF _get_product_expense ids %s' % ids)
        product_ids = []
        product_ids = self.pool.get('product.product').search(cr, uid, [('categ_id','in', ids)])
        _logger.debug('FGF _get_product_expense product_ids %s' % product_ids)
        return product_ids


    _columns = {
        'valuation1':  fields.function(_get_product_valuation1, method=True, string="Valuation",type='float',digits_compute=dp.get_precision('Account')),
        'valuation2': fields.function(_get_product_valuation2, method=True, string="Valuation Comp",type='float',digits_compute=dp.get_precision('Account')),
        'valuation_diff': fields.function(_get_valuation_diff, method=True, string="Valuation Diff",type='float',digits_compute=dp.get_precision('Account')),
        'avg_price':  fields.function(_get_avg_price, method=True, string="Avg Price",type='float',digits_compute=dp.get_precision('Account')),
        'stock_account_id':  fields.related('categ_id','property_stock_valuation_account_id',type="many2one", relation="account.account", string='Stock Valuation Account',store=False,readonly=True),
        'expense_account_id':  fields.function(_get_expense_account, method=True, string='Expense Account', type='many2one', relation='account.account',  select="1",
                    store = False
            #       store =  {
            #          'product.category' : ( _get_product_expense, ['property_account_expense_categ'], 10)
            #                }
                   ),
           }

    def fields_to_check(self, cr, uid):
        fields = super(product_product, self).fields_to_check(cr, uid)
        if fields:
            fields.append( 'valuation1' )
            fields.append( 'valuation2' )
        return fields

product_product()

#----------------------------------------------------------
#  Stock Move INHERIT
#----------------------------------------------------------
class stock_move(osv.osv):
    _inherit = "stock.move"
    _logger = logging.getLogger(__name__)

    def _compute_move_value_cost(self, cr, uid, ids, name, args, context):
        if not ids : return {}
        # ids must be sorted by date
        #self._logger.debug('sql tuple ids `%s`', tuple(ids))
        #for move in self.browse(cr, uid, ids, context):
        #    if not move.move_value_cost:
        #        self._logger.debug('sql append r `%s`', move.id)
        #        ids2.append(move.id)
        d = {}
        for move in self.browse(cr, uid, ids):
            d[move.date] = move.id
        self._logger.debug('FGF d %s', d)
        ids3 = []
        for date  in sorted(d):
            ids3.append(d[date])
        self._logger.debug('FGF ids3 `%s`', ids3)
        return self._compute_move_value_cost2(cr, uid, ids3, context)

    def _compute_move_value_cost2(self, cr, uid, ids2,  context):
        res_curr_acc = self.pool.get('res.currency')
        self._logger.debug('sql sorted ids `%s`', ids2)
        if not context:
            context = {}
        result = {}
        digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        self._logger.debug('digits `%s`', digits)
        for move in self.browse(cr, uid, ids2):
            self._logger.debug('type cost `%s`', move.picking_id.type)
            #if move.state in ['done','cancel']:
            if move.state in ['cancel']:
                result[move.id] = 0

            if move.value_correction:
                result[move.id] = -move.value_correction # to allow "natural" data entry : stock_location (source) : positive to increase value
            elif move.purchase_line_id:
                # FIXME shell we use the price_unit from stock_move? in standard module it is not possible to enter price_unit in pickings
                # anser is YES
                if move.price_unit and move.purchase_line_id.order_id.state != 'draft':
                    result[move.id] = round(move.product_qty * move.price_unit,digits)
                else:
                    rate = res_curr_acc._get_conversion_rate(cr, uid, move.purchase_line_id.order_id.pricelist_id.currency_id, move.company_id.currency_id, context=context)
                    result[move.id] = round(move.purchase_line_id.price_subtotal / move.purchase_line_id.product_qty * move.product_qty * rate ,digits)
            elif move.location_id.usage == 'internal':
                loc_id = str(move.location_id.id)
                self._logger.debug('loc_id `%s`', loc_id)
                # compute avg price per stock location
                # FIXME this must be replaced by python dictionary computation to allow recomputation of avg price
                sql = 'select \
                 sum( case when location_id = '+loc_id+' then -move_value_cost else 0 end + case when location_dest_id = '+loc_id+' then move_value_cost else 0 end) as sum_amount, \
                 sum( case when location_id = '+loc_id+' then -product_qty else 0 end + case when location_dest_id     = '+loc_id+' then product_qty else 0 end) as sum_qty \
                 from stock_move \
                where product_id = '+ str(move.product_id.id) +' \
                  and state = \'done\' \
                  and (location_id = '+loc_id+' or location_dest_id = '+loc_id+') \
                  and date <= to_date(\''+ move.date + '\',\'YYYY-MM-DD HH24:MI:SS\') and id != '+ str(move.id)
                if move.prodlot_id:
                    sql = sql + ' and prodlot_id = ' + str(move.prodlot_id.id )
                #self._logger.debug('sql move_value_cost`%s`', sql)
                cr.execute(sql)
                for r in cr.dictfetchall():
                    sum_amount = r['sum_amount']
                    sum_qty    = r['sum_qty']
                    self._logger.debug('FGF sum product %s %s %s %s' % (move.product_id.id, move.date,sum_amount, sum_qty))
                    if sum_qty and sum_qty > 0.0 and sum_amount > 0.0:
                        avg_price = sum_amount / sum_qty
                        result[move.id] = round(move.product_qty * avg_price,digits)
                    else :
                        result[move.id] = round(move.product_qty * move.product_id.standard_price,digits)
            else:
                if move.price_unit and move.price_unit != 0:
                    result[move.id] = round(move.product_qty * move.price_unit,digits)
                else:
                    result[move.id] = round(move.product_qty * move.product_id.standard_price,digits)
            if context.get('init', False) :
                #we must use sql, because we do not want to run all checks - especially for not existing lots - for historical data
                sql = 'update stock_move set move_value_cost = round(%s,%s) where id = %d' % (result[move.id],digits,move.id)
                self._logger.debug('sql init sql %s' % (sql))
                cr.execute(sql)

        self._logger.debug('FGF result `%s`', result)
        return result

    def _compute_move_value_sale(self, cr, uid, ids, name, args, context):
        self._logger.debug('value_sale')
        res_curr_acc = self.pool.get('res.currency')
        digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        if not ids: return {}
        result = {}
        for move in self.browse(cr, uid, ids):
            if move.state in ['done','cancel']: return {}
            self._logger.debug('type sale `%s`', move.picking_id.type)
            if move.sale_line_id:
                rate = res_curr_acc._get_conversion_rate(cr, uid, move.sale_line_id.order_id.pricelist_id.currency_id, move.company_id.currency_id, context=context)
                result[move.id] = round(move.product_qty * move.sale_line_id.price_unit * rate, digits)
                self._logger.debug('value_sale `%s`', result[move.id])
        return result

    def _compute_price_unit_sale(self, cr, uid, ids, name, args, context):
        self._logger.debug('value_price')
        if not ids: return {}
        result = {}
        for move in self.browse(cr, uid, ids):
            avg_price = 0.0
            if move.picking_id.type == 'out' and move.state != 'cancel' and move.product_qty and move.product_qty != 0:
                self._logger.debug('type sale `%s`', move.picking_id.type)
                avg_price = move.move_value_sale / move.product_qty
            result[move.id] = avg_price
            self._logger.debug('value_sale `%s`', result[move.id])
        return result


    def _period_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            #period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',move.date),('date_stop','>=',move.date ), ('special','=',False)])
            #period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',move.date),('date_stop','>=',move.date ),('special','!=', True)])
            period_ids= self.pool.get('account.period').search(cr,uid,[('date_start','<=',move.date_expected),('date_stop','>=',move.date_expected ),('special','!=', True)])

            if len(period_ids):
                result[move.id] = period_ids[0]

        return result

    def _get_purchase_order_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            ids2 = self.search(cr, uid, [('purchase_line_id','=',int(line.id))])
        return ids2

    def _get_sale_order_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            ids2 = self.search(cr, uid, [('sale_line_id','=',line.id)])
        return ids2

    def _get_stock_move(self, cr, uid, ids, context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            ids2 = self.search(cr, uid, [('product_id','=',line.product_id.id),('date','>=', line.date)])
        return ids2
 
 

    _columns = {
        'move_value_cost'    : fields.function(_compute_move_value_cost, method=True, string='Amount', digits_compute=dp.get_precision('Account'),type='float' ,
           store={
               'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['product_qty', 'price_unit','price_unit_pu','value_correction', 'state'], 20),
               #'stock.move': (_get_stock_move,  ['product_qty', 'price_unit', 'value_correction', 'state'], 20),
               #'purchase.order.line': (_get_purchase_order_line, ['product_qty', 'price_subtotal'], 20),
                 },
                            help="""Product's cost for accounting valuation.""") ,
        'move_value_sale'    : fields.function(_compute_move_value_sale, method=True, string='Amount Sale', digits_compute=dp.get_precision('Account'),type='float' ,
           store={
               'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['product_qty', 'state'], 20),
               #'sale.order.line': (_get_sale_order_line, ['product_qty', 'price_subtotal'], 20),
                 },
                             help="""Product's sale value for accounting valuation.""") ,
        'period_id'          : fields.function(_period_id, method=True, string="Period",type='many2one', relation='account.period', store=True, select="1",  ),
        'price_unit_sale'    : fields.function(_compute_price_unit_sale, method=True, string='Sale Price',  digits_compute=dp.get_precision('Account') ),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'value_correction'   : fields.float('Value correction', digits_compute=dp.get_precision('Account'),\
                             help="This field allows to enter value correction of product stock per lot and location. positive to increase, negative to decrease value"),
        #'date_move'          : fields.related('picking_id', 'date', type='datetime', string='move Date'),
        'date_done'          : fields.datetime('Date Done'),
 
    }


    _defaults = {
        'date': None,
        }

    def onchange_date(self, cr, uid, ids, date, date_expected, context=None):
        return {'value': {}}

    def onchange_date_move(self, cr, uid, ids, date, date_expected, move_date, context=None):
        """ On change of Scheduled Date uses Move date.
        @param date_expected: Scheduled Date
        @param date: Move Date
        @return: Move Date
        """
        #self._logger.debug('change ids %s context %s' % (ids,context))
        
        vals = {}
        if move_date:
            if not date:
                vals['date'] = move_date 
            #if not date_expected:
                vals['date_expected'] = move_date 
        return {'value': vals}

    def init(self, cr):
        ids2 = []
        sql = 'select id, date , product_id\
                 from stock_move  \
                where move_value_cost is null \
                order by product_id, date '
        cr.execute(sql)
        for r in cr.dictfetchall():
            ids2.append(r['id'])
        context = {}
        context['init'] = True
        self._compute_move_value_cost2(cr, 1, ids2, context)

    def onchange_product_id_value(self, cr, uid, ids, prod_id=False, loc_id=False,
                                                loc_dest_id=False, address_id=False):
        res = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, address_id)
        self._logger.debug('FGF on change produc id %s', res)

        #if res.get('value'):
        res['value']['product_qty'] = 0.0
        res['value']['location_id'] = ''
        res['value']['name'] = _('Value Difference') +': '+ res['value']['name']
        #else:
        #    res = {'value' : {'product_qty' : 0.0 }}
        # find inventory location

        return res

#    def init(self, cr):
      # Purchase
#      cr.execute("""
#          update stock_move m set move_value_cost = (select m.product_qty * p.price_unit from purchase_order_line p
#                                   where p.id = m.purchase_line_id) where move_value_cost is null;
#      """)
#      # Sales
#      cr.execute("""
#          update stock_move m set move_value_sale = (select m.product_qty * l.price_unit from sale_order_line l
#                                   where l.id = m.sale_line_id) where move_value_sale is null;
#      """)
#      # other
#      cr.execute("""
#          update stock_move m set move_value_cost = (select m.product_qty * t.standard_price from product_product p, product_template t
#                                   where p.id = m.product_id and t.id = p.product_tmpl_id) where move_value_cost is null;
#      """)



    def action_correction_done(self, cr, uid, ids, context=None):
        """to be able to post moves for past dates (mainly corrections) it is necessary to store the date_expected instead of the current date
          the date field is used to select records in the location structure and others
          for accounting purpose it is absolutely necessary to be able to do this.
          * correct errors
          * do valuation correction
        """
        move_ids = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
            move_ids.append(move.id)
            date1 = move.date
        res = super(stock_move, self).action_done(cr, uid, move_ids, context)
        self.write(cr, uid, move_ids, {'date': date1, 'date_expected' : date1,'date_done': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return res

    def action_done(self, cr, uid, ids, context=None):
        """to be able to post moves for past dates (mainly corrections) it is necessary to store the date_expected instead of the current date
          the date field is used to select records in the location structure and others
          for accounting purpose it is absolutely necessary to be able to do this.
          * correct errors
          * do valuation correction
        """
        move_ids = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                 continue
            move_ids.append(move.id)
            date1 = move.date
        res = super(stock_move, self).action_done(cr, uid, move_ids, context)
          
        self.write(cr, uid, move_ids, {'date': date1, 'date_expected' : date1, 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        return res





stock_move()

class stock_location(osv.osv):
    _inherit=  "stock.location"
    _logger = logging.getLogger(__name__)


    def _product_get(self, cr, uid, id, product_ids=False, context=None, states=['done']):
        if not context:
            context = {}
        prodlot_null = context.get('prodlot_null', False)
        if not prodlot_null:
            self._logger.debug('FGF product_get standard %s', context )
            return super(stock_location, self)._product_get(cr, uid, id, product_ids, context, states)
        else:
            # FIXME
            # we shell use product_qty_calc definend in  /stock_product_zero/inventory.py instead recomputing
            # recomputing always bears the risk that someone posts move in the meantime

            move_obj = self.pool.get('stock.move')
            uom_obj = self.pool.get('product.uom')
            product_obj = self.pool.get('product.product')
            res = {}

            if not isinstance(product_ids,list):
                product_ids = [ product_ids ]

            for prod in product_obj.browse(cr, uid, product_ids, context):
                move_obj = self.pool.get('stock.move')
                uom_obj = self.pool.get('product.uom')
                location = context['location']
                prodlot_id = context['prodlot_id']

                if prodlot_id:
                    move_ids = move_obj.search(cr, uid, [('location_dest_id','=',id),('product_id','=',prod.id),('prodlot_id','=',prodlot_id), ('state','=','done')], )
                    move_ids2 = move_obj.search(cr, uid, [('location_id','=',id),('product_id','=',prod.id),('prodlot_id','=',prodlot_id), ('state','=','done')], )
                else:
                    move_ids = move_obj.search(cr, uid, [('location_dest_id','=',id),('product_id','=',prod.id),('prodlot_id','=',False), ('state','=','done')], )
                    move_ids2 = move_obj.search(cr, uid, [('location_id','=',id),('product_id','=',prod.id),('prodlot_id','=',False), ('state','=','done')], )

                qty = 0.0
                for move in move_obj.browse(cr, uid, move_ids, context=context):
                    qty += uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
                for move in move_obj.browse(cr, uid, move_ids2, context=context):
                    qty -= uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)


                res[prod.id] = qty
                self._logger.debug('FGF product_get inventur %s %s %s' % ( qty, prod.name, context) )
            return res



stock_location()

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    _logger = logging.getLogger(__name__)
    _columns = {
        'recursive': fields.boolean("Include children", readonly=True, help="If checked, products contained in child locations of selected location are included as well."),
        'location_id'        : fields.many2one('stock.location','Location', select=True, readonly=True, help="Displays selected loaction"),
        }


    def _inventory_line_hook(self, cr, uid, line, value):
        """ Creates a stock move from an inventory line
        calculates the inv difference between product_qty and product_qty_calc
        @param inventory_line:
        @param move_vals:
        @return:
        """
        self._logger.debug('FGF inv line hook %s %s' % ( line, value)  )
        change = line.product_qty - line.product_qty_calc
        location_id = line.product_id.product_tmpl_id.property_stock_inventory.id

        if change > 0:
            value.update( {
                'product_qty': change,
                'location_id': location_id,
                'location_dest_id': line.location_id.id,
            })
        else :
            value.update( {
                'product_qty': -change,
                'location_id': line.location_id.id,
                'location_dest_id': location_id,
            })
        self._logger.debug('FGF inv line hook after %s %s %s' % (change, line, value)  )
        return super(stock_inventory, self)._inventory_line_hook(cr, uid, line, value)

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        computes difference between data entry and computed values for the inventory
        does not create 0 lines
        @return: True
        """
        if context is None:
            context = {}
        # to perform the correct inventory corrections we need analyze stock location by
        # location, never recursively, so we use a special context
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in inv.inventory_line_id:
                pid = line.product_id.id

                #product_context.update(uom=line.product_uom.id, to_date=inv.date, date=inv.date, prodlot_id=line.prod_lot_id.id)
                #amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]

                change = line.product_qty - line.product_qty_calc
                lot_id = line.prod_lot_id.id
                if change:
                    location_id = line.product_id.product_tmpl_id.property_stock_inventory.id
                    value = {
                        'name': 'INV:' + str(line.inventory_id.id) + ':' + line.inventory_id.name,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'prodlot_id': lot_id,
                        'date': inv.date,
                    }
                    if change > 0:
                        value.update( {
                            'product_qty': change,
                            'location_id': location_id,
                            'location_dest_id': line.location_id.id,
                        })
                        move_ids.append(self._inventory_line_hook(cr, uid, line, value))

                    elif change < 0:
                        value.update( {
                            'product_qty': -change,
                            'location_id': line.location_id.id,
                            'location_dest_id': location_id,
                        })
                        move_ids.append(self._inventory_line_hook(cr, uid, line, value))
            if move_ids:
                message = _("Inventory '%s' is done.") %(inv.name)
                self.log(cr, uid, inv.id, message)
                self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
                self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)
            else:
                message = _("Inventory '%s' nothing to do - Please cancel the inventory.") %(inv.name)
        return True


    def action_done(self, cr, uid, ids, context=None):
        """ Finish the inventory
        set the inv date as move date
        @return: True
        """
        res = super(stock_inventory, self).action_done(cr, uid, ids, context)

        move_obj = self.pool.get('stock.move')
        move_ids = []
        for inv in self.browse(cr, uid, ids):
            for m in inv.move_ids:
                move_ids.append(m.id)
        move_obj.write(cr, uid, move_ids, {'date':  inv.date,'date_expected': inv.date})

        return True

stock_inventory()

class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"
    _columns = {
          'check_lot' : fields.related('product_id','track_internal',type='boolean',string='Lot required',readonly=True,help="posting needs lot"),
        }
stock_inventory_line()


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    _defaults = {
     'date' : None,
    }

stock_picking()
