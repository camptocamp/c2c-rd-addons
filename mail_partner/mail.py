# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
##############################################################################
from openerp.osv import fields, osv
#import logging

class mail_message(osv.osv):
    _inherit = 'mail.message'
    
    def create(self, cr, uid, vals, context=None):
        partner_id = vals.get('partner_id',False)
        if not partner_id and vals.get('model',False):
            if vals['model'] == 'res.partner':
                vals['partner_id']= vals['res_id']
            else:
                model_obj = self.pool.get(vals['model'])
                if model_obj._columns.get('partner_id') and model_obj._columns['partner_id']:
                    for res in model_obj.browse(cr, uid, [vals['res_id']], context):
                        if res.partner_id:
                             vals['partner_id']= res.partner_id.id
            
        return super(mail_message, self).create(cr, uid, vals, context)

mail_message()
