# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- encoding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-10-17 12:10:57+02
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
import time
from osv import fields,osv
import pooler

class chricar_account_move_line_igel(osv.osv):
     _name = "chricar.account.move.line.igel"

     _columns = {
       'company_id'         : fields.many2one('res.company', 'Company', required=True),
       'kanzlei'            : fields.integer ('Kanzlei'),
       'klient'             : fields.integer ('Klient'),
       'fiscalyear_id'      : fields.many2one('account.fiscalyear','Geschaeftsjahr'),
       'kontoart'           : fields.integer ('Kontoart'),
       'account_id'         : fields.many2one('account.account', 'Kontonummer' ),
       'kontoname'          : fields.char    ('Kontoname', size=64),
       'ba_nr'              : fields.char    ('BA-Nr',size=8),
       'periode'            : fields.integer ('Periode'),
       'buchungsdatum'      : fields.char    ('Buchungsdatum',size=16),
       'bel_nr'             : fields.char    ('Bel.Nr',size=16),
       'name'               : fields.integer ('Journalzeile'),
       'belegdatum'         : fields.char    ('Belegdatum',size=16),
       'gegenkonto'         : fields.char    ('Gegenkonto',size=16),
       'kst_nr'             : fields.char    ('KstNr',size=16),
       'text'               : fields.char    ('Text',size=128),
       'betrag_soll'        : fields.float   ('Betrag (Soll)'),
       'betrag_haben'       : fields.float   ('Betrag (Haben)'),
       'ust_kz'             : fields.char    ('Ust-KZ',size=4),
       'ust'                : fields.float   ('Ust'),
       'ust_betrag'         : fields.float   ('Ust-Betrag'),
       'fwc'                : fields.char    ('FWC',size=4),
       'fw_betrag'          : fields.float   ('FW-Betrag'),
       'betreuer'           : fields.char    ('Betreuer',size=16),
       'team'               : fields.char    ('Team',size=16),
       'klientengruppe'     : fields.char    ('Klientengruppe',size=16),
       'zessionsname'       : fields.char    ('Zessionsname',size=16),
       'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
}

     _defaults = {
        'company_id' : lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
}
     _order =   "name"

chricar_account_move_line_igel()
