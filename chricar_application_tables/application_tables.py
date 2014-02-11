
#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2009-03-27 16:17:42+01
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

class chricar_application_tables(osv.osv):
     _name = "chricar.application_tables"

     _columns = {
       'active'             : fields.boolean ('Active'),
       'application_id'     : fields.many2one('chricar.application','Application', select=True),
       'author'             : fields.char    ('Author', size=128),
       'category'           : fields.char    ('Category', size=64, required=True),
       'demo_xml'           : fields.char    ('Demo XML', size=64),
       'depends'            : fields.char    ('Depends', size=64),
       'description'        : fields.text    ('Description', required=True),
       'import_data'        : fields.boolean ('Import Data', required=True),
       'inherit_method'     : fields.char    ('Inherit Method', size=32),
       'inherit_module_name': fields.char    ('Inherit Modul Name', size=64),
       'inherit_table'      : fields.char    ('Inherit Table', size=32),
       'init_xml'           : fields.char    ('Init XML', size=64, required=True),
       'installable'        : fields.boolean ('Installable', required=True),
       'main_menu'          : fields.char    ('Main Menu', size=64, required=True),
       'menu'               : fields.char    ('Menu', size=64, required=True),
       'menu_seq'           : fields.float   ('Menu Seq', required=True),
       'migrate'            : fields.boolean ('Migrate', required=True),
       'name'               : fields.char    ('Table Name', size=254, required=True),
       'prefix'             : fields.char    ('Table Prefix', size=16, required=True),
       'state'              : fields.char    ('State', size=8),
       'table_name'         : fields.char    ('Table Name Display', size=254),
       'table_name_source'  : fields.char    ('Source Table', size=64, required=True),
       'tree_editable'      : fields.char    ('Tree Editable', size=8),
       'data'         : fields.char    ('Update XML', size=64, required=True),
       'version'            : fields.char    ('Version', size=8, required=True),
       'website'            : fields.char    ('Website', size=64),
}
     _defaults = {

       'active'            : lambda *a: True,
       'description'       : lambda *a: 'not defined',
       'import_data'       : lambda *a: False,
       'init_xml'          : lambda *a: 'not defined',
       'installable'       : lambda *a: True,
       'menu'              : lambda *a: 'not defined',
       'menu_seq'          : lambda *a: '10',
       'migrate'           : lambda *a: True,
       'state'             : lambda *a: 'Draft',
       'data'        : lambda *a: 'not defined',
       'version'           : lambda *a: '1.0',
}
     _order = "name"
chricar_application_tables()

class chricar_application(osv.osv):
      _inherit = "chricar.application"
      _columns = {
          'application_tables_ids': fields.one2many('chricar.application_tables','application_id','Application Tables'),
      }
chricar_application()

