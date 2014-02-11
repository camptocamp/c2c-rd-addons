# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    24-MAY-2011 (GK) created
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from lxml import etree
import os.path
from xml.sax.saxutils import escape

class ir_model(osv.osv):
    _inherit = "ir.model"

    transitive_type = ["one2many", "many2many", "one2one", "many2one", "function", "reference", "related"]

    def _unique_list(self, attr_obj) :
        for constr in attr_obj._sql_constraints :
            if "unique" in constr[1] :
                return (constr[1].replace(" ", "")[7:-1]).split(",")
        return []
    # end def _unique_list
    
    def _xml_attr_args(self, cr, table, type, model_list=None) :
        attr_model = None
        if model_list :
            for child in model_list.iter("table") :
                if child.text == table :
                    attr_model = child

        attr_obj = self.pool.get(table)
        result = []
        if type in ["one2one", "many2one", "reference"] :
            unique_list = self._unique_list(attr_obj)
            if attr_model is not None and "unique_list" in attr_model.attrib :
                for l in attr_model.get("unique_list").replace(" ", "").split(",") :
                    result.append({"name" :l, "type" : attr_obj._columns[l]._type})
            elif unique_list :
                for l in unique_list :
                    result.append({"name" : l, "type" : attr_obj._columns[l]._type})
            else :
                for l, w in attr_obj._columns.items () :
                    if hasattr(w, "_fnct") and w._fnct : continue
                    if w._type in self.transitive_type : continue
                    result.append({"name" : l, "type" : w._type})
        return result
    # end def _xml_attr_args

    def _xml_attr_search(self, cr, table_obj, model_list=None) :
        result = {}
        for k,v in table_obj._columns.items () :
            if v._obj : ###################################
                result[k] = self._xml_attr_args(cr, v._obj, v._type, model_list)
        return result
    # end def _xml_attr_search

    def generate_tree(self, cr, uid, table_obj, search=[], model_list=None):
        table = table_obj._name
        table_obj._log_access = True
        attr_search = self._xml_attr_search(cr, table_obj, model_list)

        root = etree.Element("openerp")
        data = etree.SubElement(root, "data")

        model = None
        if model_list :
            for child in model_list.iter("table") :
                if child.text == table :
                    model = child
        if model is not None and "order" in model.attrib :
            order = model.get("order")
        else :
            order = "id"
        if search :
            where = " where %s" % (" and ".join('"%s" %s %s' % (s[0], s[1], s[2]) for s in search))
        else :
            where = ""
        sql = "select id from %s%s order by %s;" % (table_obj._table, where, order)
        data.append(etree.Comment(sql))
        cr.execute(sql)
        res = cr.fetchall()
        for id in [x[0] for x in res] :
            obj = table_obj.browse(cr, uid, id) # reduce memory consumption!
            record = etree.SubElement(data, "record")
            record.set("model", table)
            code = "%s_%s" % (table_obj._table, obj.id)
            record.set("id", code)
            for k,v in table_obj._columns.items () :
                if k == "id" : continue # yes, this can happen!
                if hasattr(v, "_fnct") and v._fnct : continue
                search_list = []
                if v._type not in self.transitive_type :
                    attr = getattr (obj, k)
                    if attr is False and v._type != "boolean" and v.required :
                        print _('No value for required attribute "%s" of table "%s" with id=%s.'
                                % (k, table_obj._name, id)
                               )
                    if attr is not False or v._type == "boolean" :
                        field = etree.SubElement (record, "field")
                        field.set("name", k)
                        field.text = escape(unicode(attr))
                if v._type in ["one2one", "many2one"] :
                    attr = getattr (obj, k)
                    if not attr : continue
                    attr_model = v._obj
                    attr_obj = table_obj.pool.get(attr_model)
                    if k not in attr_search : continue
                    for search in attr_search[k] :
                        attr_attr = getattr (attr, search["name"])
                        search_list.append((search["name"], attr_attr, search["type"]))
                if v._type == "reference" :
                    attr = getattr (obj, k)
                    if attr is False : continue
                    attr_model = attr.split(",")[0]
                    attr_id    = attr.split(",")[1]
                    attr_obj = table_obj.pool.get(attr_model)
                    ids = attr_obj.search(cr, uid, [("id", "=", attr_id)])
                    if not ids :
                        print _('Table %s contains no entry with id=%s although %s with id=%s references it.' 
                                % (attr_model, attr_id, table, id))
                        raise osv.except_osv \
                            ( _('Data Inconsistency !')
                            , _('Table %s contains no entry with id=%s although %s with id=%s references it.' 
                                % (attr_model, attr_id, table, id))
                            )
                    attr_ref = attr_obj.browse(cr, uid, ids[0])
                    ref_search = self._xml_attr_args(cr, attr_model, v._type, model_list)
                    for search in ref_search :
                        attr_attr = getattr (attr_ref, search["name"])
                        search_list.append((search["name"], attr_attr, search["type"]))
                if search_list :
                    field = etree.SubElement (record, "field")
                    field.set ("name", k)
                    field.set ("model", attr_model)
                    args = []
                    for n, attr, t in search_list :
                        if attr is False and t != "boolean" : continue 
                        if t == "boolean" :
                            args.append("('%s', '=', %s)" % (n, attr))
                        elif t in ["one2one", "many2one", "reference"] :
                            args.append("('%s', '=', %s)" % (n, attr.id))
                        else :
                            args.append("('%s', '=', '''%s''')" % (n, attr))
                    field.set ("search", escape("[%s]" % ",".join(args)))
        return root        
    # end def generate_tree
# end class ir_model
ir_model()