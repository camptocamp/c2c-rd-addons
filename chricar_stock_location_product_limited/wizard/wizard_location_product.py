# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution        
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

#import wizard
#import pooler
import time

def _action_open_window(self, cr, uid, data, context=None): 
    c={'location': data['ids'][0],'from_date':data['form']['from_date'],'to_date':data['form']['to_date']}
    product_obj = pooler.get_pool(cr.dbname).get('product.product')
    ids = product_obj.search(cr, uid, [('type','!=','service')],context=c)
    if not data['form']['display_with_zero_qty']:          
        products = product_obj.read(cr, uid, ids, ['id', 'qty_available','virtual_available'], context=c)
        ids=[]
        for product in products:
            if (product['qty_available']!=0) or (product['virtual_available']!=0): ids.append(product['id'])
    return {
        'name': False,
        'view_type': 'form',
        "view_mode": 'tree,form',
        'res_model': 'product.product',
        'type': 'ir.actions.act_window',
        'context': c,
        'domain':[('id','in',ids)]
    }


class product_by_location(wizard.interface):
    form1 = '''<?xml version="1.0"?>
    <form string="View Stock of Products">
        <separator string="Stock Location Analysis" colspan="4"/>
        <field name="from_date"/>
        <newline/>
        <field name="to_date"/>
        <newline/>
        <label string=""/>
        <label string="(Keep empty to open the current situation)" align="0.0" colspan="3"/> 
        <newline/>
        <separator colspan="4"/>
        <field name="display_with_zero_qty"/>      
    </form>'''
    form1_fields = {
             'from_date': {
                'string': 'From',
                'type': 'date',
        },
             'to_date': {
                'string': 'To',
                'type': 'date',
        },
            'display_with_zero_qty': {
                'string': 'Display products with 0 qty',
                'type': 'boolean',                
        },
    }

    states = {
      'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':form1, 'fields':form1_fields, 'state': [('end', 'Cancel','gtk-cancel'),('open', 'Open Products','gtk-ok')]}
        },
    'open': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_window, 'state':'end'}
        }
    }
product_by_location('stock.location.products.modified')
