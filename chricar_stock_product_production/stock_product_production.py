# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-09-19 23:51:03+02
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
from openerp.osv import fields,osv

class chricar_product_move_by_production_location(osv.osv):
    _name = "chricar.product_move_by_production_location"
    _description = "Product moves by production location"
    _auto = False
    _columns = \
        { 'id'            : fields.char    ('id',size=16, readonly=True)
        , 'location_id'   : fields.many2one('stock.location','Location', select=True, required=True)
        , 'product_id'    : fields.many2one('product.product','Product', select=True, required=True)
        , 'name'          : fields.float   ('Quantity', digits=(16,2))
        , 'amount'        : fields.float   ('Amount', digits=(16,2))
        , 'date_planned'  : fields.many2one('product.product','Product', select=True, required=True)
        , 'period_id'     : fields.many2one('account.period','Period', select=True, required=True)
        , 'fiscalyear_id' : fields.many2one('account.fiscalyear','Year', select=True, required=True)
        , 'used'          : fields.char    ('Usage',size=16, readonly=True)
        , 'capacity'      : fields.float   ('Capacity',type='float', help="Defines the capacity of the location")
        }

    def init(self, cr):
        cr.execute("""
DROP SEQUENCE IF EXISTS chricar_product_move_by_production_location_id_seq CASCADE;
CREATE SEQUENCE chricar_product_move_by_production_location_id_seq;
create or replace view chricar_product_move_by_production_location as
  select 
      nextval('chricar_product_move_by_production_location_id_seq'::regclass)::int as id,
      l.id as location_id,
      product_id, 
      product_qty as name,
      i.move_value_cost, 
      date, 
      period_id, 
      fiscalyear_id,
      'used' as used,capacity
  from 
    stock_location l,
    stock_move i,
    account_period p
  where 
    l.usage='production'
    and i.location_dest_id = l.id
    and i.state = 'done'
    and p.id = i.period_id
  union all
  select 
    nextval('chricar_product_move_by_production_location_id_seq'::regclass)::int as id,
    l.id as location_id ,
    product_id, 
    -product_qty, 
    -o.move_value_cost, 
    date, 
    period_id, 
    fiscalyear_id,
   'produced' as used,capacity
  from 
    stock_location l,
    stock_move o,
    account_period p
  where 
    l.usage='production'
    and o.location_id = l.id
    and o.state = 'done'
    and p.id = o.period_id
;""")
chricar_product_move_by_production_location()

class chricar_product_by_production_location(osv.osv):
    _name = "chricar.product_by_production_location"
    _description = "Product Production Sum"
    _auto = False
    _columns = \
        { 'id'            : fields.char    ('id',size=16, readonly=True)
        , 'location_id'   : fields.many2one('stock.location','Location', select=True, required=True)
        , 'product_id'    : fields.many2one('product.product','Product', select=True, required=True)
        , 'uom_id'        : fields.related ('product_id', 'uom_id', type="many2one", relation="product.uom", string="UoM", readonly = True )
        , 'cost_method'   : fields.related ('product_id', 'cost_method', type="char", relation="product.product", string="Cost Method", readonly = True )
        , 'name'          : fields.float   ('Quantity', digits=(16,2))
        , 'amount'        : fields.float   ('Amount', digits=(16,2))
        , 'average_price' : fields.float   ('Average Price', digits=(16,4))
        , 'fiscalyear_id' : fields.many2one('account.fiscalyear','Year', select=True, required=True)
        , 'used'          : fields.selection([('produced', 'Produced'), ('used', 'Used')],'Usage',size=16, readonly=True)
        , 'capacity'      : fields.float   ('Capacity',type='float', help="Defines the capacity of the location")
        , 'yield'         : fields.float   ('Yield',type='float')
        }

    def init(self, cr):
        cr.execute("""
DROP SEQUENCE IF EXISTS chricar_product_by_production_location_id_seq CASCADE;
CREATE SEQUENCE chricar_product_by_production_location_id_seq;
create or replace view chricar_product_by_production_location as
  select 
      nextval('chricar_product_by_production_location_id_seq'::regclass)::int as id,
      location_id,
      product_id,
      fiscalyear_id,
      used,
      capacity,
      case when capacity >0 then sum(name) / capacity else 0 end as yield,
      sum(name) as name, 
      sum(move_value_cost) as amount,
      case when sum(name) != 0 then round(sum(move_value_cost)/sum(name),2) else 0 end as average_price
    from chricar_product_move_by_production_location
    group by location_id,product_id,fiscalyear_id,used,capacity
    having round(sum(name),4) != 0 or round(sum(move_value_cost),2) != 0
;""")
chricar_product_by_production_location()
