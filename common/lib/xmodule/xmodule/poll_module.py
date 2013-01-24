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
from lxml import html

from xmodule.mako_module import MakoModuleDescriptor
from xmodule.xml_module import XmlDescriptor
from xmodule.x_module import XModule
from xmodule.stringify import stringify_children
from pkg_resources import resource_string
from progress import Progress


log = logging.getLogger(__name__)


class PollModule(XModule):
    ''' Poll Module
    '''
    js = {
      'coffee': [resource_string(__name__, 'js/src/javascript_loader.coffee')],
      'js': [resource_string(__name__, 'js/src/poll/poll.js'),
             resource_string(__name__, 'js/src/poll/poll_main.js')]
         }
    css = {'scss': [resource_string(__name__, 'css/poll/display.scss')]}
    js_module_name = "Poll"

    def __init__(self, system, location, definition, descriptor, instance_state=None,
                 shared_state=None, **kwargs):
        """
        For XML file format please look at documentation. TODO - receive
        information where to store XML documentation.
        """
        XModule.__init__(self, system, location, definition, descriptor,
                         instance_state, shared_state, **kwargs)
        self.system = system
        self.html_id = self.location.html_id()
        self.html_class = self.location.category
        self.poll_units_list = []

        if instance_state is not None:
            self.state = json.loads(instance_state)
            self.variant = self.state.get('answer', 0)
        else:
            self.variant = 0

    def get_instance_state(self):
        """Dumps all user answers"""
        # import ipdb; ipdb.set_trace()
        return json.dumps({'answered': True,
                          'answer': self.variant})

    def handle_ajax(self, dispatch, get):
        ''' get = request.POST instance '''
        # import ipdb; ipdb.set_trace()
        if dispatch == 'submit_answer':
            if int(get['answer']) == 1:
                self.variant += 10
                return json.dumps({'success': True})
            else:
                self.varuant -= 10
                return json.dumps({'success': False})
        # raise NotFoundError('Unexpected dispatch type')

    def get_html(self):
        """ Renders parameters to template. """

        params = {
                  'element_html': self.definition['render'],
                  'element_id': self.html_id,
                  'element_class': self.html_class,
                  'ajax_url': self.system.ajax_url,
                  'poll_units': self.parse_sequence(self.definition['sequence']),
                  }
        self.content = self.system.render_template(
                        'poll.html', params)
        return self.content

    def get_poll_unit_html(self, i, question):
        """ """
        return """
<div id="poll_unit_{poll_number}" class="polls"> {question}
  <div class="vote_and_submit">
    <div id="vote_block-1" class="vote">
      <ul>
        <li>
          <input type="radio" id="vote_{poll_number}" name="vote_{poll_number}" value="Yes" />
            <label for="vote_{poll_number}">Yes</label>
          </li>
          <li>
            <input type="radio" id="vote_{poll_number}" name="vote_{poll_number}" value="No" />
            <label for="vote_{poll_number}">No</label>
          </li>
        </ul>
      </div>

    <div class="vote_submit_button">
        <input type="button" value="Cast Your vote" class=".submit-button"/>
    </div>
  </div>

  <div class="graph_answer"></div>
</div>""".format(poll_number=i, question=question)

    def parse_sequence(self, html_string):
        """    substitute sequence     """
        xml = html.fromstring(html_string)
        poll_units = xml.xpath('//unit')
        for i, poll_unit in enumerate(poll_units):
            # import ipdb; ipdb.set_trace()
            poll_unit_question = stringify_children(poll_unit.xpath('//question')[0])
            poll_unit_html = html.fromstring(self.get_poll_unit_html(i,
                                             poll_unit_question))

            poll_unit_controls = (poll_unit.get('plot', "no"),
                             poll_unit.get('next_yes', "end"),
                             poll_unit.get('next_no', "end"))
            self.poll_units_list.append((poll_unit_html,
                                   poll_unit_controls))
        import ipdb; ipdb.set_trace()


class PollDescriptor(MakoModuleDescriptor, XmlDescriptor):
    module_class = PollModule
    template_dir_name = 'poll'
    stores_state = True

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
        expected_children_level_0 = ['render', 'sequence']
        for child in expected_children_level_0:
            if len(xml_object.xpath(child)) != 1:
                raise ValueError("Poll definition must include \
                    exactly one '{0}' tag".format(child))

        def parse(k):
            """Assumes that xml_object has child k"""
            return stringify_children(xml_object.xpath(k)[0])
        return {
                    'render': parse('render'),
                    'sequence': parse('sequence')
                }

    def definition_to_xml(self, resource_fs):
        '''Return an xml element representing this definition.'''
        xml_object = etree.Element('graphical_slider_tool')

        def add_child(k):
            child_str = '<{tag}>{body}</{tag}>'.format(tag=k, body=self.definition[k])
            child_node = etree.fromstring(child_str)
            xml_object.append(child_node)

        for child in ['render', 'sequence']:
            add_child(child)

        return xml_object
