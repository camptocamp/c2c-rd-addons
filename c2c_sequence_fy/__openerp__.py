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
    'name': 'Sequence Financial Year Extension fy (not for v61 and above)',
    'version': '0.7',
    'category': 'Accounting',
    'description': """
    Please do not used this module in v61 and above, there is a new one
This module adds 
* "fy" and "cj" as placeholder for prefix and suffix.

* creation rules for missing sequences in ir_sequence_type 
   if a not existing sequence is requested it will be created on the fly
   * if no prefix is defined in sequence_types a prefix will be created using 
     the first characters of each word of then name of the sequence type
     Example "Account Invoice In" will pe "AAI-"

=== fy ===
This allows gapless numbering per fiscal year.
This sequence code will be used to format the start date of the fiscalyear for the placeholder 'fy' defined for sequences as prefix and suffix.
Example a fiscal year starting on March 1st with a sequence code %Ya will generate 2011a.
This allows to handle multiple fiscal years per calendar year and fiscal years not matching caledar years easily.
This module replaces all (year) prefix and suffix occurences but will return same results as (year) for calendar year = fiscal year
as long as the sequence code is not defined.
=== cj ===
This allows to use the code of the journal as place holder.

This module is a prerequisit to automatically generated new fiscal years , periods and associated sequences using fy in prefix instead of hard coding 

ToDo: cj
""",
    'author': 'Camptocamp Austria',
    'depends': [ 'base','account' ],
    'update_xml': ['ir_sequence_view.xml',
       ],
    #'update_xml': ['product_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
