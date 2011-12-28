# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
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


{
    'name': 'Totally gapless numbering for sale/purchase order, picking',
    'version': '0.7',
    'category': 'Accounting & Finance',
    'description': """
Standard OpenERP allows deletion of sale / purchase order and pickings
this module forbid's deletion by users and managers, unused documents must be canceled manually
only users belonging to the group 'Allow SO PO PICK Gap' may delete these resources
ToDo:
* workflow - create number leaving draft
* do not create number on "new" 
""",
    'author': 'Camptocamp Austria',
    'depends': [ 'stock','sale','purchase' ],
    'update_xml': ['sequence_no_gap.xml',
                   'security/group.xml', 
                   'security/ir.model.access.csv',
       ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
