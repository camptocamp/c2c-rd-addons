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
from mx import DateTime
from openerp.osv import fields,osv
from openerp.tools import config
from openerp.tools.translate import _
import openerp.tools
from openerp.tools.sql import drop_view_if_exists
from datetime import date
from datetime import datetime
import openerp.addons.decimal_precision as dp

#----------------------------------------------------------
# prepare stock_moves
#----------------------------------------------------------

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    def _partner_name(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for partner in self.browse(cr, uid, ids, context):
             #pname=''
             pname = None
             if partner.partner_id and not (partner.sale_line_id or partner.purchase_line_id) :
                   pname = partner.partner_id.name
             if partner.sale_line_id:
                 pname = partner.sale_line_id.order_id.partner_id.name
             if partner.purchase_line_id:
                 pname = partner.purchase_line_id.order_id.partner_id.name
             if not pname and  partner.location_id.usage == 'internal':
                 if  partner.location_dest_id.usage == 'production':
                     pname = ' Used for Production'
                 if  partner.location_dest_id.usage == 'inventory':
                     pname = ' Inventory'
                 if  partner.location_dest_id.usage == 'internal':
                     pname = ' Internal'
             if not pname and  (partner.location_id.usage == 'production'   and  partner.location_dest_id.usage  == 'internal' ):
                 pname =  ' Production'

             result[partner.id] = pname
         return result


    def _partner_id(self, cr, uid, ids, field_name, arg, context=None):
         result = {}

         for partner in self.browse(cr, uid, ids, context):
            if not partner.partner_id and (partner.sale_line_id or partner.purchase_line_id) :

                 #pname=''
                 pname = None
                 if partner.sale_line_id:
                     pname = partner.sale_line_id.order_id.partner_id.id
                 if partner.purchase_line_id:
                     pname = partner.purchase_line_id.order_id.partner_id.id
                 if pname:
                     #result[partner.id] = int(pname)
                     result[partner.id] = pname

         return result

    def _period_id(self, cr, uid, ids, field_name, arg, context=None):
         result = {}
         for date_period in self.browse(cr, uid, ids, context):
             d_p = date_period.date
             d_p = datetime.strptime(d_p, '%Y-%m-%d  %H:%M:%S').date()
             cr.execute("""select id from account_period where to_date('%s','YYYY-MM-DD') between date_start and date_stop;
             """ % d_p)
             res = cr.fetchone()
             res_id = (res and res[0]) or False
             result[date_period.id] = int(res_id)
         return result


    _columns = {
       # 'partner_name'   : fields.function(_partner_name, method=True, string="Partner",type='char', size=132,store=True ),
       # 'partner_id'     : fields.function(_partner_id, method=True, string="Partner ID", type='many2one', relation='res.partner',store=True ),
       # 'period_id'      : fields.function(_period_id, method=True, string="Period ID",type='many2one', relation='account.period',store=True ),
}

stock_move()

#----------------------------------------------------------
# Product Partner Period Moves
#----------------------------------------------------------

class chricar_stock_product_partner(osv.osv):
    _name = "chricar.stock.product.partner"
    _description = "Product Partner Moves"
    _auto = False
    _columns = \
        { 'id'                 : fields.integer ('ID')
        , 'type'               : fields.selection
            ([('out','Sending Goods')
             ,('in' ,'Getting Goods') ]
            , 'Type'
            )
        , 'partner_id'         : fields.many2one('res.partner','Partner')
        , 'period_id'          : fields.many2one('account.period','Period')
        , 'product_id'         : fields.many2one('product.product','Product')
        , 'product_qty'        : fields.float('Product Qty', digits_compute=dp.get_precision('Account'))
        , 'move_value_cost'         : fields.float('Move Value', digits_compute=dp.get_precision('Account'))
        , 'move_value_sale'    : fields.float('Move Value Sale', digits_compute=dp.get_precision('Account'))
        , 'avg_price'          : fields.float('Avg Price', digits=(16, 6))
        , 'avg_sale_price'     : fields.float('Avg Sale Price', digits=(16, 6 ))
        }

    def init(self, cr):
        drop_view_if_exists(cr,'chricar_stock_product_partner')
        cr.execute("""
create view chricar_stock_product_partner as
select
       0 as id,
    s.type as type,
    a.id as partner_id, p.id as period_id ,product_id,
    sum(product_qty) as product_qty,
    sum(move_value_cost) as move_value_cost,
    sum(move_value_sale) as move_value_sale,
    case when sum(product_qty) > 0
       then sum(move_value_cost) / sum(product_qty)
       else 0
    end as avg_price,
    case when sum(product_qty) > 0
       then sum(move_value_sale) / sum(product_qty)
       else 0
    end as avg_sale_price
  from 
    stock_move,
    account_period p,
    res_partner a,
    stock_picking s
  where s.id=picking_id
    and stock_move.date between date_start and date_stop
    and s.type in ('in','out')
    and stock_move.state != 'cancel'
    and s.state != 'cancel'
  group by
    s.type,a.id,p.id ,product_id;
""")
chricar_stock_product_partner()
