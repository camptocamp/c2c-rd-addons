# -*- coding: utf-8 -*-
##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    24-JUN-2009 (GK) created
#    02-AUG-2009 (GK) Interface changed from file to string
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
from lxml import etree
import logging

class XML_Generator (object) :
    _logger = logging.getLogger('XML_Generator')

    def __init__ (self, template, nsmap=None) :
        self.root  = etree.fromstring (template)
        self.nsmap = nsmap
    # end def __init__
    
    def generate (self, **scope_dict) : 
        if self.nsmap :
            root = etree.Element (self.root.tag, self.root.attrib, nsmap = self.nsmap)
        else :
            root = etree.Element (self.root.tag, self.root.attrib)
        self.out = etree.ElementTree (root)
        self._iterate (self.root, root, scope_dict)
        return self.out
    # end def generate
    
    def write (self, xml_file, pretty = True) :
        from xml.dom.ext import PrettyPrint
        from xml.dom.ext.reader.Sax import FromXmlFile

        try :
            f = open (xml_file, "w")
            try :
                self.out.write (f)
            finally :
                f.close ()
        except (SystemExit, KeyboardInterrupt), exc :
            raise
        
        if pretty :
            doc = FromXmlFile (xml_file)
            try :
                f = open (xml_file, "w")
                try :
                    PrettyPrint (doc, f)
                finally :
                    f.close ()
            except (SystemExit, KeyboardInterrupt), exc :
                raise
    # end def write

    def _iterate (self, elm, out, scope_dict) :
        for name,value in out.items () :
            if name [0:9] == "attr-name" :
                del out.attrib[name]
                del out.attrib["attr-eval" + name [9:]]
        for name, value in elm.items () :
            if name [0:9] == "attr-name" :
                nr = name [9:]
                try :
                    val = eval (elm.attrib ["attr-eval" + nr], scope_dict)
                    out.set (elm.attrib [name], unicode (val))
                except :
                    self._logger.error('ERROR in attr-eval for `%s` `%s` `%s`', elm.tag, name, elm.attrib["attr-eval" + nr])
                    raise 
            elif name [0:9] == "attr-eval" : pass
            elif name == "text-eval":
                try :
                    out.text = unicode (eval (value, scope_dict))
                except : 
                    self._logger.error('ERROR in text-eval for `%s` `%s` `%s`', out.tag, name, value)
                    raise
        for c in elm.getchildren () :
            if "loop-eval" in c.attrib :
                try :
                    objs = eval \
                        ("[(%s) for %s in (%s)]" % 
                            ( c.attrib["var"]
                            , c.attrib["var"]
                            , c.attrib["loop-eval"]
                            )
                        , scope_dict 
                        )
                except :
                    self._logger.error('ERROR in loop-eval for `%s` `%s`', c.tag, c.attrib["loop-eval"])
                    raise
                if not ("omit_on_empty" in c.attrib and c.attrib["omit_on_empty"] == "True" and not objs) :
                    x = etree.SubElement (out, c.tag)
                    for o in objs :
                        scope_dict [c.attrib["var"]] = o
                        self._iterate (c, x, scope_dict)
                        del scope_dict [c.attrib ["var"]]
            elif "seq-eval" in c.attrib :
                try :
                    objs = eval \
                        ("[(%s) for %s in (%s)]" % 
                            ( c.attrib["var"]
                            , c.attrib["var"]
                            , c.attrib["seq-eval"]
                            )
                        , scope_dict 
                        )
                except :
                    self._logger.error('ERROR in seq-eval for `%s` `%s`', c.tag, c.attrib["seq-eval"])
                    raise 
                for o in objs :
                    scope_dict [c.attrib["var"]] = o
                    x = etree.SubElement (out, c.tag)
                    self._iterate (c, x, scope_dict)
                    del scope_dict [c.attrib ["var"]]
            else :
                x = etree.SubElement (out, c.tag)
                for name, value in c.items () :
                    if name == "loop-eval" : pass
                    elif name == "seq-eval": pass
                    elif name == "var" : pass
                    elif name [0:9] == "attr-eval" : pass
                    elif name == "text-eval":
                        try :
                            x.text = unicode (eval (value, scope_dict))
                        except : 
                            self._logger.error('ERROR in text-eval for `%s` `%s` `%s`', c.tag, name, value)
                            raise
                    elif name [0:9] == "attr-name" :
                        nr = name [9:]
                        try :
                            val = eval (c.attrib ["attr-eval" + nr], scope_dict)
                            x.set (c.attrib [name], unicode (val))
                        except :
                            self._logger.error('ERROR in attr-eval for `%s` `%s` `%s`', c.tag, name, c.attrib["attr-eval" + nr])
                            raise
                    else :
                        x.set (name, value)
                self._iterate (c, x, scope_dict)
    # end def _iterate
# end class XML_Generator
