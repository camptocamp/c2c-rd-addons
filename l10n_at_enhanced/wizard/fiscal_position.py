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

from openerp.osv import osv

class wizard_multi_charts_accounts(osv.osv_memory):
    _name='wizard.multi.charts.accounts'
    _inherit='wizard.multi.charts.accounts'

    def execute(self, cr, uid, ids, context=None):
        """
        We want to deactivate - but not delete - the original fiscal positions defined in l10n_at
        """
        if not context:
            context = {}
        res = super(wizard_multi_charts_accounts, self).execute(cr, uid, ids, context)
        
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        if not company_id:
            company_id = 1
        fiscal_pos_ids = fiscal_pos_obj.search(cr, uid, [('company_id', '=', company_id), ('name', 'not like', 'Partner')])
        fiscal_pos_obj.write(cr, uid, fiscal_pos_ids, {'active': False})
        
        return res

wizard_multi_charts_accounts()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
