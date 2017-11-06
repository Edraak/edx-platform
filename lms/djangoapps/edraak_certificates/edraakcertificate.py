# -*- coding: utf-8 -*-
import re
from os import path

from django.core.files.temp import NamedTemporaryFile
from django.utils import translation

from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import utils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
import qrcode

from util import organizations_helpers as organization_api
import arabicreshaper

from certificates.models import GeneratedCertificate

from lms.djangoapps.certificates.api import get_certificate_url, \
    get_active_web_certificate

static_dir = path.join(path.dirname(__file__), 'assets')

fonts = {
    'sahlnaskh-regular.ttf': 'Sahl Naskh Regular',
    'sahlnaskh-bold.ttf': 'Sahl Naskh Bold',
}

for font_file, font_name in fonts.iteritems():
    font_path = path.join(static_dir, font_file)
    pdfmetrics.registerFont(TTFont(font_name, font_path, validate=True))


SIZE = landscape(A4)


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
    def __init__(self, course, user, course_desc, path_builder=None):
        self.path_builder = path_builder
        self.certificate_data = get_active_web_certificate(course)
        self.cert = GeneratedCertificate.certificate_for_student(
            user, course.id)

        self.user_profile_name = user.profile.name

        self.course_id = course.id
        self.course_name = self.certificate_data.get('course_title')
        self.course_desc = course_desc
        print self.certificate_data
        self.organizations = organization_api.get_course_organizations(
            course_id=course.id)
        self.sponsors = organization_api.get_course_sponsors(
            course_id=course.id)

        print self.cert

        self.colors = {
            'base': (225 / 255.0, 0 / 255.0, 67 / 255.0),
            'grey-dark': (66 / 255.0, 74 / 255.0, 82 / 255.0),
            'grey-light': (113 / 255.0, 113 / 255.0, 113 / 255.0),
        }

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
        # TODO: Look into this
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

        background_filename = 'certificate_layout.png'
        background_path = path.join(static_dir, background_filename)

        self.ctx.drawImage(background_path, 0, 0, width, height)

    def _set_font(self, size, is_bold, color='grey-dark'):
        if is_bold:
            font = 'Sahl Naskh Bold'
        else:
            font = 'Sahl Naskh Regular'

        self.ctx.setFont(font, size)
        self.ctx.setFillColorRGB(*self.colors[color])

    def draw_single_line_bidi_text(self, text, x, y, size, bold=False, max_width=7.494, color='grey-dark'):
        x *= inch
        y *= inch
        size *= inch
        max_width *= inch

        text = text_to_bidi(text)

        while True:
            self._set_font(size, bold, color)
            lines = list(self._wrap_text(text, max_width))

            if len(lines) > 1:
                size *= 0.9  # reduce font size by 10%
            else:
                if not self.is_english_course():
                    self.ctx.drawRightString(self.bidi_x_axis(x), y, lines[0])
                else:
                    self.ctx.drawString(self.bidi_x_axis(x), y, lines[0])
                break

    def draw_bidi_center_text(self, text, x, y, size, bold=False, color='grey-dark'):
        x *= inch
        y *= inch
        size *= inch

        self._set_font(size, bold, color)

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

    def draw_bidi_text(self, text, x, y, size, bold=False,
                       max_width=7.494, lh_factor=1.3, color='grey-dark'):
        x *= inch
        y *= inch
        size *= inch
        max_width *= inch
        line_height = size * lh_factor

        self._set_font(size, bold, color=color)

        text = text_to_bidi(text)

        for line in self._wrap_text(text, max_width):
            if not self.is_english_course():
                self.ctx.drawRightString(self.bidi_x_axis(x), y, line)
                y -= line_height
            else:
                self.ctx.drawString(self.bidi_x_axis(x), y, line)
                y -= line_height

    def add_course_org_logo(self):
        center_x = 1.6
        y = 5.6

        self.draw_bidi_center_text(
            self._("Brought to you by"), center_x, y, 0.175,
            color='grey-light')

        if self.organizations:
            organization = self.organizations[0]
            logo = organization.get('logo', None)
            image = utils.ImageReader(self.path_builder(logo.url))

            iw, ih = image.getSize()
            aspect = iw / float(ih)
            height = inch / 1.55
            width = height * aspect

            org_center_x = (center_x*inch) + (width/2)
            x = self.bidi_x_axis(org_center_x)
            y -= 0.75

            self.ctx.drawImage(image, x, y*inch,
                width, height,
                mask='auto')

    def add_course_sponsor_logo(self):
        if not self.sponsors:
            return

        center_x = 1.6
        y = 4.3

        self.draw_bidi_center_text(
            self._("In sponsorship with"), center_x, y, 0.125,
            color='grey-light')

        organization = self.sponsors[0]
        logo = organization.get('logo', None)
        image = utils.ImageReader(self.path_builder(logo.url))

        iw, ih = image.getSize()
        aspect = iw / float(ih)
        height = inch / 2.1
        width = height * aspect

        org_center_x = (center_x*inch) + (width/2)
        x = self.bidi_x_axis(org_center_x)
        y -= 0.55

        self.ctx.drawImage(image, x, y*inch,
            width, height,
            mask='auto')

    def add_signatories(self):
        center_x = 1.6
        signature_space = 1.5
        space = 5

        if self.sponsors:
            space -= 1.13

        # Logo dimensions
        iw, ih = 180, 76
        aspect = iw / float(ih)
        height = inch / 1.9
        width = height * aspect

        signature_center_x = (center_x * inch) + (width / 2)
        signature_x = self.bidi_x_axis(signature_center_x)

        signatories = self.certificate_data.get('signatories', [])
        for signatory in signatories:
            signature = signatory['signature_image_path']
            signature_url = self.path_builder(signature)
            signature = ImageReader(signature_url)

            space -= signature_space
            self.ctx.drawImage(
                signature, signature_x, (space+0.25)*inch,
                width, height, mask='auto')

            self.draw_bidi_center_text(
                signatory['name'], center_x, space, 0.15)
            self.draw_bidi_center_text(
                signatory['title'], center_x, space-0.15, 0.1,
                color='grey-light')
            self.draw_bidi_center_text(
                signatory['organization'], center_x, space-0.3, 0.1,
                color='grey-light')

    def add_edraak_logo(self):
        x, y = (9.1*inch)-1, 6.5*inch
        logo = path.join(static_dir, 'edraak_logo.png')
        iw, ih = 471, 198
        aspect = iw / float(ih)

        height = inch - 10
        width = height * aspect
        self.ctx.drawImage(logo, x, y, width, height, mask='auto')

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

    def draw_debugging_grid(self):
        # TODO: remove this
        from reportlab.lib.colors import cyan
        self.ctx.setStrokeColor(cyan) # put in a frame of reference

        xs = [x*inch for x in range(13)]
        ys = [y*inch for y in range(10)]

        self.ctx.grid(xs, ys)

    def add_certificate_footer(self):
        x, y = 11,  0.9
        sub_y = y - 0.25
        font_size = 0.15
        font_sub_size = 0.12

        self.draw_english_text(
            self._('COURSE CERTIFICATE'), x, y, size=font_size)

        self.draw_english_text(
            self._('Issued'), x, sub_y, bold=True, size=font_sub_size)

        date = self._(
            '{month} {day}, {year}').format(
            month=self.cert.modified_date.strftime("%B"),
            day=self.cert.modified_date.day,
            year=self.cert.modified_date.year)

        self.draw_bidi_text(
            date, x-0.45, sub_y,
            bold=True, size=font_sub_size)

        # Verification
        # TODO: Add the QR Code here
        # NOTE: I added some space to the QR on the left
        x = x - 3.3
        self.draw_english_text(
            self._('Verify the authenticity of this certificate '
                   'at'), x, y, size=font_size)

        cert_url = get_certificate_url(
            course_id=self.course_id, uuid=self.cert.verify_uuid)
        url = self.path_builder(cert_url)

        self.add_qr_code(url)
        self.draw_english_text(url, x, sub_y, size=font_sub_size)

    def add_qr_code(self, vertification_url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(vertification_url)
        qr.make(fit=True)
        qr_image = qr.make_image()
        image = utils.ImageReader(qr_image._img)

        iw, ih = image.getSize()
        aspect = iw / float(ih)
        height = inch / 1.2
        width = height * aspect

        x = (4*inch) - (1.1*width)
        y = inch - (height/1.4)

        self.ctx.drawImage(
            image, x, y, width, height, mask='auto')

    def generate_and_save(self):
        self.init_context()

        x = 11
        y = 7
        self.add_certificate_bg()

        # TODO: remove this
        # self.draw_debugging_grid()

        self.add_edraak_logo()
        self.add_course_org_logo()
        self.add_course_sponsor_logo()
        self.add_signatories()

        self.draw_bidi_text(
            self._("CERTIFICATE OF COMPLETION"), x, y,
            size=0.30, color='base')

        y -= 0.5
        self.draw_bidi_text(
            self._("This is to certify that"), x, y,
            size=0.2, color='base')

        # User profile name
        name = self.user_profile_name
        user_profile_size = 0.42 if contains_rtl_text(name) else 0.55
        y -= 1.5

        self.draw_single_line_bidi_text(
            name, x, y,
            size=user_profile_size, bold=True)

        y -= 1
        self.draw_bidi_text(
            self._("Successfully completed"), x, y,
            size=0.2, color='grey-light')

        # Course Name
        name = self.course_name
        name_size = 0.31 if contains_rtl_text(name) else 0.3
        y -= 0.5
        self.draw_bidi_text(
            name, x, y, size=name_size, bold=True)

        y -= 0.5
        self.draw_bidi_text(
            self.course_desc, x, y, max_width=5.5, size=0.16)

        # Below goes the footer logic
        self.add_certificate_footer()
        self.save()
