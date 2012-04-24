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
from osv import fields, osv
from tools.translate import _
import logging

class account_move(osv.osv):
    _inherit = "account.move"
    _logger = logging.getLogger(__name__)

    def post(self, cr, uid, ids, context=None):
        self._logger.debug('post move context `%s`', context)
	if not context:
            context= {}
        journal_id = context.get('journal_id')
        period_id = []
        if 'period_id' in context:
           period_id = [context.get('period_id')]
        self._logger.debug('post move period_id `%s`', period_id)
        invoice_obj = context.get('invoice')
        if invoice_obj and not journal_id:
           journal_id = invoice_obj.journal_id.id
        self._logger.debug('post move journal `%s`', journal_id)
        jour_obj = self.pool.get('account.journal')
        seq_obj  = self.pool.get('ir.sequence')
        if journal_id:
          for jour in jour_obj.browse(cr, uid, [journal_id] , context=context):
            self._logger.debug('post jour `%s` `%s`', jour, jour.sequence_id)
            if jour.sequence_id: 
                main_seq_id = jour.sequence_id.id
            elif jour.create_sequence in ['create','create_fy']:
                prefix = jour.prefix_pattern or "".join(w[0] for w in _(jour.name).split(' '))
                values = \
                            { 'name'           : jour.name
                            , 'prefix'         : prefix
                            , 'padding'        : 3
                            , 'implementation' : 'no_gap'
                            }
                main_seq_id = seq_obj.create(cr, uid, values)
                jou_obj.write(cr, uid, [journal_id], {'sequence_id' : main_seq_id})
            
            if jour.create_sequence == 'create_fy' :  
                fy_seq_obj = self.pool.get('account.sequence.fiscalyear')
                period_obj = self.pool.get('account.period')
                if not period_id:
                   self._logger.debug('per_id A')
                   period_id = invoice_obj.period_id.id 
                   self._logger.debug('per_id B `%s`', period_id)
                   if not period_id:
                       self._logger.debug('per_id C `%s`', period_id)
                       period_id = period_obj.find(cr, uid, invoice_obj.date_invoice, context)
                   self._logger.debug('per_id D `%s`', period_id)
                
                if not isinstance(period_id, list) :
                    period_id = [period_id] 
                for period in period_obj.browse(cr, uid, period_id):
                    self._logger.debug('fy_id `%s`', period)
                    fy_id = period.fiscalyear_id.id
                    fy_code =  period.fiscalyear_id.code
                    self._logger.debug('fy_id a `%s`', fy_id)
                fy_seq = fy_seq_obj.search(cr, uid, [('fiscalyear_id','=', fy_id),('sequence_main_id','=',main_seq_id)])
                self._logger.debug('fy_seq_id `%s`', fy_seq)
                if not fy_seq:
                   prefix = jour.prefix_pattern or "".join(w[0] for w in _(jour.name).split(' ')) + '-%(fy)s-'
                    
                   values = \
                            { 'name'           : jour.name + ' ' +  fy_code
                            , 'prefix'         : prefix
                            , 'padding'        : 3
                            , 'implementation' : 'no_gap'
                            }
                   fy_seq_id = seq_obj.create(cr, uid, values)
                   fy_rel = \
                          { 'sequence_id'      : fy_seq_id
                          , 'sequence_main_id' : main_seq_id
                          , 'fiscalyear_id'    : fy_id
                          }   
                   self._logger.debug('fy_rel `%s``%s`', fy_rel, prefix)
                   fy_seq_obj.create(cr, uid, fy_rel)
          #return True
        return super(account_move, self).post(cr, uid, ids, context)

account_move()
