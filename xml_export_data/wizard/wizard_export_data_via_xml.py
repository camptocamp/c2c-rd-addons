# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    09-MAY-2011 (GK) created
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
import wizard
#import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from lxml import etree
import os.path
import time
from xml.sax.saxutils import escape

class wizard_export_data(wizard.interface):
    
    def generate_tree(self, cr, uid, table_obj):
        pool = pooler.get_pool(cr.dbname)
        model_obj = pool.get("ir.model")
        return model_obj.generate_tree(cr, uid, table_obj, model_list=self.model_list)
    # end def generate_tree
    
    def write_xml (self, root, file_name, pretty_print=True) :
        try :
            f = open (file_name, "w")
            try :
                f.write(etree.tostring(root, pretty_print=pretty_print))
            finally :
                f.close ()
        except (SystemExit, KeyboardInterrupt), exc :
            raise
    # end def write_xml

    def add_model(self, cr, uid, models, model) :
        pool = pooler.get_pool(cr.dbname)
        if model not in models:
            models[model] = set()
            table_obj = pool.get(model)
            if not table_obj :
                raise wizard.except_wizard \
                    ( _('Data Error !')
                    , _('Data model contains unknown table  %s.' % model)
                    )
            for l, w in table_obj._columns.items () :
#                print w, w._properties, w.string, dir(w) ###########################################################
                if hasattr(w, "_fnct") and w._fnct : continue
                if w._type in ["one2one", "many2one"] : 
                    if w._obj != model :
                        models[model].add(w._obj)
                    self.add_model(cr, uid, models, w._obj)
                if w._type == "reference" :
                    for obj in table_obj.browse(cr, uid, table_obj.search (cr, uid, [])):
                        attr = getattr (obj, l)
                        if attr :
                            new_model = attr.split(",")[0]
                            if new_model == model : continue
                            self.add_model(cr, uid, models, new_model)
                            models[model].add(new_model)
    # end def add_model

    def write_model(self, models, file_name) :
        root = etree.Element("model")
        for model in sorted(models.keys()) :
            values = models[model]
            ti = etree.SubElement(root, "table")
            ti.text = model
            for value in values :
                tiv = etree.SubElement(ti, "depends")
                tiv.text = value
        f = open(file_name, "w")
        f.write(etree.tostring(root, pretty_print=True))
        f.close()
#   end def write_model

    def _all(self, cr, uid, data, context=None):
        pool = pooler.get_pool(cr.dbname)
        path = "/Daten/Migration/"
        
        initial = {}
        model_obj = pool.get("ir.model")
        for model in model_obj.browse(cr, uid, model_obj.search(cr, uid, [])) :
            if "ir." in model.model and model.model not in ("ir.sequence", "ir.attachment"): continue
            if "res.config.view" in model.model : continue
            if "config.compute.remaining" in model.model : continue
            if "sale.config.picking_policy" in model.model : continue
            if "process." in model.model : continue
            if "wizard" in model.model : continue
            if "workflow" in model.model : continue
            if "report" in model.model : continue
#            if "audittrail" in model.model : continue # XXX
            table_obj = pool.get(model.model)
            if table_obj is None : continue
            if isinstance(table_obj, osv.osv_memory) : continue
            cr.execute("SELECT count(*) FROM %s;" % table_obj._table)
            res = cr.fetchall()[0][0]
#            print model.model, res ###############
            if res > 0 :
                initial[model.model] = []
        self.write_model(initial, os.path.join(path, "__initial__.xml"))
            

        tables = set()
        file = os.path.join(path, '__model__.xml')
        if os.path.exists(file):
            f = open(file, "r")
            self.model_list = etree.parse(f)
            f.close()
            for child in self.model_list.iter("table") :
                tables.add(child.text)
         
        ignore = set()
        file = os.path.join(path, '__ignore__.xml')
        if os.path.exists(file):
            f = open(file, "r")
            ignore_list = etree.parse(f)
            f.close()
            for child in ignore_list.iter("table") :
                ignore.add(child.text)
        models = {}
        for t in tables :
            self.add_model(cr, uid, models, t)
            
        self.write_model(models, os.path.join(path, "__manifest__.xml"))

        for ign in ignore :
            if ign in models :
                del models[ign]
        for model, values in models.iteritems() :
            models[model] = values.difference(ignore)
            
        root = etree.Element("model")
        old_len = len(models)
        while len(models) > 0 :
            for model in models.keys() :
                if len(models[model]) == 0 :
                    ti = etree.SubElement(root, "table")
                    ti.text = model
                    del models[model]
                    for m, v in models.iteritems() :
                        models[m] = v.difference(set([model]))
            if old_len == len(models) :
                file_name = os.path.join(path, "__error__.xml")
                self.write_model(models, file_name)
                raise wizard.except_wizard \
                    ( _('Data Error !')
                    , _('Data model contains circularities. See %s for more information.' % file_name)
                    )
            else :
                old_len = len(models)
        file_name = os.path.join(path, "__error__.xml")
        self.write_model(models, file_name)
        f = open(path + "__import__.xml", "w")
        f.write(etree.tostring(root, pretty_print=True))
        f.close()

        for model in ignore :
            if os.path.exists(os.path.join(path, model + ".xml")): continue ###################
            print "write_xml", model ##################
            self.write_xml \
                (self.generate_tree
                    ( cr
                    , uid
                    , pool.get(model)
                    )
                , file_name = os.path.join(path, model + ".xml")
                , pretty_print = True
                )

        elapsed = 0.0
        for child in root.iter("table") :
            model = child.text
            if os.path.exists(os.path.join(path, model + ".xml")): continue ###################
            print "write_xml", model, ##################
            t0 = time.time()
            c0 = time.clock()
            tmp = self.generate_tree \
                    ( cr
                    , uid
                    , pool.get(model)
                    )
            self.write_xml \
                ( tmp
                , file_name = os.path.join(path, model + ".xml")
                , pretty_print = False
                )
            print time.clock() - c0, ###############
            elap = time.time() - t0
            print elap ################
            elapsed += elap
        print "Export done in ", int(elapsed), " seconds"###################
        return {'result' : {'type' : 'state', 'state' : 'end'}}
    # end def _all

    states = \
        { 'init' : 
            { 'actions' : []
            , 'result'  : 
                { 'type'   : 'action'
                , 'action' : _all
                , 'state'  : 'end'
                }
            }
        }
wizard_export_data("ir.wizard_export_data_via_xml")
