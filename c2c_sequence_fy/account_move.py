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
from tools.translate import _

class account_move(osv.osv):
    _inherit = "account.move"

    def post(self, cr, uid, ids, context=None):
        import sys
        print >> sys.stderr,'post move context',context 

        journal_id = context.get('journal_id')
        invoice_obj = context.get('invoice')
        if not journal_id:
           journal_id = invoice_obj.journal_id.id
        print >> sys.stderr,'post move journal', journal_id
        jour_obj = self.pool.get('account.journal')
        seq_obj  = self.pool.get('ir.sequence')
        if journal_id:
          for jour in jour_obj.browse(cr, uid, [journal_id] , context=context):
            print >> sys.stderr,'post jour', jour, jour.sequence_id
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
                period_ids = context.get('period_id')
                if not period_ids:
                   print >> sys.stderr,'per_id A'
                   period_id = invoice_obj.period_id.id 
                   print >> sys.stderr,'per_id B', period_id
                   if not period_id:
                       print >> sys.stderr,'per_id C', period_id
                       period_id = period_obj.find(cr, uid, invoice_obj.date_invoice, context)
                   print >> sys.stderr,'per_id D', period_id
                   
                for period in period_obj.browse(cr, uid, period_id):
                   fy_id = period.fiscalyear_id.id
                   fy_code =  period.fiscalyear_id.code
                   print >> sys.stderr,'fy_id', fy_id
                fy_seq = fy_seq_obj.search(cr, uid, [('fiscalyear_id','=', fy_id),('sequence_main_id','=',main_seq_id)])
                print >> sys.stderr,'fy_seq_id', fy_seq
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
                   print >> sys.stderr,'fy_rel',fy_rel, prefix
                   fy_seq_obj.create(cr, uid, fy_rel)
         
        return super(account_move, self).post(cr, uid, ids, context)
        

    def post_gk(self, cr, uid, ids, context=None):
        if context is None : context = {}
        invoice = context.get('invoice', False)
        valid_move_ids = self.validate(cr, uid, ids, context)
        if not valid_move_ids:
            raise osv.except_osv \
                ( _('Integrity Error !')
                , _('You cannot validate a non-balanced entry!\nMake sure you have configured Payment Term properly !\nIt should contain at least one Payment Term Line with type "Balance" !')
                )
        seq_obj = self.pool.get('ir.sequence')
        jou_obj = self.pool.get('account.journal')
        for move in self.browse(cr, uid, valid_move_ids, context=context):
            if move.name == '/':
                new_name = False
                journal = move.journal_id
                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = \
                            { 'fiscalyear_id' : move.period_id.fiscalyear_id.id
                            , 'journal_id'    : journal.id
                            }
                        new_name = seq_obj.next_by_id(cr, uid, journal.sequence_id.id, context=c)
                    else :
                        values = \
                            { 'name'           : move.journal_id.name
                            , 'prefix'         : "".join(w[0] for w in _(journal.name).split(' '))
                            , 'padding'        : 3
                            , 'implementation' : 'no_gap'
                            }
                        new_id   = seq_obj.create(cr, uid, values)
                        new_name = seq_obj._format(self, cr, uid, seq_obj.browse(cr, uid, new_id), context)
                        jou_obj.write(cr, uid, [journal_id.id], {'sequence_id' : new_id})
                self.write(cr, uid, [move.id], {'name' : new_name})
        self.write(cr, uid, valid_move_ids, {'state' : 'posted'})
        return True
    # end def post

account_move()
