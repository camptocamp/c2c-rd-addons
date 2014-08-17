# -*- coding: utf-8 -*-

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
from datetime import datetime
import time
from osv import fields,osv
from tools.translate import _
from openerp import SUPERUSER_ID

class res_country(osv.osv):
    _inherit = "res.country"

    _columns = {
    'eu_member'       : fields.boolean ('EU-Member'),
    'date_start'      : fields.date    ('Member Begin'),
    'date_end'        : fields.date    ('Member End'),

    }
     
    def check_eu_member(self, cr, uid, country_d, date):
        res = False
        d = date.strftime('%Y-%m-%d')
        for country in self.browse(cr, uid, [country_id]):
            if date_start and date_start <= d and (not date_end or (date_end and date_end >= d)):
                res = True
        
        return res
    
    def init(self, cr):
        
        eu_member = [
            ('Austria','1995-01-01'),
            ('Belgium','1958-01-01'),
            ('Bulgaria','2007-01-01'),
            ('Croatia','2013-07-01'),
            ('Cyprus','2004-05-01'),
            ('Czech Republic','2004-05-01'),
            ('Denmark','1973-01-01'),
            ('Estonia','2004-05-01'),
            ('Finland','1995-01-01'),
            ('France','1958-01-01'),
            ('Germany','1958-01-01'),
            ('Greece','1981-01-01'),
            ('Hungary','2004-05-01'),
            ('Ireland','1973-01-01'),
            ('Italy','1958-01-01'),
            ('Latvia','2004-05-01'),
            ('Lithuania','2004-05-01'),
            ('Luxembourg','1958-01-01'),
            ('Malta','2004-05-01'),
            ('Netherlands','1958-01-01'),
            ('Poland','2004-05-01'),
            ('Portugal','1986-01-01'),
            ('Romania','2007-01-01'),
            ('Slovakia','2004-05-01'),
            ('Slovak Republic','2004-05-01'),
            ('Slovenia','2004-05-01'),
            ('Spain','1986-01-01'),
            ('Sweden','1995-01-01'),
            ('United Kingdom','1973-01-01')
        ]
        for c in eu_member:
            country_id = self.search(cr, SUPERUSER_ID, [ ('name','=',c[0]) ] )
            if country_id:
                self.write(cr, SUPERUSER_ID, country_id, { 'eu_member': True, 'date_start' : c[1] })
    

res_country()
