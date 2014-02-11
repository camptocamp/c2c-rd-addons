# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
##import pooler
import openerp.tools.sql
from openerp.tools import config

from datetime import datetime
from dateutil.relativedelta import relativedelta

class account_fiscalyear(osv.osv):
    _inherit = 'account.fiscalyear'

    # function must be copied
    def create_period(self,cr, uid, ids, context={}, interval=1):
        for fy in self.browse(cr, uid, ids, context):
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d')<fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)

                if de.strftime('%Y-%m-%d')>fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                self.pool.get('account.period').create(cr, uid, {
                    'name': ds.strftime('%Y%m'),
                    'code': ds.strftime('%Y%m'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    def init(self,cr):
        cr.execute("""update account_period
                         set name = to_char(date_stop,'YYYYMM'),
                             code = to_char(date_stop,'YYYYMM')
                            where name != to_char(date_stop,'YYYYMM')
                              and special = False
                  """)

        cr.execute("""update account_period
                         set name = to_char(date_stop,'YYYY') || '00 Opening Period',
                             code = to_char(date_stop,'YYYY') || '00'
                            where special=True

                  """)

        cr.execute("""update ir_sequence
                         set prefix = replace(prefix,'/','-')
                  """)

account_fiscalyear()
