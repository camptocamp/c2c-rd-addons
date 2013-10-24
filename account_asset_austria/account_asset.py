# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2004-2013 Camptocamp Austria (<http://camptocamp.com>).
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



from osv import osv, fields
import decimal_precision as dp

import time
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from tools.translate import _
import logging


class account_asset_category(osv.osv):
    _inherit = 'account.asset.category'

    _columns = {
        'half_year_rule':fields.boolean('Half Year Depreciation', help='Computes full/half depreciation for activation/purchase in fist/second half year'),
        }

    #_defaults['half_year_rule'] : True
              
account_asset_category()


class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'

    _columns = {
        'half_year_rule':fields.boolean('Half Year Depreciation', help='Computes full/half depreciation for usage in fist/second half year'),
        'activation_date': fields.date('Activation Date', readonly=True, states={'draft':[('readonly',False)]},  help='Is used instead of purchase date if set'),
        'depreciation_start_date': fields.date('Depreciation Start Date', readonly=True, states={'draft':[('readonly',False)]},  help='compteted date'),
        }
    
    _defaults = {
        'half_year_rule' : True
        }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        asset = self.browse(cr, uid, id, context=context)
        default.update({'depreciation_line_ids': [],'history_ids': [], 'account_move_line_ids':[], 'name': asset.name+ " (copy)", 'code': asset.code+ " (copy)", 'state': 'draft'})

        return super(account_asset_asset, self).copy(cr, uid, id, default, context=context)


    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        # Austrian half year rule
        _logger  = logging.getLogger(__name__)
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        if asset.half_year_rule: # and i < undone_dotation_number:
            amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids)) # yearly amount
            _logger.debug('FGF half_year_rule %s ' %(amount)   )
            if i == 1: 
                dep_start = asset.activation_date or asset.purchase_date
                dep_start_date = datetime.strptime(dep_start, '%Y-%m-%d')
                fy_id = fiscalyear_obj.search(cr, uid, [('date_start','<=',dep_start_date), ('date_stop','>=',dep_start_date)])
                for fy_dates in fiscalyear_obj.browse(cr, uid, fy_id):
                    date_stop_minus6 = datetime.strptime(fy_dates.date_stop, '%Y-%m-%d') - relativedelta(months=6)
                    _logger.debug('FGF asset mid_year %s ' %(date_stop_minus6)   )
                    if  dep_start_date > date_stop_minus6 :
                        amount = amount/2
            if i == undone_dotation_number:
                residual_amount -= amount
                
        else:
            
            amount = super(account_asset_asset, self)._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None)
            #_logger.debug('FGF half_year_rule missed %s ' %(i)   )
        return amount
             
    def compute_depreciation_board(self, cr, uid, ids, context=None):

        for asset in self.browse(cr, uid, ids, context):
            if asset.half_year_rule and (asset.prorata or asset.method != 'linear'):
                self.write(cr, uid, [asset.id], {'prorata':False, 'method':'linear'})

        res = super(account_asset_asset, self).compute_depreciation_board(cr, uid, ids, context=None)
        
        for asset in self.browse(cr, uid, ids, context):
            remaining_value = 0 
            line_count = 0
            for line in asset.depreciation_line_ids:
                if line_count > 0 and line.remaining_value < remaining_value:
                    last_line = line
                    remaining_value = line.remaining_value
                else:
                    last_line = line
                    remaining_value = line.remaining_value
            if remaining_value > 0:
                depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
                vals = {
                        'amount': remaining_value,
                        'asset_id': last_line.asset_id.id,
                        'sequence': last_line.sequence + 1,
                        'name': str(asset.id) +'/' + str(last_line.sequence + 1),
                        'remaining_value': 0,
                        'depreciated_value': (asset.purchase_value - asset.salvage_value) - (last_line.remaining_value),
                        'depreciation_date': (datetime.strptime(last_line.depreciation_date, '%Y-%m-%d') + relativedelta(years=1)).strftime('%Y-%m-%d') ,
                    }
                depreciation_lin_obj.create(cr, uid, vals, context=context)
        
        return res


    def write(self, cr, uid, ids, vals, context=None):
        result = super(account_asset_asset, self).write(cr, uid, ids, vals, context=context)
        self.compute_depreciation_board(cr, uid, ids, context=context)
        return result

            
account_asset_asset()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

