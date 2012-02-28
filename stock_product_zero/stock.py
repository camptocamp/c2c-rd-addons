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


from osv import fields, osv
import sys
import logging
_logger = logging.getLogger(__name__)


class stock_location_product(osv.osv_memory):
    _inherit = "stock.location.product"
    _columns = {
        'display_with_zero_qty' : fields.boolean('Display lines with zero'),
    }

    def action_open_window_nok(self, cr, uid, ids, context=None):
        res = super(stock_location_product, self).action_open_window( cr, uid, ids, context=None)
        # FIXME logging seems not to work in memory objects
        self._logger.info('FGF stock_location_product action_open_window pre %s', res) 

        location_products = self.read(cr, uid, ids, ['display_with_zero_qty'], context)
        # FIXME - I am not able to add display_with_zero_qty to context
        #raise osv.except_osv(_('FGF Warning !'), _('We check location_products:'))

        if location_products:
            res['context']['display_with_zero_qty'] = location_products['display_with_zero_qty']

        #self._logger.info('FGF stock_location_product action_open_window post %s', res) 
        return res

    def action_open_window(self, cr, uid, ids, context=None):
        """ To open location wise product information specific to given duration
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: An ID or list of IDs if we want more than one
         @param context: A standard dictionary
         @return: Invoice type
        """
        #mod_obj = self.pool.get('ir.model.data')
        for location_obj in self.read(cr, uid, ids, ['from_date', 'to_date','display_with_zero_qty']):
            return {
                'name': False,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'product.product',
                'type': 'ir.actions.act_window',
                'context': {'location': context['active_id'],
                       'from_date': location_obj['from_date'],
                       'to_date': location_obj['to_date'],
                       'display_with_zero_qty': location_obj['display_with_zero_qty'],
                },
                'domain': [('type', '<>', 'service')],
            }

stock_location_product()


class product_product(osv.osv):
    _inherit = "product.product"


    # FIXME this returns correct records, but group by catagory ignores this and uses all results for grouping 
    # opening a category crashes
    def read_test(self,cr, uid, ids, fields=None, context=None, load='_classic_read'):
        res_all = super(product_product, self).read(cr,uid, ids, fields, context, load='_classic_read')
        res = []
        _logger = logging.getLogger(__name__)
        _logger.info('FGF stock_location_product read ids %s', res_all)
        if  context.get('display_with_zero_qty') and context.get('display_with_zero_qty') == False:
          _logger.info('FGF stock_location_product read  only not null')
         
          for prod in self.browse(cr, uid, res_all):
            qty = prod.get('qty_available')
            vir = prod.get('virtual_available')
            if qty <> 0.0 or vir <> 0.0:
               res.append(prod) 
        else: 
           _logger.info('FGF stock_location_product  all')
        res = res_all
        # FIXME - result should be sorted by name 
        # http://wiki.python.org/moin/SortingListsOfDictionaries - returns (unicode?) error on name  
        return res
        
    def search(self, cr, uid, args, offset=0, limit=None,
                order=None, context=None, count=False):
        res_all = super(product_product, self).search(cr, uid, args, offset, limit,
                order, context=context, count=count)
        _logger = logging.getLogger(__name__)
        _logger.info('FGF stock_location_product  ids %s', res_all)
        _logger.info('FGF stock_location_product context %s', context)
        res = []
        if context.get('display_with_zero_qty') and context.get('display_with_zero_qty') == False :
        #if context.get('location') :
            _logger.info('FGF stock_location_product only not 0')
            for prod in self.browse(cr,uid,res_all,context):
                if prod.qty_available <> 0.0 or prod.virtual_available <> 0.0:
                    res.append(prod.id)
        else:
            _logger.info('FGF stock_location_product all')
            res = res_all
 
        return res
      
product_product()
