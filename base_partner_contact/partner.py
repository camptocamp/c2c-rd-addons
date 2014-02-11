# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

class res_partner_salutation(osv.osv):
    _name = 'res.partner.salutation'
    _columns = {
        'name': fields.char('Salutation', required=True, size=46, translate=True),
        'name_address': fields.char('Salutation Address', size=46, translate=True),
    }
    _order = 'name'
res_partner_salutation()

class res_partner(osv.osv):
  
    _inherit ='res.partner'

    
    def _get_title_name(self, cr, uid, title_id):
        title_obj = self.pool.get('res.partner.title')
        title_name = ''
        if title_id:
            for title in title_obj.browse(cr, uid, [title_id.id]):
                title_name = title.name
        return title_name
            
    def _compose_name(self, cr, uid, ids, name, arg, context=None):
        # this is for partner - alphabetical address book - sort
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            if partner.name and not partner.last_name:
                l_name = partner.name
            if partner.is_company:
                name = partner.last_name or l_name
            else:    
                first_name = partner.first_name or '' + ' '
                middle_name = partner.middle_name and ' ' + partner.middle_name  + ' ' or ''
                last_name = partner.last_name or l_name +', '
                title_prefix = ' '+ self._get_title_name(cr,uid, partner.title_prefix_id) + ' '
                title_postfix = ' ' + self._get_title_name(cr,uid, partner.title_postfix_id)

                name = last_name + first_name + middle_name + title_prefix + title_postfix
                if name == last_name:
                    name = replace(name, ', ', '')
            if name:            
                res[partner.id] = name.replace('  ',' ').rstrip(' ').lstrip(' ') # to avoid double spaces
            else:
                res[partner.id] = ''

        return res

    def _compose_full_name(self, cr, uid, ids, name, arg, context=None):
        # this is for Address
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            if partner.name and not partner.last_name:
                l_name = partner.name
            if partner.is_company:
                name = partner.last_name or l_name
            else:    
                salutation = partner.salutation_id and partner.salutation_id.name_address or ''
                first_name = partner.first_name or ''
                middle_name =  partner.middle_name or ''
                last_name_prefix =  self._get_title_name(cr,uid, partner.name_prefix_id)
                last_name = partner.last_name
                title_prefix = self._get_title_name(cr,uid, partner.title_prefix_id)
                title_postfix = self._get_title_name(cr,uid, partner.title_postfix_id)
                
                name = salutation +' '+ title_prefix + ' ' + first_name + ' ' + middle_name + ' ' + last_name_prefix + ' ' + last_name + ' ' + title_postfix
                
            res[partner.id] = name.replace('  ',' ').replace('  ',' ').rstrip(' ').lstrip(' ') # to avoid double spaces
        return res
        
    def _compose_full_name_with_partner(self, cr, uid, ids, name, arg, context=None):
        # this is for Address
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            if partner.is_company:
                name = partner.last_name
            else:    
                salutation = partner.salutation_id and partner.salutation_partner_id.name_address or ''
                first_name = partner.first_name or ''
                middle_name =  partner.middle_name or ''
                last_name_prefix =  self._get_title_name(cr,uid, partner.name_prefix_id)
                last_name = partner.last_name
                title_prefix = self._get_title_name(cr,uid, partner.title_prefix_id)
                title_postfix = self._get_title_name(cr,uid, partner.title_postfix_id)
                
                name = salutation +' '+ title_prefix + ' ' + first_name + ' ' + middle_name + ' ' + last_name_prefix + ' ' + last_name + ' ' + title_postfix
                
            res[partner.id] = name.replace('  ',' ').replace('  ',' ').rstrip(' ').lstrip(' ') # to avoid double spaces
        return res

    _columns = {
        'first_name' : fields.char('First Name', size=32),
        'middle_name' : fields.char('Middle Name', size=16),
        'last_name' : fields.char('Name / Last Name', size=128),
        'salutation_id' : fields.many2one('res.partner.salutation','Salutation'),
        'salutation_partner_id' : fields.many2one('res.partner.salutation','Salutation with Partner'),
        'title_prefix_id' : fields.many2one('res.partner.title','Title Prefix'),
        'title_postfix_id' : fields.many2one('res.partner.title','Title Postfix'),
        'name_prefix_id' : fields.many2one('res.partner.title','Name Prefix', help="Example: de, von, Graf"),
        'name' : fields.function(_compose_name, type='char', string='Name', size=128, help="used for alphapetical sort",store = True), # or function field
        'full_name' : fields.function(_compose_full_name, type='char', string='Full Name', size=128, help="used for address"), # or function field
        'full_name_with_partner' : fields.function(_compose_full_name_with_partner, type='char', string='Full Name', size=128, help="used for address"), # or function field
        'is_company' : fields.boolean('Is Company', help="Check if the contact is a company, otherwise it is a person" ), # from v7.0
    }
    _defaults = {
        'is_company' : lambda *a: True,
        }
        
        
    def init(self, cr):
        cr.execute("""update res_partner
                         set last_name = name
                       where last_name is null;""")

    def create(self, cr, uid, vals, context=None):
        if vals.get('name') and not vals.get('last_name') or ( vals.get('last_name') and not vals['last_name']):
            vals['last_name'] = vals['name']
        if vals.get('last_name') and not vals.get('name'):
            vals['name'] = vals['last_name']
        res = super(res_partner, self).create(cr, uid, vals, context)
        return res


#    def onchange_name(self, cr, uid, id, is_company = False, name='', first_name='', last_name='', middle_name='', title_prefix_id='', title_postfix_id='', context={}):
#        vals = {}
#        vals['is_company'] = is_company
#        vals['name'] = name
#        vals['first_name'] = first_name
#        vals['middle_name'] = middle_name
#        vals['last_name'] = last_name
#        vals['titel_prefix_id'] = title_prefix_id
#        vals['titel_postfix_id'] = title_postfix_id
            
#        name = self._compose_name(cr, uid, vals, context)
#        full_name = self._compose_full_name(cr, uid, vals, context)
#        return {'value': {'name': name, 'full_name': full_name}}

res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

