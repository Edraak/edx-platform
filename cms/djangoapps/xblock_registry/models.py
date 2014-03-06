"""
Table for storing information about installed xblocks
"""
from django.db import models
from django.utils.translation import ugettext as _


class XBlockInfo(models.Model):
    """
    Creates the database table model.
    """
    APPROVED = 'approved'
    EXPERIMENTAL = 'experimental'
    DISABLED = 'disabled'

    # Second value is the "human-readable" version.
    STATES = (
        (APPROVED, _(u'approved')),
        (EXPERIMENTAL, _(u'experimental')),
        (DISABLED, _(u'disabled'))
        )

    name = models.CharField(max_length=24, blank=False, primary_key=True, help_text=_("Name of the xblock"))
    state = models.CharField(max_length=24, blank=False, choices=STATES, default=DISABLED,
                             help_text=_("State of the xblock in Studio"))
    screenshot = models.URLField(
        max_length=512, blank=True,
        default="http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png",
        help_text=_("Screenshot of the xblock")
    )
    summary = models.CharField(
        max_length=512, blank=True,
        default="A building problem that uses a simulation of lincoln logs",
        help_text=_("Short description of this xblock")
    )

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"{0} | {1}".format(self.name, self.state)