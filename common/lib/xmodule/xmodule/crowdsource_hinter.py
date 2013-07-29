"""
Adds crowdsourced hinting functionality to lon-capa numerical response problems.

Currently experimental - not for instructor use, yet.
"""

import logging
import json
import random
import requests

from pkg_resources import resource_string

from lxml import etree

from xmodule.x_module import XModule
from xmodule.raw_module import RawDescriptor
from xblock.core import Scope, String, Integer, Boolean, Dict, List

from capa.responsetypes import FormulaResponse, StudentInputError

from calc import evaluator, UndefinedVariable
from pyparsing import ParseException

from django.utils.html import escape
from django.conf import settings

log = logging.getLogger(__name__)


class CrowdsourceHinterFields(object):
    """Defines fields for the crowdsource hinter module."""
    has_children = True

    moderate = String(help='String "True"/"False" - activates moderation', scope=Scope.content,
                      default='False')
    debug = String(help='String "True"/"False" - allows multiple voting', scope=Scope.content,
                   default='False')
    display_only = String(help='If True, then students will not be asked to submit hints',
                          scope=Scope.content, default='False')


class CrowdsourceHinterModule(CrowdsourceHinterFields, XModule):
    """
    An Xmodule that makes crowdsourced hints.
    Currently, only works on capa problems with exactly one numerical response,
    and no other parts.

    Example usage:
    <crowdsource_hinter>
        <problem blah blah />
    </crowdsource_hinter>

    XML attributes:
    -moderate="True" will not display hints until staff approve them in the hint manager.
    -debug="True" will let users vote as often as they want.
    """
    icon_class = 'crowdsource_hinter'
    css = {'scss': [resource_string(__name__, 'css/crowdsource_hinter/display.scss')]}
    js = {'coffee': [resource_string(__name__, 'js/src/crowdsource_hinter/display.coffee')],
          'js': []}
    js_module_name = "Hinter"

    def __init__(self, *args, **kwargs):
        XModule.__init__(self, *args, **kwargs)
        # We need to know whether we are working with a FormulaResponse problem.
        self.problem = self.get_display_items()[0]
        responder = self.problem.lcp.responders.values()[0]
        self.is_formula = (type(responder) == FormulaResponse)
        if self.is_formula:
            self.answer_to_str = self.formula_answer_to_str
        else:
            self.answer_to_str = self.numerical_answer_to_str

        # Transmit info to edInsights.
        data = {
            'location': self.problem.location,
            'user': self.system.anonymous_student_id,
            'moderate': self.moderate == 'True',
            'display_only': self.display_only == 'True',
            'debug': self.debug == 'True',
        }
        self.make_edInsights_query('hinting_setup', data)

    def get_html(self):
        """
        Puts a wrapper around the problem html.  This wrapper includes ajax urls of the
        hinter and of the problem.
        - Dependent on lon-capa problem.
        """
        try:
            child = self.get_display_items()[0]
            out = child.get_html()
            # The event listener uses the ajax url to find the child.
            child_url = child.system.ajax_url
        except IndexError:
            out = 'Error in loading crowdsourced hinter - can\'t find child problem.'
            child_url = ''

        # Wrap the module in a <section>.  This lets us pass data attributes to the javascript.
        out += '<section class="crowdsource-wrapper" data-url="' + self.system.ajax_url +\
            '" data-child-url = "' + child_url + '"> </section>'

        return out

    def numerical_answer_to_str(self, answer):
        """
        Converts capa numerical answer format to a string representation
        of the answer.
        -Lon-capa dependent.
        -Assumes that the problem only has one part.
        """
        return str(answer.values()[0])

    def formula_answer_to_str(self, answer):
        """
        Converts capa formula answer into a string.
        -Lon-capa dependent.
        -Assumes that the problem only has one part.
        """
        return str(answer.values()[0])

    def make_edInsights_query(self, query_name, data):
        """
        Makes a request to edInsights, and returns the response as a
        dictionary.
        """
        payload = {'in_dict_json': json.dumps(data)}
        r = requests.get(
            settings.EDINSIGHTS_SERVER_URL + 'query/' + query_name, 
            params=payload,
            headers={'AUTHORIZATION': settings.EDINSIGHTS_PASSWORD}
        )
        return json.loads(r.text)

    def handle_ajax(self, dispatch, data):
        """
        This is the landing method for AJAX calls.
        """
        if dispatch == 'get_hint':
            out = self.get_hint(data)
        elif dispatch == 'get_feedback':
            out = self.get_feedback(data)
        elif dispatch == 'vote':
            out = self.tally_vote(data)
        elif dispatch == 'submit_hint':
            out = self.submit_hint(data)
        else:
            return json.dumps({'contents': 'Error - invalid operation.'})

        if out is None:
            out = {'op': 'empty'}
        elif 'error' in out:
            # Error in processing.
            out.update({'op': 'error'})
        else:
            out.update({'op': dispatch})
        return json.dumps({'contents': self.system.render_template('hinter_display.html', out)})

    def get_hint(self, data):
        """
        The student got the incorrect answer found in data.  Give him a hint.

        Called by hinter javascript after a problem is graded as incorrect.
        Args:
        `data` -- must be interpretable by answer_to_str.
        Output keys:
            - 'best_hint' is the hint text with the most votes.
            - 'rand_hint_1' and 'rand_hint_2' are two random hints to the answer in `data`.
            - 'answer' is the parsed answer that was submitted.
        """
        try:
            answer = self.answer_to_str(data)
        except (ValueError, AttributeError):
            # Sometimes, we get an answer that's just not parsable.  Do nothing.
            log.exception('Answer not parsable: ' + str(data))
            return
        # Transmit info to edInsights.
        data = {
            'location': self.problem.location,
            'answer': answer,
            'user': self.system.anonymous_student_id,
            'number_best': 1,
            'number_random': 2,
        }
        response_dict = self.make_edInsights_query('get_hint', data)
        if not response_dict['success']:
            return response_dict
        return {
            'hints': response_dict['hints'],
            'answer': answer,
        }

    def get_feedback(self, data):
        """
        The student got it correct.  Ask him to vote on hints, or submit a hint.

        Args:
        `data` -- not actually used.  (It is assumed that the answer is correct.)
        Output keys:
            - 'answer_to_hints': a nested dictionary.
              answer_to_hints[answer][hint_pk] returns the text of the hint.
        """
        if self.display_only == 'True':
            # display_only means that we don't collect hints.
            return
        # Talk to edInsights.
        data = {
            'location': self.problem.location,
            'user': self.system.anonymous_student_id,
        }
        response_dict = self.make_edInsights_query('hint_history', data)
        if not response_dict['success']:
            return response_dict

        # Process the response.
        if len(response_dict['previous_answers']) == 0:
            # No wrong answers = nothing for user to submit here.
            return
        answer_to_hints = {}
        for hint_id, answer, text in response_dict['hints_shown']:
            if answer not in answer_to_hints:
                answer_to_hints[answer] = {}
            answer_to_hints[answer][hint_id] = text
        return {'answer_to_hints': answer_to_hints,
                'user_submissions': response_dict['previous_answers']}

    def tally_vote(self, data):
        """
        Tally a user's vote on his favorite hint.

        Args:
        `data` -- expected to have the following keys:
            'answer': text of answer we're voting on
            'hint': hint_pk
            'pk_list': A list of [answer, pk] pairs, each of which representing a hint.
                       We will return a list of how many votes each hint in the list has so far.
                       It's up to the browser to specify which hints to return vote counts for.
                       
        Returns key 'hint_and_votes', a list of (hint_text, #votes) pairs.
        """
        # Talk to edInsights.
        data = {
            'location': self.problem.location,
            'user': self.system.anonymous_student_id,
            'id': str(data['hint']),
        }
        response_dict = self.make_edInsights_query('vote', data)
        if not response_dict['success']:
            return response_dict

        hint_and_votes = [[hint, votes] for hint, hint_id, votes in response_dict['vote_counts']]
        return {'hint_and_votes': hint_and_votes}

    def submit_hint(self, data):
        """
        Take a hint submission and add it to the database.

        Args:
        `data` -- expected to have the following keys:
            'answer': text of answer
            'hint': text of the new hint that the user is adding
        Returns a thank-you message.
        """
        # Do html escaping.  Perhaps in the future do profanity filtering, etc. as well.
        hint = escape(data['hint'])
        answer = data['answer']
        data = {
            'answer': answer,
            'hint': hint,
            'user': self.system.anonymous_student_id,
            'location': self.problem.location,
        }
        response_dict = self.make_edInsights_query('submit_hint', data)
        if not response_dict['success']:
            return response_dict
        return {'message': 'Thank you for your hint!'}


class CrowdsourceHinterDescriptor(CrowdsourceHinterFields, RawDescriptor):
    module_class = CrowdsourceHinterModule
    stores_state = True

    @classmethod
    def definition_from_xml(cls, xml_object, system):
        children = []
        for child in xml_object:
            try:
                children.append(system.process_xml(etree.tostring(child, encoding='unicode')).location.url())
            except Exception as e:
                log.exception("Unable to load child when parsing CrowdsourceHinter. Continuing...")
                if system.error_tracker is not None:
                    system.error_tracker("ERROR: " + str(e))
                continue
        return {}, children

    def definition_to_xml(self, resource_fs):
        xml_object = etree.Element('crowdsource_hinter')
        for child in self.get_children():
            xml_object.append(
                etree.fromstring(child.export_to_xml(resource_fs)))
        return xml_object
