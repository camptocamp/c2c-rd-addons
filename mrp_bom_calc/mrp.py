# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com) All Rights Reserved.
# sinoj@zbeanztech.com
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
#
##############################################################################

from osv import fields
from osv import osv
#import ir
import decimal_precision as dp

import netsvc
import time
from tools import config

class mrp_bom(osv.osv):
    _name = 'mrp.bom'
    _inherit='mrp.bom'

    def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
        if product_id:
            prod=self.pool.get('product.product').browse(cr,uid,[product_id])[0]
            v = {'product_uom':prod.uom_id.id}
            v['standard_price']=prod.product_tmpl_id.standard_price
            # FIX ME standard_price_coeff is stored in product or template ?
            # Have to fix this later -> must go into template
            if 'standard_price_coeff' in prod._columns :
                    v['standard_price_coeff']=prod.standard_price_coeff
            if 'price_unit_id' in prod._columns :
                v['price_unit_id']=prod.price_unit_id.id
            if not name:
                v['name'] = prod.name
            return {'value': v}
        return {}
    def onchange_routing_id(self, cr, uid, ids, routing_id,context=None):
        if routing_id:
            cost_routing=0
            routing_obj=self.pool.get('mrp.routing').browse(cr,uid,[routing_id])[0]
            for workcentre_line in routing_obj.workcenter_lines :
                cost_routing=cost_routing+workcentre_line.hour_nbr*workcentre_line.workcenter_id.costs_hour + workcentre_line.cycle_nbr*workcentre_line.workcenter_id.costs_cycle
            v = {'cost_routing':cost_routing}

            return {'value': v}
        return {}

    def _child_compute(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for bom in self.browse(cr, uid, ids, context=context):
            result[bom.id] = map(lambda x: x.id, bom.bom_lines)
            if bom.bom_lines:
                if bom.mapping :
                    org_ids=self.pool.get('mrp.bom').search(cr, uid, [('mapping','=',False),('state','=','confirm'),('bom_id','=',False),('product_id','=',bom.product_id.id)])
                    if org_ids :
                        org_obj=self.pool.get('mrp.bom').browse(cr, uid, org_ids[0], context=context)
                        cr.execute("select greatest(write_date,create_date) from mrp_bom where id in (%s)" % (org_ids[0]))
                        res =cr.fetchone()
                        if bom.last_modified_date != res[0] :
                            for unlink_line in bom.bom_lines :
                                self.pool.get('mrp.bom').unlink(cr, uid, unlink_line.id)
                            for bom_line in org_obj.bom_lines :
                                self.pool.get('mrp.bom').create(cr, uid, {
                                    'product_id': bom_line.product_id.id,
                                    'product_uom':bom_line.product_uom.id,
                                    'name': bom_line.name,
                                    'standard_price':bom_line.standard_price,
                                    'standard_price_coeff':bom_line.standard_price_coeff,
                                    'cost_routing':bom_line.cost_routing,
                                    'product_qty':bom_line.product_qty,
                                    'bom_id':bom.id,
                                    'mapping':True,
                                    'last_modified_date':res[0],

                                    }, context=context)

                            data=self.browse(cr, uid, bom.id, context=context)
                            result[bom.id] = map(lambda x: x.id, data.bom_lines)
                    else :
                        for unlink_line in bom.bom_lines :
                            self.pool.get('mrp.bom').unlink(cr, uid, unlink_line.id)
                        data=self.browse(cr, uid, bom.id, context=context)
                        result[bom.id] = map(lambda x: x.id, data.bom_lines)
                else :
                    button_name=''
                    for bom_state_line in bom.bom_lines :
                        if bom_state_line.state == 'expire' or  bom_state_line.state == 'invalid' :
                            button_name= 'wkf_'+bom_state_line.state

                    if button_name :
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'mrp.bom', bom.id, button_name, cr)
                    data=self.browse(cr, uid, bom.id, context=context)
                    result[bom.id] = map(lambda x: x.id, data.bom_lines)

                continue
            ok = ((name=='child_complete_ids') and (bom.product_id.supply_method=='produce'))
            if bom.type=='phantom' or ok:
                sids = self.pool.get('mrp.bom').search(cr, uid, [('mapping','=',False),('bom_id','=',False),('state','=','confirm'),('product_id','=',bom.product_id.id)])
                if sids :
                    bom2 = self.pool.get('mrp.bom').browse(cr, uid, sids[0], context=context)
                    cr.execute("select greatest(write_date,create_date) from mrp_bom where id in (%s)" % (sids[0]))
                    res =cr.fetchone()
                    for bom2_line in bom2.bom_lines :
                        self.pool.get('mrp.bom').create(cr, uid, {
                            'product_id': bom2_line.product_id.id,
                            'product_uom':bom2_line.product_uom.id,
                            'name': bom2_line.name,
                            'standard_price': bom2_line.standard_price,
                            'standard_price_coeff': bom2_line.standard_price_coeff,
                            'cost_routing':bom2_line.cost_routing,
                            'product_qty':bom2_line.product_qty,
                            'bom_id':bom.id,
                            'mapping':True,
                            'last_modified_date':res[0],

                        }, context=context)
                    self.pool.get('mrp.bom').write(cr,uid,bom.id,{
                           'mapping':True,
                           'last_modified_date':res[0],
                            })
                    data=self.browse(cr, uid, bom.id, context=context)
                    result[bom.id] = map(lambda x: x.id, data.bom_lines)
                    continue
        return result

    def _quantity_cum_calc(self, cr, uid, id):
        mrp_bom_obj=self.pool.get('mrp.bom')
        bom=self.browse(cr, uid, id)
        coeff=bom.price_unit_id.coefficient
        if not coeff or coeff == 0.0:
            coeff=1
        if bom.bom_id:
            value=bom.product_qty / bom.bom_id.product_bom_qty * mrp_bom_obj._quantity_cum_calc(cr, uid,bom.bom_id.id )
        else :
            value=bom.product_qty / bom.product_bom_qty

        return value


    def quantity_cum_calc(self, cr, uid, ids,value,name, arg, context=None):
        result = {}
        mrp_bom_obj=self.pool.get('mrp.bom')
        for bom in self.browse(cr, uid, ids, context=context):
            result[bom.id]=mrp_bom_obj._quantity_cum_calc(cr,uid,bom.id)
        return result

    def standard_price_subtotal_calc(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for bom in self.browse(cr, uid, ids, context=context):
            coeff=bom.price_unit_id.coefficient
            if not coeff or coeff == 0.0:
               coeff=1
            result[bom.id]=bom.standard_price_coeff*bom.product_qty/coeff
        return result

    def standard_price_subtotal_cum_calc(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for bom in self.browse(cr, uid, ids, context=context):
            coeff=bom.price_unit_id.coefficient
            if not coeff or coeff == 0.0:
               coeff=1
            result[bom.id]=bom.product_qty_explode*bom.standard_price_coeff/coeff
        return result

    def _value_cum_calc(self, cr, uid, id):
        mrp_bom_obj=self.pool.get('mrp.bom')
        bom=self.browse(cr, uid, id)
        value=0
        for bom_line in bom.bom_lines:
            value=value +mrp_bom_obj._value_cum_calc(cr,uid,bom_line.id)

        value=value + bom.standard_price_subtotal_explode + bom.cost_routing_bom

        return value
    def value_bom_cum_calc(self, cr, uid, ids, name, arg, context=None):
        result = {}
        mrp_bom_obj=self.pool.get('mrp.bom')
        for bom in self.browse(cr, uid, ids, context=context):
            value=mrp_bom_obj._value_cum_calc(cr,uid,bom.id)
            result[bom.id]=value - bom.cost_routing_bom

        return result
    def cost_routing_bom_calc(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for bom in self.browse(cr, uid, ids, context=context):
            result[bom.id]=bom.product_qty / bom.product_bom_qty * bom.cost_routing
        return result

    def _total_cost_calc(self, cr, uid, id):
        mrp_bom_obj=self.pool.get('mrp.bom')
        bom=self.browse(cr, uid, id)
        value=0
        for bom_line in bom.bom_lines:
            value=value +mrp_bom_obj._total_cost_calc(cr,uid,bom_line.id)

        value=value + bom.standard_price_subtotal_explode + bom.cost_routing_bom
        return value

    def total_cost_calc(self, cr, uid, ids, name, arg, context=None):
        result = {}
        mrp_bom_obj=self.pool.get('mrp.bom')
        for bom in self.browse(cr, uid, ids, context=context):
            result[bom.id]=mrp_bom_obj._total_cost_calc(cr,uid,bom.id)
        return result

    _columns={
        'name': fields.char('Name', size=64, required=True,readonly=True, states={'draft': [('readonly', False)]}),
        'code': fields.char('Code', size=16, readonly=True,states={'draft': [('readonly', False)]}),
        'active': fields.boolean('Active', readonly=True,states={'draft': [('readonly', False)]}),
        'type': fields.selection([('normal','Normal BoM'),('phantom','Sets / Phantom')], 'BoM Type', required=True, help=
            "Use a phantom bill of material in raw materials lines that have to be " \
            "automatically computed in on eproduction order and not one per level." \
            "If you put \"Phantom/Set\" at the root level of a bill of material " \
            "it is considered as a set or pack: the products are replaced by the components " \
            "between the sale order to the picking without going through the production order." \
            "The normal BoM will generate one production order per BoM level.", readonly=True,states={'draft': [('readonly', False)]}),
        'date_start': fields.date('Valid From', help="Validity of this BoM or component. Keep empty if it's always valid.",readonly=True, states={'draft': [('readonly', False)]}),
        'date_stop': fields.date('Valid Until', help="Validity of this BoM or component. Keep empty if it's always valid.",readonly=True, states={'draft': [('readonly', False)]}),
        'sequence': fields.integer('Sequence', readonly=True,states={'draft': [('readonly', False)]}),
        'position': fields.char('Internal Ref.', size=64, help="Reference to a position in an external plan.",readonly=True, states={'draft': [('readonly', False)]}),
        'product_id': fields.many2one('product.product', 'Product',required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_qty': fields.float('Product Qty', required=True,readonly=True, states={'draft': [('readonly', False)]}, help="Units needed to produce the parent product" ),
        'product_bom_qty': fields.float('Bom Qty', required=True,readonly=True, states={'draft': [('readonly', False)]} , help="Units produced by this BOM (factor for child products)"),'product_uos': fields.many2one('product.uom', 'Product UOS', readonly=True,states={'draft': [('readonly', False)]}),
        'product_qty_explode': fields.float('Cum Qty', required=True,readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', 'Product UOM', required=True,readonly=True, states={'draft': [('readonly', False)]}),
        'product_rounding': fields.float('Product Rounding', help="Rounding applied on the product quantity. For integer only values, put 1.0",readonly=True, states={'draft': [('readonly', False)]}),
        'product_efficiency': fields.float('Product Efficiency', required=True, help="Efficiency on the production. A factor of 0.9 means a loss of 10% in the production.", readonly=True,states={'draft': [('readonly', False)]}),
        'price_unit_id'       :fields.many2one('c2c_product.price_unit','Price Unit' ,states={'draft': [('readonly', False)]}),
        'standard_price_coeff':fields.float(string='Standard Price/Coeff',digits=(16,8)),
        'bom_lines': fields.one2many('mrp.bom', 'bom_id', 'BoM Lines',readonly=True, states={'draft': [('readonly', False)]}),
        'bom_id': fields.many2one('mrp.bom', 'Parent BoM', ondelete='cascade', select=True,readonly=True, states={'draft': [('readonly', False)]}),
        'routing_id': fields.many2one('mrp.routing', 'Routing', help="The list of operations (list of workcenters) to produce the finished product. The routing is mainly used to compute workcenter costs during operations and to plan futur loads on workcenters based on production plannification.", readonly=True,states={'draft': [('readonly', False)]}),
        'property_ids': fields.many2many('mrp.property', 'mrp_bom_property_rel', 'bom_id','property_id', 'Properties', readonly=True,states={'draft': [('readonly', False)]}),
        'revision_ids': fields.one2many('mrp.bom.revision', 'bom_id', 'BoM Revisions',readonly=True, states={'draft': [('readonly', False)]}),
        'revision_type': fields.selection([('numeric','numeric indices'),('alpha','alphabetical indices')], 'indice type',readonly=True, states={'draft': [('readonly', False)]}),
        'child_ids': fields.function(_child_compute,relation='mrp.bom', method=True, string="BoM Hyerarchy", type='many2many',readonly=True, states={'draft': [('readonly', False)]}),
        'child_complete_ids': fields.function(_child_compute,relation='mrp.bom', method=True, string="BoM Hyerarchy", type='many2many',readonly=True, states={'draft': [('readonly', False)]}),

        'version_no':fields.integer('Version Number', readonly=True,states={'draft': [('readonly', False)]}),
        #'cost_price':fields.float('cost Price',readonly=True, states={'draft': [('readonly', False)]}),
        'standard_price': fields.float('Cost Price',  digits_compute=dp.get_precision('Purchase Price'), help="The cost of the product for BOM valuation. Especially usefull for new products.",readonly=True, states={'draft': [('readonly', False)]}),
        'standard_price_subtotal':fields.function(standard_price_subtotal_calc, method=True, type='float',string='Value', help="The cost of the product for BOM valuation. "),'product_qty_explode':fields.function(quantity_cum_calc, method=True, type='float',string='Cost Subtotal'),
        'standard_price_subtotal_explode':fields.function(standard_price_subtotal_cum_calc, method=True,type='float',string='Value BOM',help="Total Cost for the exploded BOM" ),
        'value_bom_cum':fields.function(value_bom_cum_calc, method=True,type='float',string='Value BOM Cum'),
        'cost_routing':fields.float('cost Routing', readonly=True,states={'draft': [('readonly', False)]}),
        'cost_routing_bom':fields.function(cost_routing_bom_calc, method=True, type='float',string='cost Routing BOM'),
        'total':fields.function(total_cost_calc, method=True, type='float',string='Total Cost'),
        'mapping' : fields.boolean('mapping', states={'draft': [('readonly', False)]}),
        'last_modified_date': fields.datetime('modification time' ,readonly=True),
        'state': fields.selection([('draft','Draft'),
                                   ('verify','To Be Confirm'),
                                   ('confirm','Confirmed'),
                                   ('invalid','Invalid'),
                                   ('expire','Expired')], 'state',readonly=True),

    }
    _defaults = {
        'state'          : lambda *args: 'draft',
        'version_no'     : lambda *args: 1,
        'product_bom_qty': lambda *args: 1,
    }
    def wkf_action_draft_verify(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state':'verify'}, context=None)
        return True

    def wkf_action_verify_confirm(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state':'confirm'}, context=None)
        return True

    def wkf_action_confirm_invalid(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state':'invalid'}, context=None)
        return True

    def wkf_action_confirm_draft(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state':'draft'}, context=None)
        return True

    def wkf_action_confirm_expire(self, cr, uid, ids):
        self.write(cr, uid, ids, {'state':'expire'}, context=None)
        return True

    def action_version(self, cr, uid, ids, *args):
        for bom in self.browse(cr, uid, ids):
            temp_id = self.copy(cr, uid, bom.id, {'version_no': bom.version_no + 1})
        return True

    def action_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'}, context=None)
        wf_service = netsvc.LocalService("workflow")
        for bom_id in ids:
            wf_service.trg_delete(uid, 'mrp.bom', bom_id, cr)
            wf_service.trg_create(uid, 'mrp.bom', bom_id, cr)
        return True

    def wkf_check_confirmed_bom(self, cr, uid, ids):
        for bom in self.browse(cr, uid, ids):
            if not bom.bom_id :
                bom_ids=self.pool.get('mrp.bom').search(cr, uid, [('mapping','=',False),('bom_id','=',False),('state','=','confirm'),('product_id','=',bom.product_id.id)])
                if bom_ids :
                    raise osv.except_osv("Already Done", 'The BOM of product: "%s"  already Confirmed' % bom.product_id.name)
                    return False
        return True
mrp_bom()

#class mrp_routing(osv.osv):
#    _name = 'mrp.routing'
#    _inherit='mrp.routing'
#    _columns={
#        'cost_routing':fields.float('cost Routing'),
#        }
#mrp_routing()
