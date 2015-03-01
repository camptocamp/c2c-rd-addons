# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    28-NOV-2011 (GK) created
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
from openerp.osv import fields,osv
from openerp.tools.translate import _

import logging
logger = logging.getLogger(__name__)

class Look_Ahead_Gen(object):

    is_finished = property (lambda s: not s)
    
    def __init__(self, source):
        self.source = source = iter(source)
        self._sentinel = self.succ = object()
    # end def __init__
    
    def __nonzero__(self):
        try :
            if self.succ is self._sentinel:
                self.succ = self.source.next()
        except StopIteration :
            return False
        return True
    # end def __nonzero__

    def __iter__(self):
        source = self.source
        _sentinel = self._sentinel
        while True:
            if self.succ is _sentinel :
                next = source.next()
            else :
                next = self.succ
                self.succ = _sentinel
            yield next
    # end def __iter__
# end class Loop_Ahead_Gen

def pairwise(seq):
    lag = Look_Ahead_Gen(seq)
    for h in lag :
        if lag:
            yield h, lag.succ
# end def pairwise

def period_overlaps (my, other):
    m_b = my.from_date
    m_e = my.to_date
    o_b = other.from_date
    o_e = other.to_date
    if m_b :
        if o_b :
            if o_e :
                return o_b <= m_b and m_b <= o_e
            else :
                return o_b <= m_b
        elif o_e :
            return m_b <= o_e
    elif m_e :
        if o_b :
            return o_b <= m_e
    return True
# end def _period_overlaps

def date_overlaps (my_from_date, my_to_date, other_from_date, other_to_date):
    m_b = my_from_date
    m_e = my_to_date
    o_b = other_from_date
    o_e = other_to_date
    if m_b :
        if o_b :
            if o_e :
                return o_b <= m_b and m_b <= o_e
            else :
                return o_b <= m_b
        elif o_e :
            return m_b <= o_e
    elif m_e :
        if o_b :
            return o_b <= m_e
    return True
# end def _date_overlaps

class constraint_predicate(osv.osv):
    _name = "constraint.predicate"

    _columns  = \
        { 'company_id': fields.many2one('res.company', 'Company', required=True)
        , 'condition' : fields.char 
            ('Condition'
            , required = True
            , size     = 256
            , help     = "Python expression that evaluates to 'True' if the condition is fulfilled, else 'False'"
            )
        , 'enable'    : fields.boolean('Enable', required=True)
        , 'filter'    : fields.char
            ( 'Filter'
            , size=256
            , help="Python expression. If it evaluates to 'True' then the Condition is checked"
            )
        , 'name'      : fields.char('Error Message', required=True, size=128, translate=True)
        , 'object'    : fields.char('Object Name', required=True, size=32)
        , 'table'     : fields.char('Table', required=True, size=32)
        }
    _defaults = \
        { 'company_id' : lambda s, cr, uid, c: s.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.id # V5.0
#V6.1        , 'company_id' : lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'ir.sequence', context=c)
        , 'enable' : lambda *a : True
        }
    _msg = []

    def test_obj (self, cr, uid, rule, obj) : pass # let the heirs do the work

    def test (self, cr, uid, rule) :
        result = []
        c_obj = self.pool.get (rule.table)
        c_ids = c_obj.search (cr, uid, [])
        for obj in c_obj.browse (cr, uid, c_ids) :
            has_company = 'company_id' in c_obj._columns
            if not has_company or (obj.company_id == rule.company_id) :
                result.extend(self.test_obj(cr, uid, rule, obj))
        return result
    # end def test

    def button_test (self, cr, uid, ids, id) :
        result = []
        for c in self.browse (cr, uid, ids) :
            result.extend(self.test(cr, uid, c))
        if result :
            raise osv.except_osv (_('%s Rule Error(s) !' % len(result)), _('\n'.join (result)))
        else :
            raise osv.except_osv (_('Rule successfully tested !'), _('No errors found.'))
    # end def button_test
    
    def button_start (self, cr, uid, ids, id) :

        def _check_constraint_func(self, cr, uid, ids):
            constr_one_obj = self.pool.get ("constraint.check_one")
            constr_all_obj = self.pool.get ("constraint.check_for_all")
            self._msg = []
            selection = [("table","=", self._name), ("enable", "=", True)]
            for obj in self.browse(cr, uid, ids) :
                for rule in constr_one_obj.browse(cr, uid, constr_one_obj.search(cr, uid, selection)) :
                    result = constr_one_obj.test_obj(cr, uid, rule, obj)
                    if result : 
                        self._msg.append("\n".join(result))
                for rule in constr_all_obj.browse(cr, uid, constr_all_obj.search(cr, uid, selection)) :
                    result = constr_all_obj.test_obj(cr, uid, rule, obj)
                    if result :
                        self._msg.append("\n".join(result))
            if self._msg :
                self._msg = "\n".join(self._msg)
                print ">>>>Constraint check failed: ", self._msg ################
                return False
            else :
                return True
        # end def _check_constraint_func

        self._msg = []
        model_obj = self.pool.get("ir.model")
        for name in model_obj.browse(cr, uid, model_obj.search(cr, uid, [])) :
            model = name.model
            table_obj = self.pool.get(model)
            if table_obj is None : continue
            if "ir." in model and model not in ("ir.sequence", "ir.attachment") : continue
            if "audittrail." in model: continue
            if "base." in model: continue
            if isinstance(table_obj, osv.osv_memory) : continue
            has_it = False
            for constr in table_obj._constraints :
                if constr[0].func_name == _check_constraint_func.func_name : 
                    has_it = True
                    continue
            if not has_it :
                table_obj._constraints.append((_check_constraint_func, "See server log!", []))
            logger.info('model %s' , model)
            logger.info('model constraints %s' , table_obj._constraints)

    # end def button_start

    def button_stop (self, cr, uid, ids, id) :
        model_obj = self.pool.get("ir.model")
        for name in model_obj.browse(cr, uid, model_obj.search(cr, uid, [])) :
            model = name.model
            table_obj = self.pool.get(model)
            if table_obj is None : continue
            l = []
            logger.info('model %s' , model)
            for constr in table_obj._constraints :
                logger.info('constr %s' , constr)
                logger.info('constr[0] %s' , constr[0])
                try:
                    if constr[0].func_name != "_check_constraint_func" :
                        l.append(constr)
                except:
                    l.append(constr)
            logger.info('constraints %s' , l)
            table_obj._constraints = l
            logger.info('model constraints %s' , table_obj._constraints)
    # end def button_stop

constraint_predicate ()

class constraint_check_one (osv.osv):
    _name     = "constraint.check_one"
    _inherit  = "constraint.predicate"

    def test_obj (self, cr, uid, rule, obj) :
        result = []
        c_obj = self.pool.get (rule.table)
        ctx = \
            { rule.object       : obj
            , 'pairwise'        : pairwise
            , 'date_overlaps'   : date_overlaps
            , 'period_overlaps' : period_overlaps
            }
        if rule.filter :
            if eval (rule.filter, {rule.object : obj}):
                if not eval (rule.condition, ctx):
                    name = getattr(obj, c_obj._rec_name, "")
                    result.append('%s "%s": %s' % (c_obj._description, name, rule.name))
        else :
            if not eval (rule.condition, ctx):
                name = getattr(obj, c_obj._rec_name, "")
                result.append('%s "%s": %s' % (c_obj._description, name, rule.name))
        return result
    # end def test

constraint_check_one ()

class constraint_check_for_all (osv.osv):
    _name     = "constraint.check_for_all"
    _inherit  = "constraint.predicate"

    _columns  = \
        { 'sequence' : fields.char ('Sequence', size=256, required=True, help="Python expression that evaluates to a list")
        , 'var'      : fields.char ('Variable Name', size=32,  required=True)
        }

    def test_obj (self, cr, uid, rule, obj) :
        result = []
        c_obj = self.pool.get (rule.table)
        dict = \
            { rule.object       : obj
            , 'pairwise'        : pairwise
            , 'date_overlaps'   : date_overlaps
            , 'period_overlaps' : period_overlaps
            }
        if rule.filter :
            if eval (rule.filter, dict):
                seq = eval (rule.sequence, dict)
                for elem in seq :
                    ctx = {rule.var : elem}
                    ctx.update(dict)
                    if not eval (rule.condition, ctx):
                        name = getattr(obj, c_obj._rec_name, "")
                        ename = getattr(elem, "name", "")
                        result.append('%s "%s": %s "%s"' % (c_obj._description, name, rule.name, ename))
        else :
            seq = eval(rule.sequence, dict)
            for elem in seq :
                ctx = {rule.var : elem}
                ctx.update(dict)
                if not eval (rule.condition, ctx):
#                    try :
#                        it = iter(elem)
#                        e = [o.name for o in elem]
#                    except TypeError :
                    name = getattr(obj, c_obj._rec_name, "")
                    ename = getattr(elem, "name", "")
                    result.append('%s "%s": %s "%s"' % (c_obj._description, name, rule.name, ename))
        return result
    # end def test_obj

constraint_check_for_all ()
