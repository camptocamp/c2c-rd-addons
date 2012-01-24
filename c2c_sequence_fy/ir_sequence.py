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
import time
from osv import fields, osv
from tools.translate import _
import sys

class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'

    def next_by_id(self, cr, uid, sequence_id, context=None):
        """ Draw an interpolated string using the specified sequence."""
        print >> sys.stderr,'next_by_id ',sequence_id,context
        self.check_read(cr, uid)
        company_ids = self.pool.get('res.company').search(cr, uid, [], order='company_id', context=context) + [False]
        fy_seq_id = sequence_id
        if context and context['fiscalyear_id'] :
          fy = context['fiscalyear_id'] 
          print >> sys.stderr,'fy', fy
          if fy:
            fy_seq = self.pool.get('account.sequence.fiscalyear').search(cr, uid,  [('sequence_main_id','=', sequence_id),('fiscalyear_id','=',fy)])
            for fy_s in  self.pool.get('account.sequence.fiscalyear').browse(cr, uid, fy_seq):
               fy_seq_id = fy_s.sequence_id.id
        print >> sys.stderr,'next_by_id seq_id',  fy_seq_id
             
        #ids = self.search(cr, uid, ['&',('id','=', sequence_id),('company_id','in',company_ids)])
        return self._next(cr, uid, fy_seq_id , context)

    def _abbrev(self, name, separator):
        return "".join(w[0] for w in _(name).split(separator))
    # end def _abbrev
    
    def _fy_code(self, cr, uid, context) :
        if context and ('fiscalyear_id' in context) and context.get('fiscalyear_id', False): 
          fy_id = context.get('fiscalyear_id', False)
          if fy_id :
            fiscalyear_obj = self.pool.get('account.fiscalyear')
            fy = fiscalyear_obj.browse(cr, uid, fy_id)
            return fy.sequence_code or fy.date_start[0:4]
        else :
            return time.strftime('%Y')
    # end def _fy_code

    def name_get(self, cr, uid, ids, context=None):
        if not ids : return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads :
            name = record['name']
            if record['code']:
                name = record['code'] + ' ' + name
            
            fy_id = context.get('fiscalyear_id', False)
            if fy_id :
                fy_seq_code = self._fy_code(cr, uid, context)
                name = record['code'] + ' [' +  fy_seq_code  + ']'
            res.append((record['id'], name))
        return res
    # end def name_get

    def _journal(self, cr, uid, seq) :
        journal_obj = self.pool.get('account.journal')
        jou = journal_obj.browse(cr, uid, journal_obj.search(cr, uid, [('sequence_id', '=', seq.id)]))
        if jou :
            return jou[0]
        else :
            return False
    # end def _journal
    
    def _journal_name(self, cr, uid, seq) :
        jou = self._journal(cr, uid, seq)
        if jou :
            return self._abbrev(jou.name, ' ')
        else :
            return ''
    # end def _journal_name
    
    def _seq_type(self, cr, uid, seq):
        seq_type_obj = self.pool.get('ir.sequence.type')
        ids = seq_type_obj.search(cr, uid, [('code', '=', seq.code)])
        if ids :
          return seq_type_obj.browse(cr, uid, ids[0])
        else :
            return False
    # end def _seq_type
    
    def _seq_type_name(self, cr, uid, seq) :
        ty = self._seq_type(cr, uid, seq)
        return self._abbrev(ty.name, ' ')       
    # end def _seq_type_name
    
    def _seq_type_code(self, cr, uid, seq) :
        ty = self._seq_type(cr, uid, seq)
        return self._abbrev(ty.code, '.')
    # end def _seq_type_code
    
    def _next_seq(self, cr, uid, id) :
        seq = self.browse(cr, uid, id)
        if isinstance(seq,list): 
           seq = self.browse(cr, uid, id)[0]
        
        print >> sys.stderr,'_next_seq', seq
        if seq.implementation == 'standard' :
            cr.execute("SELECT nextval('%s_%03d')" % (self._table, seq.id))
            seq.number_next = cr.fetchone()
        else:
            cr.execute("SELECT number_next FROM %s WHERE id=%s FOR UPDATE NOWAIT;" % (self._table, seq.id))
            seq.number_next = cr.fetchone()
            cr.execute("UPDATE %s SET number_next=number_next+number_increment WHERE id=%s" % (self._table, seq.id))
        return seq
    # end def _next_seq
    
    def _format(self, cr, uid, seq, context) :
        d = self._interpolation_dict()
        d['fy']  = self._fy_code(cr, uid, context)
        if self._seq_type(cr, uid, seq) :
            d['stn'] = self._seq_type_name(cr, uid, seq)
            d['stc'] = self._seq_type_code(cr, uid, seq)
        d['jn']  = self._journal_name(cr, uid, seq)
        ty = self._seq_type(cr, uid, seq)
        if seq.prefix :
            _prefix = self._interpolate(seq.prefix, d)
        elif ty and ty.prefix_pattern:
            _prefix = self._interpolate(ty.prefix_pattern or '', d)
        else :
            _prefix = ''
        if seq.suffix : 
            _suffix = self._interpolate(seq.suffix, d)
        elif ty and ty.suffix_pattern :
            _suffix = self._interpolate(ty.suffix_pattern or '', d)
        else :
            _suffix = ''
        return _prefix + ('%%0%sd' % seq.padding) % seq.number_next + _suffix
    # end def _format

    def _next(self, cr, uid, seq_ids, context=None) :
        if not seq_ids: return False
        seq = self._next_seq(cr, uid, seq_ids)
        return self._format(cr, uid, seq, context)
    # end def _next

    def next_by_code(self, cr, uid, sequence_code, context=None) :
        print >> sys.stderr,'next_by_code', sequence_code, context
        for user in  self.pool.get('res.users').browse(cr, uid, [uid],  context):
            print >> sys.stderr,'next_by_code comp', user 
            company_id = user.company_id.id
        seq_ids = self.search(cr, uid, ['&', ('code','=', sequence_code), ('company_id', '=', company_id)])
        if not seq_ids :
            seq_type_obj = self.pool.get('ir.sequence.type')
            seq_type_ids = seq_type_obj.search(cr, uid, [('code', '=', sequence_code)])
            if not seq_type_ids :
                raise osv.except_osv \
                    ( _('Integrity Error !')
                    , _('Missing sequence-code %s') % sequence_code
                    )
            seq_type = seq_type_obj.browse(cr, uid, seq_type_ids[0])
            if seq_type.create_sequence == 'none' :
                raise osv.except_osv \
                    ( _('Integrity Error !')
                    , _('Automatic creation not allowed for sequence-code %s with %s') 
                        % (sequence_code, seq_type.create_sequence)
                    )
            values = \
                { 'code'           : sequence_code
                , 'name'           : self._abbrev(seq_type.name, ' ')
#                , 'prefix'         :  # "%(stn)-"
                , 'padding'        : 3
                , 'implementation' : 'no_gap'
                }
            new_id = self.create(cr, uid, values)
            seq = self._next_seq(cr, uid, new_id)
            return self._format(cr, uid, seq, context)
        else :
            return super(ir_sequence, self).next_by_code(cr, uid, sequence_code, context=context)
    # end def next_by_code

ir_sequence()
