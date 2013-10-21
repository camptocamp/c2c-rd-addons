
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from tools.translate import _

class account_change_date(osv.osv_memory):
    _name = 'account.change.date'
    _description = 'Change Date Period'
    _columns = {
       'date'      : fields.date    ('New Date', required=True),
       'period_id' : fields.many2one('account.period', 'Period', required=True),
    }

    def view_init(self, cr , uid , fields_list, context=None):
        obj_inv = self.pool.get('account.invoice')
        if context is None:
            context = {}


    def onchange_date(self, cr, uid, ids, date, context=None):
        """ On change of Date Compute Pierod.
        
        @param date: Invoice Date
        @return: period ID
        """
        obj_period = self.pool.get('account.period')
        
        res = {}
        if date:            
            period_ids = obj_period.search(cr,uid,[('date_start','<=',date), ('date_stop','>=',date), ('state','=','draft'), ('special', '!=', True) ], context)
            if period_ids:
                res['value'] = {'period_id' : period_ids[0]}
            else:
                raise osv.except_osv(_('Error'), _('You can not set a date in a closed period !'))
  
        return res

    def change_date(self, cr, uid, ids, context=None):
        obj_inv = self.pool.get('account.invoice')
        obj_move = self.pool.get('account.move')
        obj_move_line = self.pool.get('account.move.line')
        #obj_inv_line = self.pool.get('account.invoice.line')
        obj_period = self.pool.get('account.period')
        attachment_obj = self.pool.get('ir.attachment')
        report_xml_obj = self.pool.get('ir.actions.report.xml')
        
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        new_date = data.date
        new_period_id = data.period_id.id
        
        invoice = obj_inv.browse(cr, uid, context['active_id'], context=context)
        if invoice.period_id.id == new_period_id and invoice.date_invoice == new_date: 
            return {}
        
        obj_inv.write(cr, uid, [invoice.id], {'date_invoice': new_date, 'period_id': new_period_id}, context=context)
        obj_move._compute_sum(cr, uid, [invoice.move_id.id] , sign='-')
        obj_move.write(cr, uid, [invoice.move_id.id], {'date': new_date, 'period_id': new_period_id}, context=context)
        obj_move._compute_sum(cr, uid, [invoice.move_id.id] , sign='+')
        #line_ids = []
        #for l in invoice.move_id.line_id:
        #    line_ids.append(l.id)
        #obj_move_line.write(cr, uid, line_ids, {'period_id': new_period_id}, context=context)

        report_ids = report_xml_obj.search(cr, uid, [('model','=', 'account.invoice'), ('attachment','!=', False)])
        for report in report_xml_obj.browse(cr, uid, report_ids):
            if report.attachment:
                aname = report.attachment.replace('object','invoice')
                if eval(aname):
                    aname = eval(aname)+'.pdf'
                    attachment_ids = attachment_obj.search(cr, uid, [('res_model','=','account.invoice'),('datas_fname', '=', aname),('res_id','=',invoice.id)])
                    attachment_obj.unlink(cr, uid, attachment_ids )

        
        return {'type': 'ir.actions.act_window_close'}

account_change_date()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

