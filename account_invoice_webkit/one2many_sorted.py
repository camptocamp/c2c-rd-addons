# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    06-APR-2012 (GK) created
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
# 59 Temple Place - Suite 330, Boston, MA  02111-1.17, USA.
#
###############################################
from osv import fields,osv
from tools.translate import _

class one2many_sorted (fields.one2many):
    
    def __init__(self, obj, fields_id, string='unknown', limit=None, **args) :
        if 'order' in args :
            order = []
            for col in args['order'].split(',') :
                c = col.strip()
                if ' ASC' in c.upper() :
                    order.append((c[0:c.index(' ')], False))
                elif ' DESC' in c.upper() :
                    order.append((c[0:c.index(' ')], True))
                else :
                    order.append((c, False))
            self._order = list(reversed(order))
        else :
            self._order = []
        if 'search' in args :
            self._search = args['search']
        else :
            self._search = []
        if 'set' in args :
            self._set = args['set']
        else :
            self._set = {}
        (fields.one2many).__init__(self, obj, fields_id, string=string, limit=limit, **args)
    # end def __init__

    def get (self, cr, obj, ids, name, user=None, offset=0, context=None, values={}) :
        res = {}
        _obj = obj.pool.get(self._obj)
        for id in ids : res[id] = []
        ids2 = _obj.search \
            ( cr, user
            , [(self._fields_id, 'in', ids)] + self._search
            , limit = self._limit
            )
        undecorated = []
        for r in _obj.browse(cr, user, ids2, context=context) :
            d = {}
            for key in ([('id', False)] + self._order) :
                o = r
                for m in key[0].split('.'):
                    if "()" in m :
                        o = getattr(o, m.strip("()"))()
                    else :
                        o = getattr(o, m)
                d[key[0]] = o if not isinstance(o, str) else _(o)
            undecorated.append(d)
        for key in self._order :
            decorated = [(d[key[0]], d) for d in undecorated]
            decorated.sort(reverse=key[1])
            undecorated = [d for (k, d) in decorated]
        for r in _obj.browse(cr, user, [d['id'] for d in undecorated], context=context) :
            res [getattr(r, self._fields_id).id].append(r.id)
        return res
    # end def get

    def set(self, cr, obj, id, field, values, user=None, context=None):
        for act in values :
            if act[0] == 0 : # "create"
                for k, v in self._set.iteritems() :
                    act[2][k] = v
        return super(self.__class__,self).set(cr, obj, id, field, values, user, context)
    # end def set
# end class one2many_sorted
