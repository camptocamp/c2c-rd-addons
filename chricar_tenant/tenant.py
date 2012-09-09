# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-07-09 18:08:09+02
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
import time
from osv import fields,osv
import pooler

class chricar_tenant(osv.osv):
     _name = "chricar.tenant"

     def _price_per_m2(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for tenant in self.browse(cr, uid, ids, context):
             lease   = tenant.lease
             surface = tenant.top_id.surface
             result[tenant.id] = 0.0
             if surface and surface > 0.0:
                #print lease / surface
                result[tenant.id] = lease / surface
         return result

     def _dirname(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for dirname in self.browse(cr, uid, ids, context):
             result[dirname.id] = str(dirname.name) + ' ' + dirname.partner_id.name
         return result

     def _get_state(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for tenant in self.browse(cr, uid, ids, context):
             result[tenant.id] = 'past'
             today = time.strftime('%Y-%m-%d')
             if tenant.name <= today and  ( not tenant.to_date  or tenant.to_date >= today):
                 result[tenant.id] = 'current'
             if tenant.name > today:
                 result[tenant.id] = 'future'    
                 
         return result

     _columns = {
       'contract'           : fields.char    ('Contract ', size=64),
       'date_contract'      : fields.date    ('Contract Date'),
       'lease'              : fields.float   ('Lease monthly', digits=(8,2)),
       'limited'            : fields.boolean ('Limited'),
       'name'               : fields.date    ('From Date', required=True, help="Date Contract Starts",),
       'note'               : fields.text    ('Notes'),
       'notice_period'      : fields.integer ('Notice Period Month', help="Notice period in month"),
       'termination_date'   : fields.selection([('month','Month End'),('quater','Quater End')], 'Termination Date',  size=24),
       'partner_id'         : fields.many2one('res.partner','Tenant', select=True, required=True),
       'price'              : fields.function(_price_per_m2, method=True, string=u"Price / m²", type='float', digits=(16,2),),
       'sort'               : fields.related ('top_id', 'sort', tpye ='integer', relation='chricar.top', string="Sort", readonly = True),
       'surface'            : fields.related ('top_id', 'surface', tpye ='float', relation='chricar.top', string="Surface", readonly = True),   
       'to_date'            : fields.date    ('To Date', help="Date Contract Ends"),
       'top_id'             : fields.many2one('chricar.top','Top', select=True, required=True),
       'location_id'        : fields.related ('top_id','location_id',type='many2one', relation='stock.location', string="Location", readonly = True ),
       'waiver_of_termination': fields.integer  ('Waiver of Termination', help="Duration in month bofore the tenant can terminate the lease" ),
       'lease_free'         : fields.integer  ('Initial free month', help="Duration in month the tenant does not pay rent" ),
       #'dirname'            : fields.function(_dirname, method=True, string="Dirname",type='char',size=128, store=True),
       'state'              : fields.function(_get_state, method=True, string='Status', type='char', readonly=True),
       'ref_top'            : fields.related ('top_id', 'ref_top', type ='char', relation='chricar.top', string="Ref Top", readonly = True),   
    }

     _defaults = {
       
    }

     _order = "name desc"

     def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
         super(chricar_tenant, self).name_search(cr, user, name, args, operator='=', context=context, limit=limit)

chricar_tenant()

#*************************************************************Y
class chricar_top(osv.osv):
#*************************************************************Y
      _inherit = "chricar.top"
      _columns = {
          'tenant_ids': fields.one2many('chricar.tenant','top_id','Tenant'),
      }
chricar_top()
class res_partner(osv.osv):
      _inherit = "res.partner"
      _columns = {
          'tenant_ids': fields.one2many('chricar.tenant','partner_id','Tenant'),
      }
res_partner()


class chricar_top(osv.osv):
     _inherit = "chricar.top"

     def _lease_current_m2(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         price = 0.0
         for p in self.browse(cr, uid, ids, context):
             now = time.strftime('%Y-%m-%d %H:%M:%S')
             tenant_obj = self.pool.get('chricar.tenant')
             tenant_ids = tenant_obj.search(cr,uid,['|',('to_date','=',False),('to_date','>',now),('name','<=',now),('top_id','=',p.id)])
             for lease in tenant_obj.browse(cr, uid, tenant_ids,context):
                 price  = lease.price
             result[p.id] = price
         return result

     def _lease_current(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for p in self.browse(cr, uid, ids, context):
             now = time.strftime('%Y-%m-%d %H:%M:%S')
             tenant_obj = self.pool.get('chricar.tenant')
             tenant_ids = tenant_obj.search(cr,uid,['|',('to_date','=',False),('to_date','>',now),('name','<=',now),('top_id','=',p.id)])
             lease_cur = 0.0
             for lease in tenant_obj.browse(cr, uid, tenant_ids,context):
                 lease_cur = lease.lease
             result[p.id] = lease_cur
         return result

     def _lease_potential(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         potential = 0.0
         for p in self.browse(cr, uid, ids, context):
             now = time.strftime('%Y-%m-%d %H:%M:%S')
             tenant_obj = self.pool.get('chricar.tenant')
             tenant_ids = tenant_obj.search(cr,uid,['|',('to_date','=',False),('to_date','>',now),('name','<=',now),('top_id','=',p.id)])
             price = 0.0
             for lease in tenant_obj.browse(cr, uid, tenant_ids,context):
                 price = lease.price
             potential = 0.0
             if p.lease_target and p.surface:
                 potential = p.surface * (p.lease_target - price)
             if not p.surface and p.lease_target:
                 potential = round(p.lease_target - p.lease_current,0)
             result[p.id] = potential
         return result

     def _tenant_current(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for p in self.browse(cr, uid, ids, context):
             partner_id = False
             now = time.strftime('%Y-%m-%d %H:%M:%S')
             tenant_obj = self.pool.get('chricar.tenant')
             tenant_ids = tenant_obj.search(cr,uid,['|',('to_date','=',False),('to_date','>',now),('name','<=',now),('top_id','=',p.id)])
             if tenant_ids:
                 for lease in tenant_obj.browse(cr, uid, tenant_ids,context):
                     partner_id = lease.partner_id.id
             if not partner_id:
                 tenant_ids = tenant_obj.search(cr,uid,[('name','>',now),('top_id','=',p.id)])
                 if tenant_ids:
                    for lease in tenant_obj.browse(cr, uid, tenant_ids,context):
                       partner_id = lease.partner_id.id
             result[p.id] = partner_id
         return result

     _columns = {
     'lease_current'      : fields.function(_lease_current, method=True, string="Current Lease",type='float',digits=(16,0)),
     'lease_current_m2'   : fields.function(_lease_current_m2, method=True, string="Current/m²",type='float',digits=(16,2)),
     'lease_potential'    : fields.function(_lease_potential, method=True, string="Potential Lease",type='float',digits=(16,0)),
     'tenant_id'          : fields.function(_tenant_current, method=True, type='many2one', relation='res.partner', string='Tenant' ),
     #'tenant_id'          : fields.function(_tenant_current, method=True, string='Tenant',type='char', size=128 ),
     }
chricar_top()
