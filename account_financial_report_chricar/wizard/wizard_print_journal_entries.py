# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution        
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
#import pooler
from openerp.tools.translate import _

form = '''<?xml version="1.0"?>
<form string="Print Journal">
    <field name="journal_ids"/>
    <field name="period_ids"/>
    <field name="sort_selection"/>
    <field name="landscape"/>
</form>'''

fields = {
  'journal_ids': {'string': 'Journal', 'type': 'many2many', 'relation': 'account.journal', 'required': True},
  'period_ids': {'string': 'Period', 'type': 'many2many', 'relation': 'account.period', 'required': True},
  'sort_selection': {
        'string':"Entries Sorted By",
        'type':'selection',
        'selection':[('date','By date'),("to_number(name,'999999999')",'By entry number'),('ref','By reference number')],
        'required':True,
        'default': lambda *a: 'date',
    },
    'landscape': {'string':"Landscape Mode",'type':'boolean'},
}


class wizard_print_journal(wizard.interface):

    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        period_obj = pooler.get_pool(cr.dbname).get('account.period')
        journal_obj = pooler.get_pool(cr.dbname).get('account.journal')
        data['form']['period_ids'] = period_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_obj.find(cr, uid))])
        data['form']['journal_ids'] = journal_obj.search(cr, uid, [])
        return data['form']


    def _check_data(self, cr, uid, data, *args):
        period_id = data['form']['period_ids'][0][2]
        journal_id = data['form']['journal_ids'][0][2]

        if type(period_id)==type([]):

            ids_final = []
            for journal in journal_id:
                for period in period_id:
                    ids_journal_period = pooler.get_pool(cr.dbname).get('account.journal.period').search(cr,uid, [('journal_id','=',journal),('period_id','=',period)])

                    if ids_journal_period:
                        ids_final.append(ids_journal_period)

            if not ids_final:
                raise wizard.except_wizard(_('No Data Available'), _('No records found for your selection!'))
        return data['form']


    def _check(self, cr, uid, data, context):
        if data['form']['landscape']==True:
            return 'report_landscape'
        else:
            return 'report'


    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': (('end', 'Cancel'), ('print', 'Print'))},
        },
        'print': {
            'actions': [_check_data],
            'result': {'type':'choice','next_state':_check}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'account.print.journal.entries', 'state':'end'}
        },
        'report_landscape': {
            'actions': [],
            'result': {'type':'print', 'report':'account.print.journal.entriesh', 'state':'end'}
        },
    }
wizard_print_journal('account.journal.entries.report')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

