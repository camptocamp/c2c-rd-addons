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
from openerp.osv import osv, fields
from openerp.tools.translate import _
        

#----------------------------------------------------------
#  Account fiscalyear closing text INHERIT
#----------------------------------------------------------
class account_closing_text(osv.osv):
    _name = "account.closing.text"
    _columns = {
        'company_id'   : fields.many2one('res.company', 'Company', required=True, ondelete="cascade"),
        'account_id'   : fields.many2one('account.account', 'Account', required=True, ondelete="cascade"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True, ondelete="cascade"),
        'closing_text' : fields.text('Closing Remarks'),
     }


account_closing_text()

#----------------------------------------------------------
#  Account INHERIT
#----------------------------------------------------------
class account_account(osv.osv):
    _inherit = "account.account"
    _columns = {
        'account_closing_remark_ids': fields.one2many('account.closing.text', 'account_id', 'Account Closing Text'),
     }


account_account()