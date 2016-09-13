# -*- coding: utf-8 -*-

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import utils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import landscape, A4
import arabicreshaper
from bidi.algorithm import get_display
import re
from os import path
from django.core.files.temp import NamedTemporaryFile
from django.utils import translation

static_dir = path.join(path.dirname(__file__), 'assets')

fonts = {
    'sahlnaskh-regular.ttf': 'Sahl Naskh Regular',
    'sahlnaskh-bold.ttf': 'Sahl Naskh Bold',
}

for font_file, font_name in fonts.iteritems():
    font_path = path.join(static_dir, font_file)
    pdfmetrics.registerFont(TTFont(font_name, font_path, validate=True))


SIZE = landscape(A4)


def get_organization_logo(organization):
    organization = organization.lower()
    if organization == 'mitx' or organization == 'harvardx' or organization == 'qrf':
        return 'edx.png'
    elif organization == u'bayt.com':
        return 'bayt-logo2-en.png'
    elif organization == u'qrta':
        return 'qrta_logo.jpg'
    elif organization == 'aub':
        return 'Full-AUB-Seal.jpg'
    elif organization == "csbe":
        return 'csbe.png'
    elif organization == "hcac":
        return 'HCAC_Logo.png'
    elif organization == "delftx":
        return 'delftx.jpg'
    elif organization == "britishcouncil":
        return 'british-council.jpg'
    elif organization == "crescent_petroleum":
        return 'crescent-petroleum.jpg'
    elif organization == 'auc':
        return 'auc.jpg'
    elif organization == 'pmijo':
        return 'pmijo.jpg'
    elif organization == 'qou':
        return 'qou.png'
    elif organization == 'mbrcgi':
        return 'mbrcgi.png'
    else:
        return None


def get_course_sponsor(course_id):
    if course_id in (
            "BritishCouncil/Eng100/T4_2015",
            "course-v1:BritishCouncil+Eng100+T4_2015",
            "course-v1:BritishCouncil+Eng2+2016Q3",
            "course-v1:BritishCouncil+Eng3+Q4-2016"
    ):
        return "crescent_petroleum"
    else:
        return None


def text_to_bidi(text):
    text = normalize_spaces(text)

    reshaped_text = arabicreshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def normalize_spaces(text):
    return re.sub(' +', ' ', text)


def contains_rtl_text(string):
        try:
            string.decode('ascii')
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            return True
        else:
            return False


class EdraakCertificate(object):
    def __init__(self, user_profile_name, course_id, course_name, course_desc, instructor, course_end_date, course_org=None):
        self.user_profile_name = user_profile_name
        self.course_id = course_id
        self.course_name = course_name
        self.course_desc = course_desc
        self.instructor = instructor
        self.course_end_date = course_end_date
        self.course_org = course_org

        self.temp_file = NamedTemporaryFile(suffix='-cert.pdf')

        self.ctx = None

    def is_english_course(self):
        return not contains_rtl_text(self.course_name)

    def _(self, text):
        """
        Force the translation language to match the course language instead of the platform language.
        """
        previous_locale = translation.get_language()
        forced_language = 'en' if self.is_english_course() else 'ar'

        with translation.override(forced_language):
            return translation.ugettext(text)

    def init_context(self):
        ctx = canvas.Canvas(self.temp_file.name)
        ctx.setPageSize(SIZE)
        self.ctx = ctx

    def bidi_x_axis(self, x):
        """
        Normalize the X-axis and provide the correct RTL/LTR value.

        This helps avoiding hard-coded values for both directions.
        """

        if not self.is_english_course():
            return x
        else:
            return SIZE[0] - x

    def add_certificate_bg(self):
        width, height = SIZE

        direction = 'ltr' if self.is_english_course() else 'rtl'
        background_filename = 'certificate_layout_{}.jpg'.format(direction)
        background_path = path.join(static_dir, background_filename)

        self.ctx.drawImage(background_path, 0, 0, width, height)

    def _set_font(self, size, is_bold):
        if is_bold:
            font = 'Sahl Naskh Bold'
        else:
            font = 'Sahl Naskh Regular'

        self.ctx.setFont(font, size)
        self.ctx.setFillColorRGB(66 / 255.0, 74 / 255.0, 82 / 255.0)

    def draw_single_line_bidi_text(self, text, x, y, size, bold=False, max_width=7.494):
        x *= inch
        y *= inch
        size *= inch
        max_width *= inch

        text = text_to_bidi(text)

        while True:
            self._set_font(size, bold)
            lines = list(self._wrap_text(text, max_width))

            if len(lines) > 1:
                size *= 0.9  # reduce font size by 10%
            else:
                if not self.is_english_course():
                    self.ctx.drawRightString(self.bidi_x_axis(x), y, lines[0])
                else:
                    self.ctx.drawString(self.bidi_x_axis(x), y, lines[0])
                break

    def draw_bidi_center_text(self, text, x, y, size, bold=False):
        x *= inch
        y *= inch
        size *= inch

        self._set_font(size, bold)

        text = text_to_bidi(text)

        self.ctx.drawCentredString(self.bidi_x_axis(x), y, text)

    def draw_english_text(self, text, x, y, size, bold=False, max_width=7.494, lh_factor=1.3):
        x *= inch
        y *= inch
        size *= inch
        max_width *= inch
        line_height = size * lh_factor
        self._set_font(size, bold)
        text = text_to_bidi(text)
        for line in self._wrap_text(text, max_width):
            self.ctx.drawString(self.bidi_x_axis(x), y, line)
            y -= line_height

    def draw_bidi_text(self, text, x, y, size, bold=False, max_width=7.494, lh_factor=1.3):
        x *= inch
        y *= inch
        size *= inch
        max_width *= inch
        line_height = size * lh_factor

        self._set_font(size, bold)

        text = text_to_bidi(text)

        for line in self._wrap_text(text, max_width):
            if not self.is_english_course():
                self.ctx.drawRightString(self.bidi_x_axis(x), y, line)
                y -= line_height
            else:
                self.ctx.drawString(self.bidi_x_axis(x), y, line)
                y -= line_height

    def add_course_org_logo(self, course_org):
        if course_org:
            logo = get_organization_logo(course_org)
            if logo:
                image = utils.ImageReader(path.join(static_dir, logo))

                iw, ih = image.getSize()
                aspect = iw / float(ih)
                height = 1.378 * inch
                width = height * aspect

                rtl_x = 3.519 * inch

                if not self.is_english_course():
                    x = rtl_x
                else:
                    x = self.bidi_x_axis(rtl_x) - width

                y = 6.444 * inch

                self.ctx.drawImage(image, x, y, width, height)

    def add_course_sponsor_logo(self, sponsor):
        logo = get_organization_logo(sponsor)
        if logo:
            image = utils.ImageReader(path.join(static_dir, logo))

            iw, ih = image.getSize()
            aspect = iw / float(ih)
            height = 0.75 * inch
            width = height * aspect

            rtl_x = 9.25 * inch

            if not self.is_english_course():
                x = rtl_x
            else:
                x = self.bidi_x_axis(rtl_x) - width

            y = 2.45 * inch

            self.ctx.drawImage(image, x, y, width, height)

    def _wrap_text(self, text, max_width):
        same = lambda x: x
        _reversed = reversed if not self.is_english_course() else same

        words = _reversed(text.split(u' '))

        def de_reverse(text_to_reverse):
            if not self.is_english_course():
                return u' '.join(_reversed(text_to_reverse.split(u' ')))
            else:
                return text_to_reverse

        line = u''
        for next_word in words:
            next_width = self.ctx.stringWidth(line.strip() + u' ' + next_word.strip())

            if next_width >= max_width:
                yield de_reverse(line).strip()
                line = next_word
            else:
                line += u' ' + next_word.strip()

        if line:
            yield de_reverse(line).strip()

    def save(self):
        self.ctx.showPage()
        self.ctx.save()

    def course_org_disclaimer(self):
        if self.course_org == 'MITX':
            return self._("A course of study offered by Edraak with cooperation from MITx. "
                          "The learning experience has been supervised and managed by the course team.")
        else:
            return self._("A course of study offered by Edraak. The learning experience has been supervised and "
                          "managed by the course team.")

    def generate_and_save(self):
        self.init_context()

        x = 10.8
        self.add_certificate_bg()
        self.add_course_org_logo(self.course_org)

        self.draw_bidi_text(self._("This is to certify that:"), x, 5.8, size=0.25)

        user_profile_size = 0.42 if contains_rtl_text(self.user_profile_name) else 0.5
        self.draw_single_line_bidi_text(self.user_profile_name, x, 5.124, size=user_profile_size, bold=True)

        self.draw_bidi_text(self._("Successfully completed:"), x, 4.63, size=0.25)

        course_name_size = 0.31 if contains_rtl_text(self.course_name) else 0.33

        sponsor = get_course_sponsor(self.course_id)
        if sponsor:
            self.draw_single_line_bidi_text(self.course_name, x, 4.1, size=course_name_size, bold=True)
            self.draw_bidi_text(self._("This course is sponsored by:"), x, 3.5, size=0.25)
            self.add_course_sponsor_logo(sponsor)
        else:
            self.draw_bidi_text(self.course_name, x, 4.1, size=course_name_size, bold=True)
            if not self.is_english_course():
                self.draw_bidi_text(self.course_desc, x, 3.74, size=0.16)
            else:
                self.draw_english_text(self.course_desc, x, 3.74, size=0.16)

        date_x = 2.01

        words = self._("Course{new_line}Certificate{new_line}of Completion").split('{new_line}')

        for idx, word in enumerate(words):
            font_size = 0.27
            line_height = font_size * 1.3
            y = 6.1 - (idx * line_height)

            self.draw_bidi_center_text(word, date_x, y, size=font_size, bold=True)

        self.draw_single_line_bidi_text(self.instructor, x, 1.8, size=0.26, bold=True)

        if not self.is_english_course():
            self.draw_bidi_text(self.course_org_disclaimer(), x, 1.44, size=0.16)
        else:
            self.draw_english_text(self.course_org_disclaimer(), x, 1.44, size=0.16)

        self.draw_bidi_center_text(self.course_end_date, date_x, 4.82, size=0.27)

        self.save()
