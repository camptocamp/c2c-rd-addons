# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

 
from openerp.osv import fields, osv
import openerp.netsvc
from openerp.tools.translate import _
import time
import logging

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _is_production(self, cr, uid, ids, field_names, arg, context=None):
        """ 
        @return: Dictionary of values
        """
        res = {}
        for pick in self.browse(cr, uid, ids, context=context):
            res[pick.id] = 0
            for line in pick.move_lines:
                 if line.location_id.usage in ['inventory', 'production'] or line.location_dest_id.usage in ['inventory', 'production'] :
                    res[pick.id] = 1
                    break
                 else:
                    res[pick.id] = -1

        return res
                
    
    _columns = {
          'is_production'    : fields.function(_is_production, method=True,  type='integer', string='Is Production',store=True),
    }


    
stock_picking()
    


