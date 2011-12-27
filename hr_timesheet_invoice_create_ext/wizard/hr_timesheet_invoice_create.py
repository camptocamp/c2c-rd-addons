# -*- coding: utf-8 -*-
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
import time
from osv import osv, fields
#
# TODO: check unit of measure !!!
#
class hr_timesheet_invoice_create(osv.osv_memory):

    _inherit = 'hr.timesheet.invoice.create'
    _columns = \
        { 'date_invoice' : fields.date
            ( 'Date Invoice'
            , help='The date of the invoice or emtpy will take the current day on validate'
            )
        , 'description'  : fields.char
            ( 'Prefix Invoice Text'
            , size=16
            , help='This text will be placed before the name of the analytic account instead of the current date'
            )
        , 'reference'    : fields.char
            ( 'Reference'
            , size=64
            , help='The reference on the invoice, usually the period of service'
            )
        }
    _defaults = {'description' : lambda *a: time.strftime('%d/%m/%Y')}

    def do_create(self, cr, uid, ids, context=None) :
        act_win = super(hr_timesheet_invoice_create, self).do_create(cr, uid, ids, context)
        data = self.read(cr, uid, ids, [], context=context)[0]
        line_obj = self.pool.get('account.analytic.line')
        inv_obj  = self.pool.get('account.invoice')

        inv_ids = line_obj.invoice_cost_create(cr, uid, context['active_ids'], data, context=context)
        for inv in inv_obj.browse(cr, uid, inv_ids) : 
            values = \
                { 'name'         : data['description'] + ' - ' + inv.invoice_line[0].account_analytic_id.name
                , 'date_invoice' : data['date_invoice'] or False
                , 'reference'    : data['reference'] or False
                }
            inv_obj.write(cr, uid, [inv.id], values)
        return act_win
    # end def do_create
hr_timesheet_invoice_create()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
