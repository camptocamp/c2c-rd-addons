# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    08-JUN-2012 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# 59 Temple Place - Suite 330, Boston, MA  02111-1.17, USA.
#
###############################################
from openerp.osv import fields, osv

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def _invoice(self, cr, uid, ids, name, arg, context=None) :
        return super(account_move_line, self)._invoice(cr, uid, ids, name, arg, context)

    def _invoice_search(self, cr, uid, obj, name, args, context={}) :
        """Redefinition for searching account move lines without any invoice related ('invoice.id','=',False)"""
        sql = """SELECT l.id FROM account_move_line l 
                    LEFT JOIN account_invoice i ON l.move_id = i.move_id 
                    WHERE i.id IS NULL"""
        for x in args:
            if (x[2] is False) and (x[1] == '=') and (x[0] == 'invoice') :
                cr.execute(sql)
                res = cr.fetchall()
                if not len(res):
                    return [('id', '=', '0')]
                return [('id', 'in', [x[0] for x in res])]
        return super(account_move_line, self)._invoice_search(cr, uid, obj, name, args, context=context)

    _columns = \
        { 'invoice': fields.function
            ( _invoice
            , method=True
            , string='Invoice'
            , type='many2one'
            , relation='account.invoice'
            , fnct_search=_invoice_search
            )
        }
account_move_line()
