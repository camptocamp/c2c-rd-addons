# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2010 Camptocamp Austria (<http://www.camptocamp.at>)
#    Copyright (C) 2011-2011 Swing Entwicklung betrieblicher Informationssysteme GmbH (<http://www.swing-system.com>)
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
from osv import fields, osv

class account_journal(osv.osv):
    _inherit = "account.journal"
    _sequence_selection = [('none','No creation'), ('create','Create'), ('create_fy','Create per Fiscal Year')]
    _columns = \
    { 'create_sequence' : fields.selection
        ( _sequence_selection
        , 'Create Sequence'
        , required = "True" 
        , help     = """Sequence will be created on the fly using the code of the journal and fiscalyear as prefix"""
        )
    }

    _defaults = {'create_sequence' : lambda *a: 'create_fy'}
account_journal()
