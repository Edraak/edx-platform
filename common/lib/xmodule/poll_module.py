"""
Poll module is ungraded xmodule used by students to
to do set of polls.

Poll module contains a nummber of 2 - steps basic sequences. Every sequence
has data from all previous sequences. Selection of sequences can be in 
control block.

Basic sequence:

0. Control block
    a) get data from any previous sequence
    b) if block
    c) link to sequence


1. First. - must be, always visible
If student does not yet anwered - Question
If stundent have not answered - Question with statistics (yes/no)

2. Second - optional, if student does not yet answered on 1st - hidden
If student answers first time - show plot with statistics from
answer from other users.

"""

import json
import logging
from lxml import etree
import xmltodict

from xmodule.mako_module import MakoModuleDescriptor
from xmodule.xml_module import XmlDescriptor
from xmodule.x_module import XModule
from xmodule.stringify import stringify_children
from pkg_resources import resource_string


log = logging.getLogger(__name__)


class PollModule(XModule):
    ''' Poll Module
    '''

    js = {
      'js': [
        # 3rd party libraries used by graphic slider tool.
        # TODO - where to store them - outside xmodule?
        resource_string(__name__, 'js/src/graphical_slider_tool/jstat-1.0.0.min.js'),

        resource_string(__name__, 'js/src/graphical_slider_tool/gst_main.js'),
        resource_string(__name__, 'js/src/graphical_slider_tool/gst.js')
      ]
    }
    js_module_name = "Poll"

    def __init__(self, system, location, definition, descriptor, instance_state=None,
                 shared_state=None, **kwargs):
        """
        For XML file format please look at documentation. TODO - receive
        information where to store XML documentation.
        """
        XModule.__init__(self, system, location, definition, descriptor,
                         instance_state, shared_state, **kwargs)

    def get_html(self):
        """ Renders parameters to template. """

        # these 3 will be used in class methods
        self.html_id = self.location.html_id()
        self.html_class = self.location.category
        self.configuration_json = self.build_configuration_json()
        params = {
                  'element_html': self.definition['render'],
                  'element_id': self.html_id,
                  'element_class': self.html_class,
                  'configuration_json': self.configuration_json
                  }
        self.content = self.system.render_template(
                        'poll.html', params)
        return self.content

    def build_configuration_json(self):
        """Creates json element from xml element (with aim to transfer later
         directly to javascript via hidden field in template). Steps:

            1. Convert xml tree to python dict.

            2. Dump dict to json.

        """
        # <root> added for interface compatibility with xmltodict.parse
        # class added for javascript's part purposes
        return json.dumps(xmltodict.parse('<root class="' + self.html_class +
                '">' + self.definition['configuration'] + '</root>'))


class GraphicalSliderToolDescriptor(MakoModuleDescriptor, XmlDescriptor):
    module_class = PollModule
    template_dir_name = 'poll'

    @classmethod
    def definition_from_xml(cls, xml_object, system):
        """
        Pull out the data into dictionary.

        Args:
            xml_object: xml from file.

        Returns:
            dict
        """
        # check for presense of required tags in xml
        expected_children_level_0 = ['render', 'configuration']
        for child in expected_children_level_0:
            if len(xml_object.xpath(child)) != 1:
                raise ValueError("Graphical Slider Tool definition must include \
                    exactly one '{0}' tag".format(child))

        def parse(k):
            """Assumes that xml_object has child k"""
            return stringify_children(xml_object.xpath(k)[0])
        return {
                    'render': parse('render'),
                    'configuration': parse('configuration')
                }

    def definition_to_xml(self, resource_fs):
        '''Return an xml element representing this definition.'''
        xml_object = etree.Element('graphical_slider_tool')

        def add_child(k):
            child_str = '<{tag}>{body}</{tag}>'.format(tag=k, body=self.definition[k])
            child_node = etree.fromstring(child_str)
            xml_object.append(child_node)

        for child in ['render', 'configuration']:
            add_child(child)

        return xml_object
