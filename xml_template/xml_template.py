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
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import XML_Generator
import base64
from lxml import etree

class xml_template(osv.osv):
    _name           = "xml.template"
    _description    = "XML Template"
    _order          = "name"

    _columns  = \
        { "comment"        : fields.text("Comment")
        , "content"        : fields.text("Content", required=True, help="Contains XML-template specification")
        , "name"           : fields.char("Name", size=256, required=True)
        , "schema"         : fields.char("XML schema", size=256, help="Generated XML-file will be checked against this")
        , "reference_ids"  : fields.one2many("xml.template.ref", "xml_template_id", "References")
        , "regulation_ids" : fields.one2many("xml.template.url", "xml_template_id", "Regulations")
        , "valid_from"     : fields.date("Valid from")
        , "valid_to"       : fields.date("Valid to")
        }
    _sql_constraints = \
        [( "xml_template_name_index"
         , "unique (name)"
         , "The Name has to be unique!"
         )
        ]

    def button_generate_template(self, cr, uid, ids, id):
        for obj in self.browse(cr, uid, ids) :
            if obj.schema :
                parser = etree.XMLParser(no_network=False)
                schema_root = etree.parse(obj.schema, parser)
                if ".xsd" in obj.schema.lower() :
                    xslt_root   = etree.parse("http://www.swing-system.com/xsl/xsd2xml.xsl", parser) # can be optimized as function field!
                elif ".rng" in obj.schema.lower() :
                    xslt_root   = etree.parse("http://www.swing-system.com/xsl/rng2xml.xsl", parser) # can be optimized as function field!
                else :
                    raise osv.except_osv \
                        ( _("Data Error !")
                        , _("Unknown schema type: %s" % obj.schema)
                        )
                transform   = etree.XSLT(xslt_root)
                template    = transform(schema_root)
                self.write(cr, uid, [obj.id], {'content' : template})
    # end def button_generate_template

    def generate_xml(self, cr, uid, id, nsmap=None, **scope_dict) :
        """Generates the XML and returns it
        
        :param nsmap: (dictionary of) namespaces
        :param scope_dict: (dictionary of) navigation roots 
        :return: root of XML-structure
        """
        obj = self.browse(cr, uid, id)
        if obj and obj.content :
            generator = XML_Generator.XML_Generator(obj.content, nsmap) # can be optimized as function field!
            xml = generator.generate(**scope_dict)
            if obj.schema :
                self.is_schema_valid(cr, uid, id, xml)
            return xml
        raise osv.except_osv \
            ( _("Data Error !")
            , _("Invalid Template with ID: %s" % id)
            )
    # end def generate_xml

    def is_schema_valid(self, cr, uid, id, xml) :
        """Checks the validity of the provided XML according to the specified schema
        
        :param xml: root of XML-structure to be checked 
        :return: Boolean
        """
        obj = self.browse(cr, uid, id)
        if obj and obj.schema :
            parser = etree.XMLParser(no_network=False)
            schema_root = etree.parse(obj.schema, parser)
            if ".xsd" in obj.schema.lower() :
                schema = etree.XMLSchema(schema_root)
            elif ".rng" in obj.schema.lower() :
                schema = etree.RelaxNG(schema_root)
            else :
                raise osv.except_osv \
                    ( _("Data Error !")
                    , _("Unknown schema type: %s" % obj.schema)
                    )
            return schema.validate(xml)
        raise osv.except_osv \
            ( _("Data Error !")
            , _("Invalid Template with ID: %s" % id)
            )
    # end def is_schema_valid

    def _remove_attachments(self, cr, uid, attach_to, name, fname, description, context=None) :
        attachment_obj = self.pool.get('ir.attachment')
        att_ids = attachment_obj.search \
            ( cr, uid
            , [ ('res_model', '=', attach_to._table_name)
              , ('res_id', '=', attach_to.id)
              , ('name', '=', name)
              , ('description', '=', description)
              , ('datas_fname', '=', "%s.xml" % fname)
              ]
            )
        if att_ids :
            attachment_obj.unlink(cr, uid, att_ids, context=context)
    # end def _remove_attachments

    def attach_xml(self, cr, uid, id, attach_to, xml, name, fname, description=False, pretty_print=False, context=None) :
        """ Creates an attachment and returns its ID
        
        Note that attachments with identical name/filename/description will be replaced
        
        :param attach_to: object that receives the attachment
        :param xml: root of XML-structure that will be attached
        :param name: name of the attachment
        :param fname: filename of the attachment (without extension .xml)
        :param description: description of the attachment
        :param pretty_print: True/False
        :param context: dictionary or None
        :return: ID of new attachment object 
        """
        obj = self.browse(cr, uid, id)
        if not obj :
            raise osv.except_osv \
                ( _("Data Error !")
                , _("Invalid Template with ID: %s" % id)
                )
        attachment_obj = self.pool.get('ir.attachment')
        attach_ref_obj = self.pool.get('ir.attachment.ref')
        self._remove_attachments(cr, uid, attach_to, name, fname, description, context=context)
        vals  = \
            { 'name'         : name
            , 'datas'        : base64.encodestring('<?xml version="1.0" encoding="UTF-8"?>\n' + etree.tostring(xml, pretty_print=pretty_print))
            , 'datas_fname'  : "%s.xml" % fname
            , 'res_model'    : attach_to._table_name
            , 'res_id'       : attach_to.id
            , 'description'  : description
            }
        res = attachment_obj.create(cr, uid, vals, context=context)
        for reference in obj.reference_ids :
            vals = \
                { "ir_attachment_id" : res
                , "name"             : reference.name._table_name + "," + str(reference.name.id)
                }
            attach_ref_obj.create(cr, uid, vals, context=context)
        return res
    # end def attach_xml

    def write_file(self, cr, uid, id, xml, filename, pretty_print=True) :
        """Writes the XML to the specified filename
        
        :param xml: root of XML-structure to be written
        :param filename: full file name
        :param pretty_print: True/False
        """
        f = open(filename, "w")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(etree.tostring(xml, pretty_print=pretty_print))
        f.close()
    # end def write_file
# end class xml_template
xml_template()

class xml_template_url(osv.osv):
    _name           = "xml.template.url"
    _description    = "XML Template URL"
    _order          = "name"

    _columns  = \
        { "xml_template_id" : fields.many2one("xml.template", "XML Template", required=True, ondelete="cascade")
        , "name"            : fields.char("URL", size=256, required=True)
        }
# end class xml_template_url
xml_template_url()

class xml_template_ref(osv.osv):
    _name           = "xml.template.ref"
    _description    = "XML Template Reference"
    _order          = "name"

    def _links_get(self, cr, uid, context={}) :
        obj = self.pool.get("res.request.link")
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ["object", "name"], context)
        return [(r["object"], r["name"]) for r in res]
    # ende def _links_get

    _columns  = \
        { "xml_template_id" : fields.many2one("xml.template", "XML Template", required=True, ondelete="cascade")
        , "name"            : fields.reference('Reference', selection=_links_get, size=128, required=True)
        }
# end class xml_template_ref
xml_template_ref()
