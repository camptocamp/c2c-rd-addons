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
        'half_year_rule':fields.boolean('Half Year Depreciation', help='Computes full/half depreciation for usage in fist/second half year'),
        }

    #_defaults['half_year_rule'] : True
              
account_asset_category()


class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'

    _columns = {
        'half_year_rule':fields.boolean('Half Year Depreciation', help='Computes full/half depreciation for usage in fist/second half year'),
        'activation_date': fields.date('Activation Date', readonly=True, states={'draft':[('readonly',False)]},  help='Is used instead of purchase date if set'),
        }




    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        period_obj = self.pool.get('account.period')
        for asset in self.browse(cr, uid, ids, context=context):
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)])
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual
            
            if asset.half_year_rule:
                # are we in the first year ?
                _logger  = logging.getLogger(__name__)
                _logger.debug('FGF asset %s ' %(asset.activation_date)   )
                dep_start = asset.activation_date or asset.purchase_date
                #_logger.debug('FGF asset date %s ' %(dep_start)   )
                #_logger.debug('FGF asset date type %s ' %(type(dep_start))   )
                dep_start_date = datetime.strptime(dep_start, '%Y-%m-%d')
                _logger.debug('FGF asset depr start date %s ' %(dep_start_date)   )
                #_logger.debug('FGF asset date type %s ' %(type(dep_start_date))   )
                #fy_id = fiscalyear_obj.search(cr, uid, [('date_start','<=',dep_start_date), ('date_stop','>=',dep_start_date)], context)
                fy_id = fiscalyear_obj.search(cr, uid, [('date_start','<=',dep_start_date), ('date_stop','>=',dep_start_date)])
                #fy_id = fiscalyear_obj.search(cr, uid, [('date_start','<=',asset.purchase_date), ('date_stop','>=',asset.purchase_date)], context)
                #diff = 0
                if fy_id:
                    for fy_dates in fiscalyear_obj.browse(cr, uid, fy_id):
                        date_stop_minus6 = datetime.strptime(fy_dates.date_stop, '%Y-%m-%d') - relativedelta(months=6)
                        _logger.debug('FGF asset mid_year %s ' %(date_stop_minus6)   )
                        #if datetime.strptime(asset.purchase_date,'%Y-%m-%d') > date_stop_minus6 :
                        if  dep_start_date > date_stop_minus6 :
                            d_date = date_stop_minus6 + timedelta(days=1)
                            diff = 0
                            _logger.debug('FGF asset half %s ' %(d_date)   )
                        else:
                            d_date = datetime.strptime(fy_dates.date_start, '%Y-%m-%d')
                            diff = 1
                        
                        depreciation_date = d_date
                        _logger.debug('FGF asset depr_date %s ' %(depreciation_date)   )
                        total_days = (datetime.strptime(fy_dates.date_stop, '%Y-%m-%d') - datetime.strptime(fy_dates.date_start, '%Y-%m-%d')).days +1 + diff
                        _logger.debug('FGF depr_days %s ' %(total_days))
                        #total_days = 366 +diff
                        _logger.debug('FGF depr_days %s ' %(total_days))
                else:        
                    depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
            elif asset.prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
            else:
                # depreciation_date = 1st January of purchase fiscalyear
                fy_id = fiscalyear_obj.search(cr, uid, [('date_start','<=',asset.purchase_date), ('date_stop','>=',asset.purchase_date)], context)
                if fy_id:
                    for  fy_dates in fiscalyear_obj.browse(cr, uid, [fy_id]):
                        depreciation_date = datetime.strptime(fy_dates.start_date, '%Y-%m-%d')
                
            day = depreciation_date.day
            month = depreciation_date.month
            year = depreciation_date.year
            if total_days == 0:
                total_days = (year % 4) and 365 or 366 
            
            

            undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                i = x + 1 
                amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                residual_amount -= amount
                vals = { 
                     'amount': amount,
                     'asset_id': asset.id,
                     'sequence': i,
                     'name': str(asset.id) +'/' + str(i),
                     'remaining_value': residual_amount,
                     'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount),
                     'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }   
                depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                depreciation_date = (datetime(year, month, day) + relativedelta(months=+asset.method_period))
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        return True
  
              
account_asset_asset()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

