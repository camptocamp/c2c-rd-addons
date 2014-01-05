# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Ferdinand Gassauer)
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
from osv import fields, osv
import one2many_sorted
import logging

class res_users_company(osv.osv):
    _name = "res.users.company"
    _description = "User Company Specific Data"
    # may be not all necessary
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'company_id': fields.many2one('res.company', 'Company'),
        'user_email': fields.char('Email', size=240, help="Email for this company"),
        'signature': fields.text('Signature', help="Signature for this company"),
        }

    def init(self, cr):
      return
      cr.execute("""
          insert into res_users_company(user_id,company_id,user_email,signature)
                 select id,company_id,email,signature from res_config_users u
                 where (u.id,u.company_id) not in (select user_id,company_id from res_users_company);
      """)

    
res_users_company()


class users(osv.osv):
    _inherit = "res.users"

    def _get_email(self, cr, uid, ids, field, arg, context=None):
        if not context:
            context = {}
        user_comp_obj = self.pool.get('res.users.company')
        res = {}        
        
        c_id = ''
        if context.get('company_id'):
            c_id = context['company_id']
        for user in self.browse(cr, uid, ids):         
            res[user.id] = ''
            for comp in user.user_company_ids:
                if c_id or user.company_id.id == comp.company_id.id:
                    #c_id = user.company_id.id
                    res[user.id] = comp.user_email
                
        return res

    def _get_signature(self, cr, uid, ids, field, arg, context=None):
        if not context:
            context = {}
        user_comp_obj = self.pool.get('res.users.company')
        res = {}        
        
        c_id = ''
        if context.get('company_id'):
            c_id = context['company_id']
        for user in self.browse(cr, uid, ids):         
            res[user.id] = ''

            for comp in user.user_company_ids:
                if c_id or user.company_id.id == comp.company_id.id:
                    #c_id = user.company_id.id
                    res[user.id] = comp.signature
                
        return res
    
    _columns = {
        'user_company_ids': one2many_sorted.one2many_sorted('res.users.company', 'user_id', 'Company Data' , order = 'company_id.name') ,   
        'user_email': fields.function(_get_email, type='char', string='Email'),
        'signature': fields.function(_get_signature, type='text', string='Signature'),
      
        }

users()