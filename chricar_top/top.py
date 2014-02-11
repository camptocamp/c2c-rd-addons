# -*- coding: utf-8 -*-

#!/usr/bin/python

##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-07-09 16:17:22+02
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
import logging

class stock_location(osv.osv):
    _inherit = "stock.location"

    _columns = \
        { 'blueprint' : fields.binary  ('Blueprint')
        , 'image'     : fields.binary  ('Image')
         , 'assessed_value' : fields.float   ('Assessed Value', digits=(10,0), help="""Assessed value for Austrian tax turpose (Einheitswert)""")
         , 'assessed_value_increased' : fields.float   ('Assessed Value Increased', digits=(10,0), help="""Assessed value for Austrian tax turpose (erhöhter Einheitswert)""")
         , 'assessed_date' : fields.date   ('Assessed Value Date',  help="""Date of assessed value for Austrian tax turpose (Einheitswertstichtag)""")
        }

stock_location()


class chricar_top(osv.osv):
    _name = "chricar.top"
    _table = "chricar_top"
    _logger = logging.getLogger(_name)

    class one2many_analytic(fields.one2many):
        def get (self, cr, obj, ids, name, user=None, offset=0, context=None, values={}):
            res = {}
            for id in ids : res[id] = []
            for v in values:
                top_analytic_id = [v.get('account_analytic_id')]

            ids2 = obj.pool.get (self._obj).search \
                ( cr
                , user
                , [(self._fields_id, 'in', top_analytic_id)]
                , limit = self._limit
                )

            for r in obj.pool.get (self._obj)._read_flat \
                (cr
                , user
                , ids2
                , [self._fields_id]
                , context = context
                , load = '_classic_write'
                ):
                res [id].append( r['id'] )
            return res
        # end def get


    def _operating_cost(self, cr, uid, ids, field_name, arg, context=None):
        result = {}

        for p in self.browse(cr, uid, ids, context):
            if p.location_id.operating_cost and  p.surface and  p.surface > 0.0:
                surface_tot = 0.0
                if p.location_id:
                    top_ids = self.pool.get('chricar.top').search(cr, uid, [('location_id', '=', p.location_id.id)])
                    for s in  self.pool.get('chricar.top').browse(cr, uid, top_ids):
                        if s.surface:
                            surface_tot += s.surface
                    if surface_tot > 0.0 and p.surface and p.surface > 0.0 :
                        operating_cost = p.location_id.operating_cost / surface_tot * p.surface
            else:
                operating_cost = 0.0
            result[p.id] = operating_cost
        return result

    def _get_ref(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for p in self.browse(cr, uid, ids, context):
            result[p.id] = 'chricar.top,' + str(p.id)
        return result

    _columns = {
      'active'             : fields.boolean ('Active', help="If the active field is set to False, it will allow you to hide the top without removing it."),
      'account_analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', required=True),
      'analytic_line_ids'  : one2many_analytic('account.analytic.line', 'account_id', 'Analytic Lines'),
      'alarm'              : fields.boolean ('Alarm', required=True),
      'old_building'       : fields.boolean ('Old Building', required=True),
      'constructed'        : fields.integer ('Construction Year'),
      'blueprint'          : fields.binary  ('Blueprint'),
      'category'           : fields.char    ('Category', size=16),
      'description'        : fields.text    ('Description'),
      'floor'              : fields.char    ('Floor', size=16, required=True),
      'balcony'            : fields.float   ('Balconies m²',digits=(10,2)),
      'garden'             : fields.float   ('Garden m²',digits=(10,2)),
      'terrace'            : fields.float   ('Terraces m²',digits=(10,2)),
      'garage'             : fields.integer ('Garage included'),
      'carport'            : fields.integer ('Carport included'),
      'parking_place_rentable': fields.boolean ('Parking rentable', help="Parking rentable in the location if available"),
      'handicap'           : fields.boolean ('Handicap Accessible', required=True),
      'heating'            : fields.selection([('unknown','unknown'),
                                               ('none','none'),
                                               ('tiled_stove', 'tiled stove'),
                                               ('stove', 'stove'),
                                               ('central','central heating'),
                                               ('self_contained_central','self-contained central heating')], 'Heating', required=True),
      'heating_source'     : fields.selection([('unknown','unknown'),
                                               ('electricity','Electricity'),
                                               ('wood','Wood'),
                                               ('pellets','Pellets'),
                                               ('oil','Oil'),
                                               ('gas','Gas'),
                                               ('district','District Heating')], 'Heating Source', required=True),
      'internet'           : fields.boolean ('Internet', required=True),
      'lease_target'       : fields.float   ('Target Lease', digits=(6,2)),
      'lift'               : fields.boolean ('Lift', required=True),
      'location_id'        : fields.many2one('stock.location','Location', select=True, required=True),
      'name'               : fields.char    ('Top', size=64, required=True),
      'note'               : fields.text    ('Notes'),
      'note_sales'         : fields.text    ('Note Sales Folder'),
      'partner_id'         : fields.many2one('res.partner','Owner', select=True),
      'partner_from'       : fields.date    ('Purchase Date'),
      'partner_to'         : fields.date    ('Sale Date'),
      'rooms'              : fields.char    ('Rooms', size=32 ),
      'solar_electric'     : fields.boolean ('Solar Electric System', required=True),
      'solar_heating'      : fields.boolean ('Solar Heating System', required=True),
      'staircase'          : fields.char    ('Staircase', size=8, required=True),
      'surface'            : fields.float   ('Surface', required=True, digits=(10,2)),

      'telephon'           : fields.boolean ('Telephon', required=True),
      'tv_cable'           : fields.boolean ('Cable TV', required=True),
      'tv_sat'             : fields.boolean ('SAT TV', required=True),
      'usage'              : fields.selection([('unlimited','unlimited'),
                                               ('office','Office'),
                                               ('shop','Shop'),
                                               ('flat','Flat'),
                                                ('rural','Rural Property'),
                                               ('parking','Parking')], 'Usage', required=True),
      'product_product_id' : fields.integer ('Product'),
      'sort'               : fields.integer ('Sort'),
       'sequence'           : fields.integer ('Sequ.'),

      'top_cost_ids'       : fields.one2many('chricar.top.cost','top_id','Top Costs'),

      'operating_cost'     : fields.function(_operating_cost, method=True, string="Monthly operating costs", type='float', digits=(16,0)),
      'ref_top'            : fields.function(_get_ref, method=True, string="Ref Top", type="char"),
      'air_condition'      : fields.selection([('unknown','Unknown'),
                                               ('none','None'),
                                               ('full','Full'),
                                               ('partial','Partial'),
                                               ], 'Air Condition' ),
}
    _defaults = {
      'active'            : lambda *a: True,
      'alarm'             : lambda *a: False,
      'old_building'      : lambda *a: False,
      'floor'             : lambda *a: '0',
      'balcony'           : lambda *a: 0,
      'terrace'           : lambda *a: 0,
      'garden'            : lambda *a: 0,
      'garage'            : lambda *a: 0,
      'carport'           : lambda *a: 0,
      'heating'           : lambda *a: 'self_contained_central',
      'heating_source'    : lambda *a: 'gas',
      'internet'          : lambda *a: False,
      'lift'              : lambda *a: True,
      'solar_electric'    : lambda *a: False,
      'solar_heating'     : lambda *a: False,
      'staircase'         : lambda *a: '1',
      'telephon'          : lambda *a: False,
      'tv_cable'          : lambda *a: False,
      'tv_sat'            : lambda *a: False,
      'usage'             : lambda *a: 'unlimited',
}

#     _order = 'partner_id.name','location_id.name','sequence'
#     _order = 'location_id,sort'


    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        #reads = self.read(cr, uid, ids, ['name','location_id'])
        reads = self.read(cr, uid, ids, [])
        res = []
        for record in reads:
            top = record['name']
            staircase = record['staircase']
            floor = record['floor']
            surface = ''
            if record['surface'] > 0.0:
                surface = ' [' + str(record['surface'])  + u'm²]'
            location = record['location_id'][1]

            #name = location  + ' - ' + staircase + '/' + floor + '/' + top + surface
            name = staircase + '/' + floor + '/' + top
            res.append((record['id'], name))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        ids = self.search(cr, user, [('location_id',operator,name)] + args, limit=limit, context=context)
        ids += self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    def init(self, cr):
        """
            Creates not existing analytic accounts for
            * objects (stock locations)
            * tops
            @param cr: the current row, from the database cursor
        """
        context = []
        res = {}

        top_obj = self.pool.get('chricar.top')
        comp_obj = self.pool.get('res.company')
        analytic_obj = self.pool.get('account.analytic.account')
        ids = top_obj.search(cr,1,[('account_analytic_id','=',False),('usage','!=','parking')])
        for top in top_obj.browse(cr,1,ids,context ):
            vals = {}

            top_name = top.location_id.name + ' - '
            if top.staircase != '0':
                top_name += top.staircase
            if top.floor != '0':
                top_name += '/'+ top.floor
            if top.staircase != '0' or top.floor != '0':
                top_name  += '/'
            top_name += top.name
            if top.surface > 0.0:
                top_name += ' ('+ str(top.surface) + u'm²)'

            company = comp_obj.search(cr,1,[('partner_id','=',top.partner_id.id)])
            company_id = ''
            if company:
                company_id = company[0]
            vals = {
                'name'       : top_name,
                'company_id' : company_id,
                'state'      : 'open',
                }
            self._logger.debug('top vals `%s`', vals)

            analytic = analytic_obj.create(cr, 1, vals, context)
            self._logger.debug('analytic `%s`', analytic)
            top_obj.write(cr,1,[top.id], {'account_analytic_id': analytic} )
        return

chricar_top()
#####################
# Modification of parents
#####################

class res_partner(osv.osv):
    _inherit = "res.partner"

    def _lease_current_sum(self, cr, uid, ids, field_name, arg, context=None):
        _logger = logging.getLogger(__name__)
        result = {}
        lease_current_sum = 0.0
        for p in self.browse(cr, uid, ids, context):
            if p.top_ids:
                for top_id in p.top_ids:
                    lease_current_sum += top_id.lease_current
            result[p.id] = lease_current_sum

        return result

    def _lease_potential_sum(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        lease_potential_sum = 0.0
        for p in self.browse(cr, uid, ids, context):
            if p.top_ids:
                for top_id in p.top_ids:
                    lease_potential_sum += top_id.lease_potential
            result[p.id] = lease_potential_sum
        return result

    def _lease_current_participation_sum(self, cr, uid, ids, field_name, arg, context=None):
        _logger = logging.getLogger(__name__)
        result = {}
        lease_current_participation_sum = 0.0
        for p in self.browse(cr, uid, ids, context):
            if p.participation_ids:
                for participation_id in p.participation_ids:
                    if participation_id.percentage and participation_id.partner_id.lease_current_sum:
                        #lease_current_participation_sum += ( participation_id.partner_id.lease_current_sum + participation_id.partner_id.lease_current_participation_sum) * percentage
                        lease_current_participation_sum += ( participation_id.partner_id.lease_current_sum * participation_id.percentage / 100 )
                        # FIXME participation_id.partner_id.lease_current_sum returns a wrong value if more than one participation
                        self._logger.debug('percentage `%s`', participation_id.percentage)
                        self._logger.debug('sum lease `%s`', participation_id.partner_id.lease_current_sum)
                        self._logger.debug('partner `%s`', participation_id.partner_id.id)
            result[p.id] = lease_current_participation_sum

        return result

    _columns = {
        'top_ids'             : fields.one2many('chricar.top','partner_id','Real Estate Top'),
        'lease_current_sum'   : fields.function(_lease_current_sum, method=True, string="Current Lease Sum", type='float', digits=(16,0)),
        'lease_potential_sum' : fields.function(_lease_potential_sum, method=True, string="Potential Lease Sum", type='float', digits=(16,0)),
        'lease_current_participation_sum'   : fields.function(_lease_current_participation_sum, method=True, string="Current Lease Participation Sum (wrong!!)", type='float', digits=(16,0)),
    }
res_partner()

class stock_location(osv.osv):
    _inherit = "stock.location"
    _columns = {
        'top_ids'        : fields.one2many('chricar.top','location_id','Real Estate Top'),
        'operating_cost' : fields.float   ('Monthly Operating Costs', digits=(10,2), help="""Operating Costs for Real Estate, will be calculated per m² for each Top"""),
    }
    _order = 'complete_name'

stock_location()

#####################
# Costs for renting out
#####################
class chricar_top_cost (osv.osv):
    _name = "chricar.top.cost"
    _table = "chricar_top_cost"

    def _amount_tax(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        tax = 0.0
        tax_rate = 0.0
        for p in self.browse(cr, uid, ids, context):
            amount_base = p.name
            if amount_base and p.account_tax_id:
                tax_rate = p.account_tax_id.amount
                tax = round(amount_base * tax_rate ,2)
            result[p.id] = tax
        return result

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        total = 0.0
        tax_rate = 0.0
        for p in self.browse(cr, uid, ids, context):
            amount_base = p.name
            if amount_base and p.account_tax_id:
                tax_rate = p.account_tax_id.amount
            tax = round(amount_base * tax_rate ,2)
            total = amount_base + tax
            result[p.id] = total
        return result

    _columns = {
       'top_id'             : fields.many2one('chricar.top','Top', select=True, required=True),
       'seq'                : fields.integer('Sort'),
       'account_id'         : fields.many2one('account.account','Account', required=True, select=1),
       'account_tax_id'     : fields.many2one('account.tax', 'Tax', required=True, select=1),
       'amount'             : fields.function(_amount, method=True, string="Amount Total",type='float',digits=(16,2)),
       'amount_tax'         : fields.function(_amount_tax, method=True, string="Amount Tax",type='float',digits=(16,2)),
       'name'               : fields.float('Amount Net', digits=(16,2)),
}
    _order = 'top_id, seq'

chricar_top_cost()



#####################
# Insurance Info - Top and Location
#####################
class chricar_insurance(osv.osv):
     _name = "chricar.insurance"

     _columns = {
       'top_id'             : fields.many2one('chricar.top','Top', select=True),
       'location_id'        : fields.many2one('stock.location','Location', select=True),
       'partner_id'         : fields.many2one('res.partner','Insurance', select=True),
       'name'               : fields.char    ('Insurance Contract', size=64, required=True),
       'insurance_from'     : fields.date    ('Insurance Date From'),
       'insurance_to'       : fields.date    ('Insurance Date To'),
       'term_of_notice'     : fields.date    ('Term of Notice'),
       'coverage'           : fields.float   ('Coverage'),
       'premium'            : fields.float   ('Premium'),
      }

     _sql_constraints = [
       ('top_or_location', "CHECK((top_id is not null or location_id is not null) and not (top_id is not null and location_id is not null))", "Either location or top must be defined" ) 
      ]

chricar_insurance()
