"""
Table for storing information about installed xblocks
"""
from django.db import models
from django.utils.translation import ugettext as _
import pip
import pkg_resources
from xblock.core import XBlock


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

    name = models.CharField(max_length=128, blank=False, primary_key=True, help_text=_("Name of the xblock"))
    display_name = models.CharField(max_length=128, blank=True, help_text=_("Display name of the xblock"))
    repo = models.URLField(
        max_length=512, blank=True,
        help_text=_("GitHub repository for obtaining the xblock"))
    commit = models.CharField(max_length=256, blank=True, help_text=_("Commit ID for a specific version of the repository"))
    package_name = models.CharField(max_length=128, blank=True, help_text=_("Package name of xblock to install"))
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

    def clean(self):
        #Could throw Validation error
        newly_created = len(XBlockInfo.objects.all().filter(name=self.name)) == 0
        if newly_created:
            #"git+https://github.com/edx/acid-block.git@bf61f0fcd5916a9236bb5681c98374a48a13a74c#egg=acid-xblock"
            if self.commit:
                pip.main(["install", "git+{repo}@{commit}#egg={name}".format(repo=self.repo, commit=self.commit, name = self.package_name)])
            else:
                pip.main(["install", "git+{repo}#egg={name}".format(repo=self.repo, name = self.package_name)])
            dist = pkg_resources.get_distribution(self.package_name)
            XBlock.extra_entry_points.append((self.name, dist.get_entry_info(XBlock.entry_point, self.name)))
        return super(XBlockInfo, self).clean()


    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u"{0} | {1}".format(self.name, self.state)