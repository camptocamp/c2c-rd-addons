# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution        
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import time
from openerp.tools.translate import _

period_form = '''<?xml version="1.0"?>
<form string="Invoice List">
    <field name="company_id"/>
    <newline/>
    <group colspan="4">
        <separator string="Filter by type" colspan="4"/>
        <field name="out_invoice"/>
        <field name="out_refund"/>
        <field name="in_invoice"/>
        <field name="in_refund"/>
    </group>
    <group colspan="4">
        <separator string="Filter by state" colspan="4"/>
        <field name="draft"/>
        <field name="proforma"/>
        <field name="open"/>
        <field name="paid"/>
        <field name="cancel"/>
    </group>
    <group colspan="4">
        <separator string="Filter by date (default current year)" colspan="4"/>
        <field name="state" required="True"/>
        <newline/>
        <group attrs="{'invisible':[('state','=','none')]}" colspan="4">
            <group attrs="{'invisible':[('state','=','byperiod')]}" colspan="4">
                <separator string="Date Filter" colspan="4"/>
                <field name="date_from"/>
                <field name="date_to"/>
            </group>
            <group attrs="{'invisible':[('state','=','bydate')]}" colspan="4">
                <separator string="Filter on Periods" colspan="4"/>
                <field name="periods" colspan="4" nolabel="1"/>
            </group>
        </group>
    </group>
    <group colspan="4">
        <separator string="Options" colspan="4"/>
        <field name="detailed_taxes" required="False"/>
        <field name="order_by" required="True"/>
    </group>
</form>'''

period_fields = {
    'company_id': {'string': 'Company', 'type': 'many2one', 'relation': 'res.company', 'required': True},
    'out_invoice': {'string':'Customer invoices', 'type':'boolean', 'default': lambda *a: True},
    'out_refund': {'string':'Customer refunds', 'type':'boolean', 'default': lambda *a: True},
    'in_invoice': {'string':'Supplier invoices', 'type':'boolean', 'default': lambda *a: True},
    'in_refund': {'string':'Supplier refunds', 'type':'boolean', 'default': lambda *a: True},
    'draft': {'string':'Draft', 'type':'boolean',},
    'proforma': {'string':'Pro-forma', 'type':'boolean',},
    'open': {'string':'Open', 'type':'boolean', 'default': lambda *a: True},
    'paid': {'string':'Done', 'type':'boolean', 'default': lambda *a: True},
    'cancel': {'string':'Cancelled', 'type':'boolean',},
    'detailed_taxes': {'string':'Detailed taxes', 'type':'boolean',},
    'state':{
        'string':"Date/Period Filter",
        'type':'selection',
        'selection':[('bydate','By Date'),('byperiod','By Period'),('all','By Date and Period'),('none','No Filter')],
        'default': lambda *a:'none'
    },
    'periods': {'string': 'Periods', 'type': 'many2many', 'relation': 'account.period', 'help': 'All periods if empty'},
    'date_from': {'string':"Start date",'type':'date','required':True ,'default': lambda *a: time.strftime('%Y-01-01')},
    'date_to': {'string':"End date",'type':'date','required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'order_by': {'string': 'Order by', 'type': 'selection', 'selection': [('number','Number'),('date','Date'),('partner','Partner')], 'default': lambda *a: 'number'},
}



class wizard_report(wizard.interface):
    def _get_defaults(self, cr, uid, data, context={}):
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
           company_id = user.company_id.id
        else:
           company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
        data['form']['context'] = context
        return data['form']


    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':period_form, 'fields':period_fields, 'state':[('end','Cancel','gtk-cancel'),('report','Print','gtk-print')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'account.invoice.list.report', 'state':'end'}
        }
    }
wizard_report('account.invoice.list.report')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
