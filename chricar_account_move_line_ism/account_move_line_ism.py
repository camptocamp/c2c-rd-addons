#!/usr/bin/python
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 20140830
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
from time import mktime
from datetime import datetime
import time
from osv import fields,osv
import pooler
from tools.translate import _
import logging



class ism_mandant(osv.osv):
    _name = "ism.mandant"

    _columns = {
      'mandant'   : fields.char    ('Mandant', size=8, required=True),
      'name'      : fields.char    ('Mandant', size=32, required=True),
      'company_id': fields.many2one('res.company', 'Company'),
    }

ism_mandant()

class ism_buchungsjahr(osv.osv):
    _name = "ism.buchungsjahr"

    def _mandant_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids= self.pool.get('ism.mandant').search(cr,uid,[('mandant','=',move.mandant) ])

            if len(res_ids):
                result[move.id] = res_ids[0]

        return result

    _columns = {
       'mandant'  : fields.char    ('Mandant', size=8, required=True),
       'code'              : fields.char    ('Code', size=64, required=True),
       'name'              : fields.char    ('Bezeichnung', size=16, required=True), 
       'mandant_id'        : fields.function(_mandant_id, method=True, string="Company",type='many2one', relation='ism.mandant', store=True, select="1",  ), 
       'company_id'        : fields.related
               ( "mandant_id"
               , "company_id"
               , type     = "many2one"
               , relation = "res.company"
               , string   = "Company"
               , store    = False
               )      ,
       'period_ids': fields.one2many('ism.periode','jahr_id','Perioden')
    }          

ism_buchungsjahr()

class ism_periode(osv.osv):
    _name = "ism.periode"


    def _mandant_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids= self.pool.get('ism.mandant').search(cr,uid,[('mandant','=',move.mandant) ])

            if len(res_ids):
                result[move.id] = res_ids[0]
        return result
                
    def _jahr_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids= self.pool.get('ism.buchungsjahr').search(cr,uid,[('mandant','=',move.mandant),('code','like',move.code[:4]) ])

            if len(res_ids):
                result[move.id] = res_ids[0]

        return result
    
    _columns = {
       'mandant'  : fields.char    ('Mandant', size=8, required=True),
       'mandant_id'        : fields.function(_mandant_id, method=True, string="Company",type='many2one', relation='ism.mandant', store=True, select="1",  ),
       'code'              : fields.char    ('Code', size=64, required=True),
       'name'              : fields.char    ('Periode', size=16, required=True), 
       
       'jahr_id'           : fields.function(_jahr_id, method=True, string="Year",type='many2one', relation='ism.buchungsjahr', store=True, select="1",  ), 
#       'jahr_id'           : fields.char    ('Jahr', size=16, required=False),
       'company_id'        : fields.related
               ( "mandant_id"
               , "company_id"
               , type     = "many2one"
               , relation = "res.company"
               , string   = "Company"
               , store    = False
               )    
    }          

ism_periode()


class ism_account(osv.osv):
    
    _logger = logging.getLogger(__name__)

    _name = "ism.account"
    
    def _mandant_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids= self.pool.get('ism.mandant').search(cr,uid,[('mandant','=',move.mandant) ])

            if len(res_ids):
                result[move.id] = res_ids[0]
        return result
          
    _columns = {
       'mandant'           : fields.char    ('Mandant', size=8, required=True),
       'code'              : fields.char    ('Code', size=16, required=True),
       'name'              : fields.char    ('Kontobezeichnung', size=50, required=True), 
       'mandant_id'        : fields.function(_mandant_id, method=True, string="Company",type='many2one', relation='ism.mandant', store=False, select="1",  ), 
       'company_id'        : fields.related
               ( "mandant_id"
               , "company_id"
               , type     = "many2one"
               , relation = "res.company"
               , string   = "Company"
               , store    = False
               )     ,
       'move_ids': fields.one2many('ism.buchungen','konto_id','Buchungen')
    }

ism_account()

class ism_belege(osv.osv):
    _name = "ism.belege"

    def _mandant_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids= self.pool.get('ism.mandant').search(cr,uid,[('mandant','=',move.mandant) ])

            if len(res_ids):
                result[move.id] = res_ids[0]
        return result


    def _jahr_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids = []
            result[move.id] = ''
            res_ids= self.pool.get('ism.buchungsjahr').search(cr,uid,[('mandant','=',move.mandant),('code','=',move.buchungsjahr) ])

            if len(res_ids):
                result[move.id] = res_ids[0]
        return result

    _columns = {
       'mandant'  : fields.char    ('Mandant', size=8, required=True),
       'mandant_id'        : fields.function(_mandant_id, method=True, string="Company",type='many2one', relation='ism.mandant', store=True, select="1",  ),     
       
       'name'              : fields.char    ('Beleg', size=8, required=False), 
       'beleg_text'        : fields.char    ('Beleg Text', size=8, required=True), 
       'buchungsjahr'      : fields.char    ('Buchungsjahr', size=5, required=True), 
       'jahr_id'           : fields.function(_jahr_id, method=True, string="Year",type='many2one', relation='ism.buchungsjahr', store=True, select="1",  ),     
       'company_id'        : fields.related
               ( "mandant_id"
               , "company_id"
               , type     = "many2one"
               , relation = "res.company"
               , string   = "Company"
               , store    = False
               ),
       'move_ids'          : fields.one2many('ism.buchungen','beleg_id','Buchungen')

    }

ism_belege()


class ism_buchungen(osv.osv):
    _name = "ism.buchungen"
    
    def _mandant_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids= self.pool.get('ism.mandant').search(cr,uid,[('mandant','=',move.mandant) ])

            if len(res_ids):
                result[move.id] = res_ids[0]
                
        return result


    def _period_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            res_ids= self.pool.get('ism.periode').search(cr,uid,[('company_id','=',move.company_id.id),('code','like',move.periode) ])

            if len(res_ids):
                result[move.id] = res_ids[0]

        return result
    
    def _beleg_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            result[move.id] = False
            konto_ids= self.pool.get('ism.belege').search(cr,uid,[('company_id','=',move.company_id.id),('name','=',move.beleg)])
            if len(konto_ids):
                result[move.id] = konto_ids[0]
        return result

    def _konto_id(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            result[move.id] = False
            konto_ids= self.pool.get('ism.account').search(cr,uid,[('company_id','=',move.company_id.id),('code','=',move.kontonummer)])
            if len(konto_ids):
                result[move.id] = konto_ids[0]
        return result

    def _debit(self, cr, uid, ids, name, arg, context):
        result = {}
        for move in self.browse(cr, uid, ids):
            result[move.id] = 0
            if move.amount >0:
                result[move.id] = move.amount

        return result

    def _credit(self, cr, uid, ids, name, arg, context):
        result = {}

        for move in self.browse(cr, uid, ids):
            result[move.id] = 0
            if move.amount <0:
                result[move.id] = move.amount

        return result
    

    _columns ={
       'mandant'  : fields.char    ('Mandant', size=8, required=True),
       'mandant_id'        : fields.function(_mandant_id, method=True, string="Company",type='many2one', relation='ism.mandant', store=True, select="1",  ),     


       'kontonummer'        : fields.char    ('Kontonummer', size=8, required=True),
       'konto_id'           : fields.function(_konto_id, method=True, string="Account",type='many2one', relation='ism.konto',  select="1", store=True ),
       'periode'            : fields.char    ('Periode', size=8, required=True),
       'periode_id'         : fields.function(_period_id, method=True, string="Period",type='many2one', relation='ism.periode', store=True, select="1",  ),
       'beleg'              : fields.char    ('Beleg', size=8, required=True),
       'beleg_id'           : fields.function(_beleg_id, method=True, string="Beleg",type='many2one', relation='ism.belege', store=True, select="1",  ),
       'amount'             : fields.float   ('Balance', required=True, digits=(16,2)),
       'name'               : fields.char    ('Text', size=128),
       'debit'              : fields.function(_debit, method=True, string="Debit",type='float', store=True, ),
       
       'credit'             : fields.function(_credit, method=True, string="Debit",type='float', store=True, ),
       'company_id'        : fields.related
               ( "mandant_id"
               , "company_id"
               , type     = "many2one"
               , relation = "res.company"
               , string   = "Company"
               , store    = False
               ),       
}

    _order = "name"
ism_buchungen()
