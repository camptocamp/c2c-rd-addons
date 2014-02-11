
#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-03-27 16:28:26+01
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
import time
from openerp.osv import fields,osv
#import pooler

class chricar_application_columns(osv.osv):
     _name = "chricar.application_columns"

     _columns = {
       'application_tables_id': fields.many2one('chricar.application_tables','Source Table Name', select=True, required=True),
       'char_size'          : fields.float   ('Size', digits=(4,0)),
       'column_fk'          : fields.char    ('Column FK', size=64),
       'column_list_show'   : fields.boolean ('List Show', required=True),
       'defaults'           : fields.char    ('Defaults', size=256),
       'extra_tab'          : fields.boolean ('Extra Tab', required=True),
       'help'               : fields.char    ('Help', size=256),
       'inherits_columns'   : fields.boolean ('Inherits Columns', required=True),
       'is_name'            : fields.boolean ('is Name', required=True),
       'many2one'           : fields.boolean ('Many2one', required=True),
       'migrate'            : fields.boolean ('Migrate', required=True),
       'name_column'        : fields.char    ('Column Name Display', size=64, required=True),
       'name_column_source' : fields.char    ('Source Column Name', size=64, required=True),
       'name'               : fields.char    ('Column Name', size=64, required=True),
       'num_precision'      : fields.float   ('Num Precision', digits=(4,0)),
       'num_scale'          : fields.float   ('Num Scale', digits=(4,0)),
       'one2many_col_name'  : fields.char    ('One2many Col Name', size=64),
       'read_only'          : fields.boolean ('Read Only', required=True),
       'required'           : fields.boolean ('Required', required=True),
       'search'             : fields.char    ('Search', size=8),
       'sequence'           : fields.float   ('Sequence', digits=(4,0)),
       'sort_form'          : fields.float   ('Form Sort', digits=(4,0)),
       'sort_list'          : fields.integer ('List Sort'),
       'source_pk'          : fields.float   ('Source PK', digits=(4,0)),
       'state'              : fields.char    ('State', size=16),
       'suppress_in_form'   : fields.boolean ('Form Suppress', required=True),
       'table_fk'           : fields.char    ('Table FK', size=64),
       'table_fk_source'    : fields.char    ('Source Table Foreign Key', size=64),
       'tiny_column_english': fields.char    ('Column Name English', size=64),
       'translate'          : fields.boolean ('Translate', required=True),
       'type'               : fields.char    ('Type', size=16, required=True),
}
     _defaults = {
       'column_list_show'  : lambda *a: True,
       'extra_tab'         : lambda *a: False,
       'inherits_columns'  : lambda *a: False,
       'is_name'           : lambda *a: False,
       'many2one'          : lambda *a: False,
       'migrate'           : lambda *a: True,
       'read_only'         : lambda *a: False,
       'required'          : lambda *a: False,
       'suppress_in_form'  : lambda *a: False,
       'translate'         : lambda *a: False,
}

chricar_application_columns()

class chricar_application_tables(osv.osv):
      _inherit = "chricar.application_tables"
      _columns = {
          'application_columns_ids': fields.one2many('chricar.application_columns','application_tables_id','Application Columns'),
      }
chricar_application_tables()

