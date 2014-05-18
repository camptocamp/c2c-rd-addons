# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2004-2013 ChriCar Beteiligungs- und Beratungs- GmbH (<http://camptocamp.com>).
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

class project(osv.osv):
    _inherit = "project.project"

    def _get_project_parent(self, cr, uid, id, context=None):
        res = {}
        if context is None:
            context = {}
        for proj in self.browse(cr, uid, [id], context):
            sql = """
            select pp.id 
             from project_project pp ,
                  account_analytic_account pa,
                  account_analytic_account a,
                  project_project p
            where p.id  = %s
              and a.id = p.analytic_account_id
              and pp.analytic_account_id = pa.id
              and a.parent_id = pa.id
        """ % (proj.id)
            cr.execute(sql)
            p_id = cr.fetchone() or ''
            res  = p_id

        return res
   
    _columns = {
         'project_child_ids' : fields.one2many('project.project', 'project_parent_id', 'Child Projects'),
         #'project_parent_id' : fields.function(_get_project_parent, method=True, string="Project Parent", store =True),
         'project_parent_id' : fields.many2one('project.project','Parent Project'),
      }

    def create(self, cr, uid, vals, context=None):
        res = super(project, self).create(cr, uid, vals, context);

        project_parent_id  = self._get_project_parent(cr, uid, res)
        super(project, self).write(cr, uid, res , {'project_parent_id':project_parent_id}, context)
        return res 

    def write(self, cr, uid, ids, vals, context=None):
        for proj in self.browse(cr, uid, ids, context):
            project_parent_id  = self._get_project_parent(cr, uid, proj.id)
            vals['project_parent_id'] = project_parent_id
            return super(project, self).write(cr, uid, [proj.id], vals,context)

project()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

