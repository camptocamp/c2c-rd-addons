# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    02-SEP-2011 (GK) created
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
import os.path
import unicode2ascii

class ir_model(osv.osv):
    _inherit = "ir.model"
    
    _unprintable = ["one2many", "many2many", "reference", "binary"]
 
    def _u2a \
        ( self
        , text
        , quote='"'
        , field_separator=","
        , line_separator="\n"
        ) :
        if not text : return ""
        txt = ""
        quoted = False
        for c in text:
            if ord(c) < 128 : txt += c
            elif c in unicode2ascii.EXTRA_LATIN_NAMES : txt += unicode2ascii.EXTRA_LATIN_NAMES[c]
            elif c in unicode2ascii.UNI2ASCII_CONVERSIONS : txt += unicode2ascii.UNI2ASCII_CONVERSIONS[c]
            elif c in unicode2ascii.EXTRA_CHARACTERS : txt += unicode2ascii.EXTRA_CHARACTERS[c]
            elif c in unicode2ascii.FG_HACKS : txt += unicode2ascii.FG_HACKS[c]
            else : txt+= "_"
        txt = txt.replace(quote, quote + quote)
        if field_separator in txt : quoted = True
        if line_separator in txt : quoted = True
        if quoted :
            return quote + txt + quote
        else :
            return txt
    # end def _u2a

    def generate_csv \
        ( self, cr, uid
        , table_obj
        , search=[]
        , header=True
        , field_separator=","
        , decimal_point="."
        , quote='"'
        , line_separator="\n"
        ) :

        result = []
# header
        if header :
            fields = []
            for k,v in table_obj._columns.items () :
                if k == "id" : continue # yes, this can happen!
                if v._type not in self._unprintable :
                    fields.append(self._u2a(v.string, quote, field_separator, line_separator))
            result.append(field_separator.join(fields))

        if search :
            where = " where %s" % (" and ".join('"%s" %s %s' % (s[0], s[1], s[2]) for s in search))
        else :
            where = ""
        sql = "select id from %s%s order by id;" % (table_obj._table, where)
        cr.execute(sql)
        res = cr.fetchall()
        for id in [x[0] for x in res] :
            obj = table_obj.browse(cr, uid, id) # reduce memory consumption!
            fields = []
            for k,v in table_obj._columns.items () :
                if k == "id" : continue # yes, this can happen!
                if v._type not in self._unprintable :
                    attr = getattr (obj, k)
                    if attr is False and v._type != "boolean" and v.required :
                        print _('No value for required attribute "%s" of table "%s" with id=%s.'
                                % (k, table_obj._name, id)
                               )
                    if v._type == "boolean" :
                        fields.append(str(attr))
                    elif attr is False :
                        fields.append("")
                    elif v._type == "float" :
                        fields.append(str(attr).replace(".", decimal_point))
                    elif v._type == "integer" :
                        fields.append(str(attr))
                    elif v._type in ["one2one", "many2one"] :
                        fields.append(self._u2a(attr.name, quote, field_separator, line_separator))
                    else :
                        fields.append(self._u2a(attr, quote, field_separator, line_separator))
            result.append(field_separator.join(fields))
        return line_separator.join(result)
    # end def generate_csv
# end class ir_model
ir_model()