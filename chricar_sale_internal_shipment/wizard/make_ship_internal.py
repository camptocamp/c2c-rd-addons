# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import netsvc
import pooler
import sys

internal_shipment_form = """<?xml version="1.0"?>
<form string="Create internal shipment">
    <separator colspan="4" string="Do you really want to create an internal shipment?" />
    <field name="location_id" />
    <field name="location_dest_id" />
</form>
"""

internal_shipment_fields = {
    'location_id' : {'string':'Source Location', 'type':'many2one','relation':'stock.location','required':True , 'domain':"[('usage','=','internal')]"},
    'location_dest_id' : {'string':'Destination Location', 'type':'many2one','relation':'stock.location','required':True, 'domain':"[('usage','=','internal')]"}
}

ack_form = """<?xml version="1.0"?>
<form string="Create internal shipment">
    <separator string="Internal shipment created" />
</form>"""

ack_fields = {}

def _make_internal_shipment(self, cr, uid, data, context):
    order_obj = pooler.get_pool(cr.dbname).get('sale.order')
    internal='n'
    for o in order_obj.browse(cr, uid,  data['ids'] , context):
        saleid = o.id
        for i in o.picking_ids:
           if i.type== 'internal':
              internal = 'y'
    if internal == 'n':
        order_obj.action_ship_internal_create(cr, uid, data['ids'], data['form']['location_id'],data['form']['location_dest_id'])
    print >>sys.stderr, '_make_internal_shipment ',internal, data, context
    #for id in data['ids']:
    #    wf_service = netsvc.LocalService("workflow")
    #    wf_service.trg_validate(uid, 'sale.order', id, 'manual_internal_shipment', cr)
    pool = pooler.get_pool(cr.dbname)
    mod_obj = pool.get('ir.model.data')
    act_obj = pool.get('ir.actions.act_window')
    xml_id='action_picking_tree6'
    result = mod_obj._get_id(cr, uid, 'stock', xml_id)
    id = mod_obj.read(cr, uid, result, ['res_id'])['res_id']
    result = act_obj.read(cr, uid, id)
    result['domain'] = [('type','=','internal'),('sale_id','=', saleid)]
            
    return result

    #return {
    #    'domain': "[('id','in', ["+','.join(map(str,newinv))+"])]",
    #    'name': 'Invoices',
    #    'view_type': 'form',
    #    'view_mode': 'tree,form',
    #    'res_model': 'account.internal_shipment',
    #    'view_id': False,
    #    'context': "{'type':'out_refund'}",
    #    'type': 'ir.actions.act_window'
    #}
    #return {}

class make_internal_shipment(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : internal_shipment_form,
                    'fields' : internal_shipment_fields,
                    'state' : [('end', 'Cancel'),('internal_shipment', 'Create Internal Shipment') ]}
        },
        'internal_shipment' : {
            'actions' : [],
            'result' : {'type' : 'action',
                    'action' : _make_internal_shipment,
                    'state' : 'end'}
        },
    }
make_internal_shipment("sale.order.make_internal_shipment")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

