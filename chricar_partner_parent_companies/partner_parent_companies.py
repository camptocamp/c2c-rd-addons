# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2008-07-05
#
###############################################
import time
from osv import fields,osv
import pooler

class res_partner_parent_company(osv.osv):
     _name = "res.partner.parent_company"

     def _children_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
           if line.partner_id.participation_ids:
             for participation in line.partner_id.participation_ids:
               res += participation.id
        return res

     _columns = {
       'name'               : fields.float   ('Share',digits=(16,2),required=True),
       'paid_in'            : fields.float   ('Paid in Share',digits=(16,2),required=True),
       'agio'               : fields.float   ('Agio',digits=(16,2),required=True),
       'percentage'         : fields.float   ('Percentage',digits=(9,6)),
       'partner_id'         : fields.many2one('res.partner','Partner', required=True),
       'partner_parent_id'  : fields.many2one('res.partner','Parent', required=True),
       'valid_from'	    : fields.date    ('Valid From'),
       'valid_until'	    : fields.date    ('Valid Until'),
       'valid_fiscal_from'  : fields.date    ('Fiscal Valid From'),
       'valid_fiscal_until' : fields.date    ('Fiscal Valid Until'),
       'contract_date'      : fields.date    ('Contract Date'),
       'contract_number'    : fields.char    ('Contract Number', size=32),
       'consolidation'      : fields.boolean ('Consolidation'),
       'comment'            : fields.text    ('Notes'),
       'active'             : fields.boolean ('Active'),
       'state'              : fields.char    ('State', size=16),
       #'children_ids'       : fields.function(_children_ids, method=True, string='Participations'),
       #'children_ids'       :fields.one2many('res.partner.parent_company','parent_id','Children Items'),
     }
     _defaults = {
       'active': lambda *a: True,
       'name': lambda *a: 0.0,
       'paid_in': lambda *a: 0.0,
       'agio': lambda *a: 0.0,
       'percentage': lambda *a: 0.0,
     }
res_partner_parent_company()

class res_partner(osv.osv):
      _inherit = "res.partner"
      _columns = {
          'partner_ids': fields.one2many('res.partner.parent_company','partner_id','Parent Companies'),
          'partner_current_ids': fields.one2many('res.partner.parent_company','partner_id','Parent Companies Current'),
          'participation_ids': fields.one2many('res.partner.parent_company','partner_parent_id','Participations'),
          'participation_current_ids': fields.one2many('res.partner.parent_company','partner_parent_id','Participations Current', ),
      }
res_partner()