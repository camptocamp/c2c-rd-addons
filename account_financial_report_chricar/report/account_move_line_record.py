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


import time
from openerp.report import report_sxw

#
# Use period and Journal for selection of resources
#
class journal_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(journal_print, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
        })

    def set_context(self, objects, data, ids, report_type = None):
        if data['model'] == 'ir.ui.menu':
            period_ids = data['form']['period_ids'][0][2]
            journal_ids = data['form']['journal_ids'][0][2]
            periods = ','.join([str(id) for id in period_ids])
            journals = ','.join([str(id) for id in journal_ids])
            self.cr.execute('select id from account_move where period_id in ('+ periods +') and journal_id in ('+ journals +') and state!=\'draft\' order by ('+ data['form']['sort_selection'] +'),id')
            move_ids = map(lambda x: x[0], self.cr.fetchall())
        else:
            move_ids = []
            journalperiods = self.pool.get('account.journal.period').browse(self.cr, self.uid, ids)
            for jp in journalperiods:
                self.cr.execute('select id from account_move where period_id=\'%s\' and journal_id=\'%s\' and state!=\'draft\' order by date,id' % (jp.period_id.id, jp.journal_id.id))
                move_ids.extend(map(lambda x: x[0], self.cr.fetchall()))

        objects = self.pool.get('account.move').browse(self.cr, self.uid, move_ids)
        super(journal_print, self).set_context(objects, data, ids, report_type)


report_sxw.report_sxw('report.account.print.journal.entries', 'account.journal.period', 'addons/account_financial_report_chricar/report/account_move_line_record.rml', parser=journal_print, header=False)
report_sxw.report_sxw('report.account.print.journal.entriesh', 'account.journal.period', 'addons/account_financial_report_chricar/report/account_move_line_record_h.rml', parser=journal_print, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

