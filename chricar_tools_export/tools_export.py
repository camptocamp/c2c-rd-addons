# -*- coding: utf-8 -*-
##############################################################################
#
#    Chricar Beteiligungs- und Beratungs- GmbH
#    Copyright (C) 2004-2010 Chricar Beteiligungs- und Beratungs- GmbH,
#    www.chricar.at
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging

class ir_model(osv.osv):

    #def _psql_csv_export(self, cr, uid, ids, field_name, arg, context=None):
    def _psql_csv_export(self, cr, uid, ids):
        res = {}
        ir_exports_obj = self.pool.get('ir.exports')
        ir_exports_line_obj = self.pool.get('ir.exports.line')
        for model in self.browse(cr, uid, ids, context):
            export_ids = ir_exports_obj.search(cr, uid, [('resource', '=', model.model)])
            ir_exports_obj.unlink(cr, uid, export_ids , context=context)
            ir_export_id = ir_exports_obj.create(cr, uid, {
                        'name': 'default_export',
                        'resource': model.model,
                        })
            m = model.model.replace('.','_')
            psql = "\o %s.csv"%(m)
            psql = psql +"\n\nselect \'%s_\'||id as id"%(m)
            t_exists = False
            cr.execute("select True from information_schema.tables where table_name='%s' " % (m))
            t_exists = bool(cr.fetchone())
            if t_exists:
             for field in model.field_id:
                f = field.name

                ir_exports_line_obj.create(cr, uid, {
                        'name' : f,
                        'export_id' : ir_export_id 
                        })

                export = False
                cr.execute("select True from information_schema.columns where table_name='%s' and column_name='%s'" % (m,f))
                f_exists = bool(cr.fetchone())
                if f_exists:
                  if field.required == True or field.ttype == 'text':
                    export = True
                  else:
                    cr.execute("select True from %s where \"%s\" is not null limit 1"% (m,f))
                    export = bool(cr.fetchone())

                  if field.ttype == 'many2one':
                       r = field.relation.replace('.','_')
                       f = "\'%s_\'||%s as \"%s:id\"" % (r,f,f)
                       export = True
                  else:
                       f = '"'+f+'"'
                if export == True:
                    psql = psql + '\n  , ' + f
                                
            psql = psql + '\n from '+ m + ';'
            res[model.id] = psql
        return res

    _inherit = 'ir.model'
    _logger = logging.getLogger(__name__)
    _columns = {
        #'psql_csv_export': fields.function(_psql_csv_export, method=True,string='PSQL Export SQL',type = 'text',store=True),
        'psql_csv_export': fields.text('PSQL Export SQL'),
        }

    def init(self, cr):
        uid = 1
        context = None
        model_obj = self.pool.get('ir.model')
        model_ids  = model_obj.search(cr,uid,'')        
        res = {}
        ir_exports_obj = self.pool.get('ir.exports')
        ir_exports_line_obj = self.pool.get('ir.exports.line')
        counter = 0.0
        for model in sorted(self.browse(cr, uid, model_ids, context)):
            counter +=1
            export_ids = ir_exports_obj.search(cr, uid, [('resource', '=', model.model),('name','=','default_export')])
            self._logger.debug('export_ids `%s` `%s` `%s` `%s`', counter, model.id, model.name, export_ids)
            if export_ids:
                export_line_ids = ir_exports_line_obj.search(cr, uid, [('export_id', 'in', export_ids)])
                if export_line_ids:
                    ir_exports_line_obj.unlink(cr, uid, export_line_ids , context=context)
                    self._logger.debug('export_ids `%s` `%s`', export_ids ,export_line_ids)
                ir_exports_obj.unlink(cr, uid, export_ids , context=context)
            ir_export_id = ir_exports_obj.create(cr, uid, {
                        'name': 'default_export',
                        'resource': model.model,
                        })
            m = model.model.replace('.','_')
            psql = "\o %s.csv"%(m)
            psql = psql +"\n\nselect \'%s_\'||id as id"%(m)
            t_exists = False
            cr.execute("select True from information_schema.tables where table_name='%s' " % (m))
            t_exists = bool(cr.fetchone())
            if t_exists:
             # FIXME should be sorted by field.name
             for field in sorted(model.field_id):
                f = field.name
                self._logger.debug('field `%s`', f)
                ir_exports_line_obj.create(cr, uid, {
                        'name' : f,
                        'export_id' : ir_export_id
                        })
                # FIXME remove continue, but then it hangs after 50 to 150 records
                #if counter > 50:
                #    continue
                export = False
                cr.execute("select True from information_schema.columns where table_name='%s' and column_name='%s'" % (m,f))
                f_exists = bool(cr.fetchone())
                if f_exists:
                  # use only fields with content
                  if field.required == True or field.ttype == 'text':
                    export = True
                  else:
                    cr.execute("select True from %s where \"%s\" is not null limit 1"% (m,f))
                    export = bool(cr.fetchone())
                  # m2o fields
                  if field.ttype == 'many2one':
                       r = field.relation.replace('.','_')
                       f = "\'%s_\'||%s as \"%s:id\"" % (r,f,f)
                       export = True
                  else:
                       f = '"'+f+'"'
                if export == True:
                    psql = psql + '\n  , ' + f

            psql = psql + '\n from '+ m + ';'
            self._logger.debug('model psql `%s` `%s`', model.name, psql)
            #FIXME write hangs
            model_obj.write(cr,uid,[model.id], {'psql_csv_export': psql})
 
        return True

ir_model()
