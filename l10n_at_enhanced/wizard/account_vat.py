# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) camptocamp
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

class account_vat_declaration(osv.osv_memory):
    _inherit = 'account.vat.declaration'
    
    _columns = {
      'template_id' : fields.many2one('xml.template', "XML Template"),
      }
    
    def create_tax_xml(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.tax.code'
        datas['form'] = self.read(cr, uid, ids, context=context)[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        datas['form']['company_id'] = self.pool.get('account.tax.code').browse(cr, uid, [datas['form']['chart_tax_id']], context=context)[0].company_id.id
        if datas['form']['template_id']:
            template_id = datas['form'].get('template_id', False)
        else:
            template_id = ''
        period_ids = [] # FIXME
        
        tax_code_obj = self.pool.get('account.tax.code')
        xml_gen_obj = self.pool.get('xml.template')
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        if template_id:
            fiscalyear_id = datas['form'].get('fiscalyear_id', False)
            for fiscalyear in fiscalyear_obj.browse(cr, uid, [fiscalyear_id]):
                chart_id = datas['form']['chart_tax_id']
                for tax in tax_code_obj.browse(cr, uid, [chart_id] , context):
                    xml = xml_gen_obj.generate_xml(cr, uid, template_id, tax = tax, fiscalyear = fiscalyear )
                    
                    file_name = 'tax_xml_'+fiscalyear.code
                    file_name += '' # FIXME period name missing
                    file_name += '.xml'
                    file_name = file_name.replace(' ','').replace('/','-')
                    xml_gen_obj.attach_xml(cr, uid, fiscalyear_id , fiscalyear , xml, file_name, file_name, description=False, pretty_print=True, context=None)
  
        return 

account_vat_declaration()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
