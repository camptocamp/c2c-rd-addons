# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    26-JUL-2011 (GK) created
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
{ 'sequence': 500,
"name"         : "Tool for generating XML-files from a template"
, "version"      : "1.1"
, "author"       : "Swing Entwicklung betrieblicher Informationssysteme GmbH"
, "website"      : "http://www.swing-system.com"
, "description"  : """
Generates XML-Files from a Template

The structure and features of the XML-Template:

The XML-template ist copied "as-is" to the output XML-file:

|  <MyTag1>
|    <MyTag2 my-attribute="foo">
|      My Body
|    </MyTag2>
|  </MyTag1>

yields:

|  <MyTag1>
|    <MyTag2 my-attribute="foo">
|      My Body
|    </MyTag2>
|  </MyTag1>


Additional control-attributes allow to fill the output XML with data from the data-model:

|  <MyTag1>
|    <MyTag2 attr-name1="foo" attr-eval="root.foo">
|      <MyTag3 text-eval="root.bar"/>
|    </MyTag2>
|  </MyTag1>

will produce:

|  <MyTag1>
|    <MyTag2 foo="FOO">
|      <MyTag3>BAR</MyTag3>
|    </MyTag2>
|  </MyTag1>

provided that the Python expression "root.foo" will return "FOO" and "root.bar" will return "BAR"
I.e., "attr-name[0-9]" provides an attribute-name and "attr-eval[0-9]" provides a Python-expression.
The "[0-9]" can be any integer as long as "name" and "eval" matches.

List-iterations can be provided with the attributes "loop-eval" and "var":

|  <MyTag1>
|    <MyTag2 loop-eval="[1,2,4]" var="number">
|      <MyTag3 text-eval="number"/>
|    </MyTag2>
|  </MyTag1>

will produce

|  <MyTag1>
|    <MyTag2>
|      <MyTag3>1</MyTag3>
|      <MyTag3>2</MyTag3>
|      <MyTag3>4</MyTag3>
|    </MyTag2>
|  </MyTag1>

A variant of this, "seq-eval" is necessary, if there is no surrounding tag for the list
(which is a weak XML-design - but cannot be excluded):

|  <MyTag1>
|    <MyTag2 seq-eval="[1,2,4]" var="number">
|      <MyTag3 text-eval="number"/>
|    </MyTag2>
|  </MyTag1>

will produce

|  <MyTag1>
|    <MyTag3>1</MyTag3>
|    <MyTag3>2</MyTag3>
|    <MyTag3>4</MyTag3>
|  </MyTag1>

The option "omit_on_empty" is used, if the surrounding tag shall be omitted with empty lists:

|  <MyTag1>
|    <MyTag2 loop-eval="[]" var="number" omit_on_empty="True">
|      <MyTag3 text-eval="number"/>
|    </MyTag2>
|  </MyTag1>

will produce

|  <MyTag1>
|  </MyTag1>

On the other hand: 

|  <MyTag1>
|    <MyTag2 loop-eval="[]" var="number" omit_on_empty="False">
|      <MyTag3 text-eval="number"/>
|    </MyTag2>
|  </MyTag1>

will produce

|  <MyTag1>
|    <MyTag2>
|    </MyTag2>
|  </MyTag1>


The programmatic interface (API) of the XML-Template:

def generate_xml(self, cr, uid, id, nsmap=None, \*\*scope_dict)

returns the output XMl. If a schema is provided, the validity is checked.

def attach_xml(self, cr, uid, id, attach_to, xml, name, fname, description, context)

creates an attachment from the output XML and attaches it to another object.

def write_file(self, cr, uid, id, xml, filename)

writes the output XML to a (server-side) provided file.


Example-Code (generate a XML for an invoice and attach it to that invoice):


|        template_obj = self.pool.get("xml.template")
|        template_ref_obj = self.pool.get("xml.template.ref")
|        template_refs = template_ref_obj.browse \
|            ( cr, uid
|            , template_ref_obj.search
|                (cr, uid, [("name", "=", "%s,%s" % (invoice._name, invoice.id))])
|            )
|        if not template_refs :
|            raise osv.except_osv \
|                ( _('Data Error !')
|                , _('No Template defined for Invoice ') + invoice.name
|                )
|
|        template_ref = template_refs[0]
|        xml = template_obj.generate_xml \
|            (cr, uid
|            , template_ref.xml_template_id.id
|            , invoice     = invoice
|            , partner     = partner
|            , time        = time.strftime("%Y-%m-%d %H:%M:%S")
|            )
|
|        template_obj.attach_xml \
|            ( cr, uid
|            , template_ref.xml_template_id.id
|            , attach_to   = invoice
|            , xml         = xml
|            , name        = invoice.name
|            , fname       = invoice.name + ".xml"
|            , description = "XML file representing this invoice"
|            )
"""
, "category"     : "Tool"
, "depends"      : ["base"]
, "init_xml"     : []
, "demo"         : []
, "data"   : 
[ "security/ir.model.access.csv"
, "xml_template_view.xml"
, "ir_attachment_view.xml"
]
, "test"         : []
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
