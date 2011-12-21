# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
#    Copyright (C) 2011-2011 Swing Entwicklung betrieblicher Informationssysteme GmbH (<http://www.swing-system.com>)
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

class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'

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
        ty = seq_type_obj.browse(cr, uid, seq_type_obj.search(cr, uid, [('code', '=', seq.code)]))
        if ty :
            return ty[0]
        else :
            return False
    # end def _seq_type
    
    def _seq_type_name(self, cr, uid, seq) :
        ty = self._seq_type(cr, uid, seq)
        if ty :
            return self._abbrev(ty.name, ' ')
        else :
            return ''
    # end def _seq_type_name
    
    def _seq_type_code(self, cr, uid, seq) :
        ty = self._seq_type(cr, uid, seq)
        if ty :
            return self._abbrev(ty.code, '.')
        else :
            return ''
    # end def _seq_type_code

    def _next(self, cr, uid, seq_ids, context=None) :
        import sys
        print >>sys.stderr, "_next begin"
        res = super(ir_sequence, self)._next(cr, uid, seq_ids, context)
        if not res:
            return False
        seq = self.browse(cr, uid, seq_ids[0])
        d = self._interpolation_dict()
        d['fy']  = self._fy_code(cr, uid, context)
        d['stn'] = self._seq_type_name(cr, uid, seq)
        d['stc'] = self._seq_type_code(cr, uid, seq)
        d['jn']  = self._journal_name(cr, uid, seq)
        if seq.prefix :
            _prefix = self._interpolate(seq.prefix, d)
        else :
            ty = self._seq_type(cr, uid, seq)
            _prefix = ty.prefix_pattern or ''
        if seq.suffix : 
            _suffix = self._interpolate(seq.suffix, d)
        else :
            ty = self._seq_type(cr, uid, seq)
            _suffix = ty.suffix_pattern or ''
        print >>sys.stderr, "_next end"
        return _prefix + '%%0%sd' % seq.padding % seq.number_next + _suffix
    # end def _next

ir_sequence()
