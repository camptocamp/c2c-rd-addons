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

    #def init(self, cr):
      #return
      #cr.execute("""
          #insert into res_users_company(user_id,company_id,user_email,signature)
                 #select id,company_id,email,signature from res_config_users u
                 #where (u.id,u.company_id) not in (select user_id,company_id from res_users_company);
      #""")

    
res_users_company()


class users(osv.osv):
    _inherit = "res.users"

    def _get_email(self, cr, uid, ids, field, arg, context=None):
        _logger = logging.getLogger(__name__)
        if not context:
            context = {}
        _logger.debug('FGF get mail context %s', context)
        user_comp_obj = self.pool.get('res.users.company')
        res = {}        
        
        c_id = ''
        if context.get('company_id'):
            c_id = context['company_id']
        _logger.debug('FGF get mail c_id %s', c_id)    
        for user in self.browse(cr, uid, ids, context):         
            res[user.id] = ''
            _logger.debug('FGF get mail user %s', user)
            for comp in user.user_company_ids:
                _logger.debug('FGF get mail res %s %s'%( c_id or user.company_id.id ,comp.company_id.id))        
                if (c_id or user.company_id.id) == comp.company_id.id:
                    _logger.debug('FGF get mail res found %s %s'%( (c_id or user.company_id.id) ,comp.company_id.id)) 
                    res[user.id] = comp.user_email
        _logger.debug('FGF get mail res %s', res)
        return res

    def _get_signature(self, cr, uid, ids, field, arg, context=None):
        _logger = logging.getLogger(__name__)
        if not context:
            context = {}
        user_comp_obj = self.pool.get('res.users.company')
        res = {}        
        c_id = ''
        if context.get('company_id'):
            c_id = context['company_id']
        _logger.debug('FGF get mail c_id %s', c_id)    
        for user in self.browse(cr, uid, ids, context):         
            res[user.id] = ''
            _logger.debug('FGF get mail user %s', user)
            for comp in user.user_company_ids:
                _logger.debug('FGF get mail res %s %s'%( c_id or user.company_id.id ,comp.company_id.id))        
                if (c_id or user.company_id.id) == comp.company_id.id:
                    _logger.debug('FGF get mail res found %s %s'%( (c_id or user.company_id.id) ,comp.company_id.id)) 
                    res[user.id] = comp.signature
        _logger.debug('FGF get mail res %s', res)
        return res
                
        return res
    
    _columns = {
        'user_company_ids': one2many_sorted.one2many_sorted('res.users.company', 'user_id', 'Company Data' , order = 'company_id.name') ,   
        'user_email': fields.function(_get_email, type='char', string='Email'),
        'signature': fields.function(_get_signature, type='text', string='Signature'),
      
        }

users()

class mail_message(osv.osv):
    _inherit = 'mail.message'

    def _get_company(self, cr, uid, ids, field, arg, context=None):
        if not context:
            context = {}
        res = {}
        _logger = logging.getLogger(__name__)
        for message in self.browse(cr, uid, ids, context):
            res[message.id] = ''
            if message.model:
                _logger.debug('FGF message.model %s', message.model)
                model_obj = self.pool.get(message.model)
                
                for model_rows in model_obj.browse(cr, uid, [message.res_id], context):
                    try:
                        _logger.debug('FGF message.model comp %s', model_rows.company_id.id)
                        res[message.id] = model_rows.company_id.id
                    except:
                        pass
        return res
        
    _columns = {
        'company_id' : fields.function(_get_company, methd=True, type='many2one', relation='res.company', string='Company')
    }
    
mail_message() 