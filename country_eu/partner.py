#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved

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
from osv import fields,osv
import time
from tools.translate import _
import logging

class res_partner(osv.osv):
    _inherit = "res.partner"

    def check_fiscal_position(self, cr, uid, ids, context):
        _logger = logging.getLogger(__name__)
        country_obj = self.pool.get('res.country')
        company_obj = self.pool.get('res.company')
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')

        fiscal_pos_ids = fiscal_pos_obj.search(cr, uid, [])
        if not fiscal_pos_ids:
            return True

        current_user = self.pool.get('res.users').browse(cr, uid, [uid], context=context)[0]
        company_id =  current_user.company_id.id

        home_country_id = ''
        if company_id:
            company_partner_id_address = current_user.company_id.partner_id.address
            for address in company_partner_id_address:
                if address.country_id:
                    home_country_id = address.country_id.id
        
        partner = self.browse(cr, uid, ids, context)[0]
        if home_country_id and not partner.property_account_position:
            d = time.strftime('%Y-%m-%d')
            for address in partner.address:
                if address.country_id and address.country_id.id != home_country_id:
                    for country in country_obj.browse(cr, uid, [address.country_id.id], context):
                        if country.date_start and country.date_start <= d and (not country.date_end or (country.date_end and country.date_end >= d)):
                            raise osv.except_osv(_('Error'), _('You must assign a fiscal postition (partner accounting tab) for EU-Partners in %s %s !') % \
                                    (country.name, partner.name ))
                        else:
                            raise osv.except_osv(_('Error'), _('You must assign a fiscal postition (partner accounting tab) for Non-EU-Partners in %s %s !') % \
                                    (country.name, partner.name))

        return ''

    def write(self, cr, uid, ids, vals, context=None):
        res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
        self.check_fiscal_position(cr, uid, ids, context)
        return res

    def create(self, cr, uid, vals, context=None):
        res = super(res_partner, self).create(cr, uid, vals, context=context)
        self.check_fiscal_position(cr, uid, ids, context)
        return res


        
    
res_partner()
