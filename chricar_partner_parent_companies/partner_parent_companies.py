# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2008-07-05
#
###############################################
from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.one2many_sorted as one2many_sorted
import logging
import time

class res_partner_parent_company(osv.osv):
    _name  = "res.partner.parent_company"
    _order = "valid_from"

    def _children_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.partner_id.participation_ids:
                for participation in line.partner_id.participation_ids:
                    res += participation.id
        return res

    _columns = \
        { 'name'               : fields.float   ('Share', digits=(16,2), required=True)
        , 'paid_in'            : fields.float   ('Paid in Share', digits=(16,2), required=True)
        , 'agio'               : fields.float   ('Agio', digits=(16,2), required=True)
        , 'percentage'         : fields.float   ('Percentage', digits=(9,6))
        , 'partner_id'         : fields.many2one('res.partner', 'Partner', required=True)
        , 'partner_parent_id'  : fields.many2one('res.partner', 'Parent', required=True)
        , 'valid_from'                : fields.date    ('Valid From')
        , 'valid_until'            : fields.date    ('Valid Until')
        , 'valid_fiscal_from'  : fields.date    ('Fiscal Valid From')
        , 'valid_fiscal_until' : fields.date    ('Fiscal Valid Until')
        , 'contract_date'      : fields.date    ('Contract Date')
        , 'contract_number'    : fields.char    ('Contract Number', size=32)
        , 'consolidation'      : fields.boolean ('Consolidation')
        , 'comment'            : fields.text    ('Notes')
        , 'active'             : fields.boolean ('Active')
        , 'state'              : fields.char    ('State', size=16)
        #, 'children_ids'       : fields.function(_children_ids, method=True, string='Participations'),
        #, 'children_ids'       :fields.one2many('res.partner.parent_company', 'parent_id','Children Items'),
        }
    _defaults = \
        { 'active'     : lambda *a: True
        , 'name'       : lambda *a: 0.0
        , 'paid_in'    : lambda *a: 0.0
        , 'agio'       : lambda *a: 0.0
        , 'percentage' : lambda *a: 0.0
        }

    def cmp_func(self):
        def cmp (a,b) :
            if a.partner_id.name == b.partner_id.name :
                if a.valid_from == b.valid_from :
                    return 0
                elif a.valid_from < b.valid_from :
                    return -1
                else :
                    return 1
            elif a.partner_id.name < b.partner_id.name :
                return -1
            else :
                return 1

        return cmp
   # end def cmp_func
res_partner_parent_company()

class res_partner(osv.osv) :

    _inherit = "res.partner"
    _logger = logging.getLogger(__name__)

    def _get_share(self, cr, uid, share_owner_id, partner_id, share, owner_share, consolidate, level = 1):
        _logger = logging.getLogger(__name__)
        share_child = share
        owners_share = owner_share
        level_child = level
        for partner in self.browse(cr, uid, [partner_id]):
            self._logger.debug('partner %s share %s' %( partner.name, share) )

            for parent_share in partner.partner_current_ids:
                self._logger.debug('A parent %s share %s share_child %s' %( parent_share.partner_parent_id.name, parent_share.percentage, share_child ) )
                if parent_share.percentage >0 :
                    if share_child != None:
                        share = share_child * parent_share.percentage / 100
                    else:
                        share = parent_share.percentage
                else:
                    share = 0.0
                self._logger.debug('B partner %s share %s' %( parent_share.partner_id.name, share) )

                if parent_share.partner_parent_id.id == share_owner_id:
                    if consolidate == 'all':
                        owners_share += share
                        self._logger.debug('FGF owner %s partner %s share-res %s' %(share_owner_id, partner.name, owners_share) )
                    elif consolidate == 'direct' and level_child == 1:
                        owners_share += share
                    elif consolidate == 'consol' and parent_share.consolidation == True:
                        owners_share += share
                else:
                    level += 1
                    self._logger.debug('FGF A not owner - partner %s share %s share-res %s' %( partner.name, share, owners_share) )
                    owners_share = self._get_share(cr, uid, share_owner_id, parent_share.partner_parent_id.id,  share, owners_share, consolidate, level)
                    self._logger.debug('FGF B not owner - partner %s share %s share-res %s' %( partner.name, share, owners_share) )

        return owners_share

    def _get_owners_share(self, cr, uid, ids, name, args, context):
        if not context:
            context = {}
        res = {}
        for partner in self.browse(cr, uid, ids):
            if context.get('share_owner_id'):
                res[partner.id] = self._get_share(cr, uid, context['share_owner_id'], partner.id, None, 0.0, 'all')
            else:
                res[partner.id] = 0
        return res

    def _get_owners_direct_share(self, cr, uid, ids, name, args, context):
        if not context:
            context = {}
        res = {}
        for partner in self.browse(cr, uid, ids):
            if context.get('share_owner_id'):
                res[partner.id] = self._get_share(cr, uid, context['share_owner_id'], partner.id, None, 0.0, 'direct' )
            else:
                res[partner.id] = 0
        return res

    def _get_owners_consol_share(self, cr, uid, ids, name, args, context):
        if not context:
            context = {}
        res = {}
        for partner in self.browse(cr, uid, ids):
            if context.get('share_owner_id'):
                res[partner.id] = self._get_share(cr, uid, context['share_owner_id'], partner.id, None, 0.0, 'consol')
            else:
                res[partner.id] = 0
        return res


    _columns = \
        {
          'partner_ids'       : one2many_sorted.one2many_sorted
            ( 'res.partner.parent_company'
            , 'partner_id'
            , 'Parent Companies'
            , order  = 'partner_parent_id.name,valid_from'
            )
        , 'partner_current_ids'       : one2many_sorted.one2many_sorted
            ( 'res.partner.parent_company'
            , 'partner_id'
            , 'Parent Companies Current'
            , search = ['|',('valid_until', '=', False),('valid_until', '>',time.strftime('%Y-%m-%d')) ]
            , order  = 'partner_parent_id.name,valid_from'
            )
        , 'participation_ids' : one2many_sorted.one2many_sorted
            ( 'res.partner.parent_company'
            , 'partner_parent_id'
            , 'Participations'
            , order  = 'partner_id.name,valid_from'
            )
        , 'participation_current_ids' : one2many_sorted.one2many_sorted
            ( 'res.partner.parent_company'
            , 'partner_parent_id'
            , 'Participations Current'
            , search = ['|',('valid_until', '=', False),('valid_until', '>',time.strftime('%Y-%m-%d')) ]
            , order  = 'partner_id.name,valid_from'
            )
        , 'owners_share'             : fields.function(_get_owners_share, digits=(9,6), string='Owners Share', help="multi-level Owner share")
        , 'owners_direct_share'      : fields.function(_get_owners_direct_share, digits=(9,6), string='Owners Direct Share', help="Owners direct share")
        , 'owners_consol_share'      : fields.function(_get_owners_consol_share, digits=(9,6), string='Owners Share Consolidate', help="Owners share to consolidate")
        }
res_partner()

class res_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
          'owners_share'             : fields.related('partner_id', 'owners_share', type='float', string='Owners Share', help="multi-level Owner share")
        , 'owners_direct_share'      : fields.related('partner_id', 'owners_direct_share', type='float', string='Owners Direct Share', help="Owners direct share")
        , 'owners_consol_share'      : fields.related('partner_id', 'owners_consol_share', type='float',string='Owners Share Consolidate', help="Owners share to consolidate")
        }

res_company()
