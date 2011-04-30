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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter

import netsvc
import pooler
from osv import fields, osv
from tools.translate import _

import sys
# 
# this is ugly copied code, but I do not see any other possiblity to modify base/ir/sequence.py/_process parameters in the calling get_id due to get_id fy extension defined in account.
# 

import sys

class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"
    _columns = {
        'sequence_code': fields.char('Sequence Code', size=6,help="""This code will be used to format the start date of the fiscalyear for the placeholder 'fy' defined for sequences as prefix and suffix.
        Example a fiscal year starting on March 1st with a sequence code %Ya will generate 2011a.
        This allows to handle multiple fiscal years per calendar year and fiscal years not matching caledar years easily"""),
    }
account_fiscalyear()


class account_journal(osv.osv):
    _inherit = "account.journal"
    _columns = {
        'create_sequence': fields.selection([('none','No creation'), ('create','Create'), ('create_fy','Create per Fiscal Year')],'Create Seuqnce',\
                  help="""Sequence will be created automatically on the fly using the code of the journal and for fy the fy prefix to compose the prefix of the sequence""", required="True", 
        ),
    }
    
    def init(self, cr):
        cr.execute("""update account_journal
                         set create_sequence = 'create_fy'
        """)
account_journal()
#----------------------------------------------------------
# Entries Move - replace ir sequence
#----------------------------------------------------------

class ir_sequence_type(osv.osv):
    _inherit = 'ir.sequence.type'
    _columns = {
        'prefix': fields.char('Prefix',size=64, help="Prefix value of the record for the sequence"),
        'suffix': fields.char('Suffix',size=64, help="Suffix value of the record for the sequence"),
        'name_template' :  fields.char('Name template',size=64, help="ToDo - how to construct sequence name"),
        'create_sequence': fields.selection([('none','No creation'), ('create','Create'), ('create_fy','Create per Fiscal Year')],'Create Seuqnce',\
                  help="""Sequence will be created automatically on the fly using the code of the journal and for fy the fy prefix to compose the prefix of the sequence""", required="True", ),
    }
    def init(self, cr):
        cr.execute("""update ir_sequence_type
                         set create_sequence = 'create'
        """)


ir_sequence_type()

class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' '+name
            
            fy_id = context.get('fiscalyear_id', False)
            if fy_id:
                fy = self.pool.get('account.fiscalyear').browse(cr, uid, fy_id, context=None)
                t = datetime.strptime(fy.date_start, '%Y-%m-%d')
                fy_seq_code = ''
                if fy.sequence_code:
                    fy_seq_code= t.strftime(fy.sequence_code)
                else: 
                    fy_seq_code= t.strftime('%Y')
                name = record['code'] + ' [' +  fy_seq_code +']'
            res.append((record['id'], name))
        return res

    def init(self, cr):
        cr.execute("""update ir_sequence
                         set prefix = replace(prefix,'(year)','(fy)'),
                             suffix = replace(suffix,'(year)','(fy)')
        """)
        
    def _process_base(self, cr, uid, s, context):
        print >> sys.stderr , 'process', context, s
        if context.get('fiscalyear_id'):
           fy_id = context.get('fiscalyear_id', False)
           fy = self.pool.get('account.fiscalyear').browse(cr, uid, fy_id,  context=None)
           print >> sys.stderr , 'process fy ', fy
           if fy.sequence_code:
               fy_seq_code= fy.sequence_code
           else: 
               print >> sys.stderr , 'process fy date_start', fy.date_start[0:4]
               fy_seq_code= fy.date_start[0:4]
        else:        
           fy_seq_code = time.strftime('%Y')    
        return (s or '') % {
            'fy'  : fy_seq_code,
            'year':time.strftime('%Y'),
            'month': time.strftime('%m'),
            'day':time.strftime('%d'),
            'y': time.strftime('%y'),
            'doy': time.strftime('%j'),
            'woy': time.strftime('%W'),
            'weekday': time.strftime('%w'),
            'h24': time.strftime('%H'),
            'h12': time.strftime('%I'),
            'min': time.strftime('%M'),
            'sec': time.strftime('%S'),
        }

    # copy from bae/ir/sequence.py
    def get_id_base(self, cr, uid, sequence_id, test='id', context=None):
        assert test in ('code','id')
        company_id = self.pool.get('res.users').read(cr, uid, uid, ['company_id'], context=context)['company_id'][0] or None
        cr.execute('''SELECT id, number_next, prefix, suffix, padding
                      FROM ir_sequence
                      WHERE %s=%%s
                       AND active=true
                       AND (company_id = %%s or company_id is NULL)
                      ORDER BY company_id, id
                      FOR UPDATE NOWAIT''' % test,
                      (sequence_id, company_id))
        res = cr.dictfetchone()
        if not res:
            import sys         
            print >> sys.stderr,'missinf sequence ',sequence_id,company_id
            if isinstance(sequence_id,(str,unicode)):
                sequence_type_obj = self.pool.get('ir.sequence.type')
                sequence_type_id = sequence_type_obj.search(cr, uid, [('code','=',sequence_id)])
                for sequence_line in sequence_type_obj.browse(cr, uid, sequence_type_id):
                  prefix = ''
                  
                  # FIXME sequence name should be translated to produce nationalized abrevation
                  if sequence_line.create_sequence == 'none' :
                    continue 
                  if not sequence_line.prefix:
                    for w in sequence_line.name.split(' '):
                        prefix += w[0:1]
                    prefix += '-'
                  print 'create seq', company_id,prefix,sequence_line
                  new_seq_id = self.create(cr,uid,{
                   'code'   : sequence_id,
                   'name'   : sequence_line.name,
                   'active' : True,
                   'prefix' : prefix,
                   'suffice': '', 
                   'padding': 3,
                   'number_next' : 1,
                   'number_increment' : 1,
                   'company_id' : company_id,
                    }) ,
                  return self.get_id_base(cr, uid,new_seq_id,
                                                  test="id",
                                                  context=context)
 
            raise osv.except_osv(_('Integrity Error !'), _('Missing Sequence %s' % sequence_id))
        if res:
            cr.execute('UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s AND active=true', (res['id'],))
            if res['number_next']:
                import sys
                print >> sys.stderr, 'ir seq res', res
                return self._process_base(cr, uid,res['prefix'], context) + '%%0%sd' % res['padding'] % res['number_next'] + self._process_base(cr, uid,res['suffix'], context)
            else:
                return self._process_base(cr, uid,res['prefix'], context) + self._process_base(cr, uid,res['suffix'], context)
        return False

    # copy from account/sequence.py
    def get_id(self, cr, uid, sequence_id, test='id', context=None):
        import sys
        if context is None:
            context = {}
        company_id = context.get('company_id') or None
        journal_id = context.get('journal_id')
        fiscalyear_id = context.get('fiscalyear_id', False)
        journal_obj = self.pool.get('account.journal').browse(cr, uid, journal_id, context=None)
        cr.execute('select id from ir_sequence where '
                   + test + '=%s and active=%s', (sequence_id, True,))
        res = cr.dictfetchone()
        # FIXME - for now seq_id in journal is mandatory
        if not res:    
            if journal_obj.create_sequence != 'none':
                 res['id'] = self.create(cr,uid,{
                   'code'   : journal_obj.code,
                   'name'   : journal_obj.name,
                   'active' : True,
                   'prefix' : journal.code + '-',
                   'suffice': '',
                   'padding': 3,
                   'number_next' : 1,
                   'number_increment' : 1,
                   'company_id' : company_id,
               }) ,
                 journal_obj.write(cr,uid,{'sequence_id' : res['id']}) 
        print >> sys.stderr, 'seq res ',res, context
        if res:
            for line in self.browse(cr, uid, res['id'],
                                    context=context).fiscal_ids:
                print >> sys.stderr, 'seq line', line, fiscalyear_id
                if line.fiscalyear_id.id == fiscalyear_id:
                        print >> sys.stderr, 'seq fy id', line.sequence_id.id
                        return self.get_id_base(cr, uid,
                                                           line.sequence_id.id,
                                                           test="id",
                                                           context=context)
            if journal_obj.create_sequence == 'create_fy':
                    sequence_obj   = self.pool.get('ir.sequence').browse(cr, uid, sequence_id, context=None)
                    fiscalyear_obj = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id, context=None)
                    code_fy = fiscalyear_obj.sequence_code or fiscalyear_obj.date_start[0:4]
                    seq_fy_id = self.create(cr,uid,{
                      'code'   : sequence_obj.code ,
                      'name'   : journal_obj.name  + ' ' + code_fy,
                      'active' : True,
                      'prefix' : journal_obj.code + '-' + code_fy + '-',
                      'suffice': '',
                      'padding': 3,
                      'number_next' : 1,
                      'number_increment' : 1,
                      'company_id' : company_id,
                    })
                    seq_fy_obj = self.pool.get('account.sequence.fiscalyear')
                    seq_fy_rel_id = seq_fy_obj.create(cr,uid,{
                       'sequence_main_id' : sequence_id ,
                       'sequence_id'      : seq_fy_id,
                       'fiscalyear_id'    : fiscalyear_id,
                       })
                    return self.get_id_base(cr, uid,
                                                           seq_fy_id,
                                                           test="id",
                                                           context=context)
        print >> sys.stderr, 'seq id'
        return self.get_id_base(cr, uid, sequence_id, test,
                                               context=context)



ir_sequence()

#----------------------------------------------------------
# Entries Move - autogenerate of ir sequence
#----------------------------------------------------------
class account_move(osv.osv):
    _inherit = "account.move"


    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise osv.except_osv(_('Integrity Error !'), _('You cannot validate a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name =='/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id,'journal_id': move.journal_id.id}
                        print >>sys.stderr, 'context c ' ,c
                        new_name = obj_sequence.get_id(cr, uid, journal.sequence_id.id, context=c)
                    # FIXME
                    # some sequences are requested internaly but not defined 
                    # https://bugs.launchpad.net/bugs/737517    
                    #else:
                    #    raise osv.except_osv(_('Error'), _('No sequence defined on the journal !'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})

        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))

        return True

account_move()
