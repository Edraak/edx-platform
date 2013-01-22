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
from progress import Progress


log = logging.getLogger(__name__)


class PollModule(XModule):
    ''' Poll Module
    '''

    js = {
       'coffee': [resource_string(__name__, 'js/src/javascript_loader.coffee'),
                  resource_string(__name__, 'js/src/poll/poll_main.coffee')],
      'js': [resource_string(__name__, 'js/src/poll/poll.js')]
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
        self.system = system
        if instance_state is not None:
            # state = json.loads(instance_state)
            pass

    def get_instance_state(self):
        """Dumps all user answers"""
        return json.dumps({'answered': True})

    def handle_ajax(self, dispatch, get):       # TODO: bounds checking
        ''' get = request.POST instance '''
        import ipdb; ipdb.set_trace()
        pass
        # if dispatch == 'goto_position':
            # self.position = int(get['position'])
            # return json.dumps({'success': True})
        # raise NotFoundError('Unexpected dispatch type')

    # def handle_ajax(self, dispatch, get, system):
    #     """
    #     This is called by courseware.module_render, to handle an AJAX call.
    #     "get" is request.POST.

    #     Returns a json dictionary:
    #     { 'progress_changed' : True/False,
    #     'progress': 'none'/'in_progress'/'done',
    #     <other request-specific values here > }
    #     """

    #     handlers = {
    #         'save_answer': self.save_answer,
    #         'save_assessment': self.save_assessment,
    #         'save_post_assessment': self.save_hint,
    #     }

    #     if dispatch not in handlers:
    #         return 'Error'

    #     before = self.get_progress()
    #     d = handlers[dispatch](get, system)
    #     after = self.get_progress()
    #     d.update({
    #         'progress_changed': after != before,
    #         'progress_status': Progress.to_js_status_str(after),
    #     })
    #     return json.dumps(d, cls=ComplexEncoder)


    # def answer_first_question(self, get, system):
    #     """
    #     After the answer is submitted, show the plot.

    #     Args:
    #         get: the GET dictionary passed to the ajax request.  Should contain
    #             a key 'student_answer'

    #     Returns:
    #         Dictionary with keys 'success' and either 'error' (if not success),
    #         or 'rubric_html' (if success).
    #     """
    #     # Check to see if attempts are less than max
    #     if self.attempts > self.max_attempts:
    #         # If too many attempts, prevent student from saving answer and
    #         # seeing rubric.  In normal use, students shouldn't see this because
    #         # they won't see the reset button once they're out of attempts.
    #         return {
    #             'success': False,
    #             'error': 'Too many attempts.'
    #         }

    #     if self.state != self.INITIAL:
    #         return self.out_of_sync_error(get)

    #     # add new history element with answer and empty score and hint.
    #     self.new_history_entry(get['student_answer'])
    #     self.change_state(self.ASSESSING)

    #     return {
    #         'success': True,
    #         'plot_html': self.get_plot_and_second_answer(system)
    #     }

    # def get_plot_and_second_answer(self, system):
    #     """
    #     Return the appropriate version of the rubric, based on the state.
    #     """
    #     if self.state == self.INITIAL:
    #         return ''

    #     rubric_html  = CombinedOpenEndedRubric.render_rubric(self.rubric)

    #     # we'll render it
    #     context = {'rubric': rubric_html,
    #                'max_score': self._max_score,
    #     }

    #     if self.state == self.ASSESSING:
    #         context['read_only'] = False
    #     elif self.state in (self.POST_ASSESSMENT, self.DONE):
    #         context['read_only'] = True
    #     else:
    #         raise ValueError("Illegal state '%r'" % self.state)

    #     return system.render_template('self_assessment_rubric.html', context)

    def get_html(self):
        """ Renders parameters to template. """
        #set context variables and render template
        # if self.state != self.INITIAL:
        #     latest = self.latest_answer()
        #     previous_answer = latest if latest is not None else ''
        # else:
        #     previous_answer = ''

        # these 3 will be used in class methods
        self.html_id = self.location.html_id()
        self.html_class = self.location.category
        self.configuration_json = self.build_configuration_json()
        params = {
                  'element_html': self.definition['render'],
                  'element_id': self.html_id,
                  'element_class': self.html_class,
                  'configuration_json': self.configuration_json,
                 'ajax_url': self.system.ajax_url,
            'state': 1,
            'allow_reset': True,
            'child_type': 'poll'
                  }
        # import ipdb; ipdb.set_trace()
        self.content = self.system.render_template(
                        'poll.html', params)
        # import ipdb; ipdb.set_trace()
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


class PollDescriptor(MakoModuleDescriptor, XmlDescriptor):
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
