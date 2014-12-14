# -*- coding: utf-8 -*-

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
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

light_font_url = path.join(static_dir, "DINNextLTArabic-Light.ttf")
pdfmetrics.registerFont(TTFont("DIN Next LT Arabic Light", light_font_url, validate=True))

bold_font_url = path.join(static_dir, "DinTextArabic-Bold.ttf")
pdfmetrics.registerFont(TTFont("DIN Next LT Arabic Bold", bold_font_url, validate=True))

SIZE = landscape(A4)


def course_org_to_logo(course_org):
    course_org = course_org.lower()
    if course_org == 'mitx' or course_org == 'harvardx' or course_org == 'qrf':
        return 'edx.png'
    elif course_org == u'bayt.com':
        return 'bayt-logo2-en.png'
    elif course_org == u'qrta':
        return 'qrta_logo.jpg'
    elif course_org == 'aub':
        return 'Full-AUB-Seal.jpg'
    elif course_org == "csbe":
        return 'csbe.png'
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
    def __init__(self, user_profile_name, course_name, course_desc, instructor, course_end_date, course_org=None):
        self.user_profile_name = user_profile_name
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

        translation.activate(forced_language)
        translated_text = translation.ugettext(text)
        translation.deactivate()
        translation.activate(previous_locale)

        return translated_text

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
            font = "DIN Next LT Arabic Bold"
        else:
            font = "DIN Next LT Arabic Light"

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
                y += line_height

    def add_course_org_logo(self, course_org):
        if course_org:
            logo = course_org_to_logo(course_org)
            if logo:
                image = path.join(static_dir, logo)

                width = 2.467 * inch
                height = 1.378 * inch

                rtl_x = 3.519 * inch

                if not self.is_english_course():
                    x = rtl_x
                else:
                    x = self.bidi_x_axis(rtl_x) - width

                y = 6.444 * inch

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
            # Translators: Edraak-specific
            return self._("A course of study offered by Edraak with cooperation from MITx. "
                          "The learning experience has been supervised and managed by the course team.")
        else:
            # Translators: Edraak-specific
            return self._("A course of study offered by Edraak. The learning experience has been supervised and "
                          "managed by the course team.")

    def generate_and_save(self):
        self.init_context()

        x = 10.8
        self.add_certificate_bg()
        self.add_course_org_logo(self.course_org)

        # Translators: Edraak-specific
        self.draw_bidi_text(self._("This is to certify that:"), x, 5.8, size=0.25)

        self.draw_single_line_bidi_text(self.user_profile_name, x, 5.124, size=0.5, bold=True)

        # Translators: Edraak-specific
        self.draw_bidi_text(self._("Successfully completed:"), x, 4.63, size=0.25)

        self.draw_bidi_text(self.course_name, x, 4.1, size=0.33, bold=True)

        if not self.is_english_course():
            self.draw_bidi_text(self.course_desc, x, 3.78, size=0.16)
        else:
            self.draw_english_text(self.course_desc, x, 3.78, size=0.16)

        date_x = 2.01

        # Translators: Keep newlines for formatting, Edraak-specific
        words = self._("Course{new_line}Certificate{new_line}of Completion").split('{new_line}')

        for idx, word in enumerate(words):
            font_size = 0.27
            line_height = font_size * 1.3
            y = 6.1 - (idx * line_height)

            self.draw_bidi_center_text(word, date_x, y, size=font_size, bold=True)

        self.draw_single_line_bidi_text(self.instructor, x, 1.8, size=0.26, bold=True)

        if not self.is_english_course():
            self.draw_bidi_text(self.course_org_disclaimer(), x, 1.48, size=0.16)
        else:
            self.draw_english_text(self.course_org_disclaimer(), x, 1.48, size=0.16)

        self.draw_bidi_center_text(self.course_end_date, date_x, 4.82, size=0.27)

        self.save()
