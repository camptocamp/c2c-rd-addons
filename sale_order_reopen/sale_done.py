# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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

# FIXME remove logger lines or change to debug
 
from osv import fields, osv
import netsvc
from tools.translate import _
import time
import logging


class sale_order(osv.osv):
    _inherit = 'sale.order'


    def action_done(self, cr, uid, ids, context=None):
        """ Changes SO to done.
        @return: True
        """
        _logger = logging.getLogger(__name__)

        _logger.info('FGF sale_order done %s' % (ids))

        for order in self.browse(cr, uid, ids):
            _logger.info('FGF sale_order done invoiced_rate %s' % (order.invoiced_rate))
            if order.invoiced_rate > 99 and order.invoiced is True and order.state not in  ['done','cancel']:
            #if order.invoiced_rate == 1 and order.invoiced is True: 

                self.write(cr, uid, order.id, {'state':'done','shipped':True})

            #self.log_sale(cr, uid, ids, context=context)  
            
        return True

    def action_unset_uninvoiced_lines(self, cr, uid, ids, context=None):
        """ Changes SO uninvoiced_lines to False.
        @return: True
        """
        _logger = logging.getLogger(__name__)


        for order in self.browse(cr, uid, ids):
            _logger.info('FGF sale_order invoiced_lines %s' % (order.uninvoiced_lines))
            if order.uninvoiced_lines is True and order.invoiced is True and order.state == 'done':

                self.write(cr, uid, order.id, {'uninvoiced_lines':False})


        return True
    
sale_order()
    


