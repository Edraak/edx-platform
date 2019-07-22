from util.organizations_helpers import *
from xmodule.modulestore.django import modulestore


all_courses = modulestore().get_courses()
orgs = set(map(lambda x:x.org.lower(), all_courses))
for o in orgs:
    curr_org = get_organization_by_short_name(o)
    if not curr_org:
        data = {
            'name': o,
            'short_name': o,
            'description': 'Organization Description',
            'active': True,
            # 'logo': "organization_logos/{}.png".format(o)
        }
        print add_organization(data)
        curr_org = get_organization_by_short_name(o)
        print "org ", data, "added"
        # time.sleep(10)
    org_courses = filter(lambda x:x.org.lower() == o, all_courses)
    for c in org_courses:
        if not get_course_organizations(c.id):
            print "course ", curr_org,  "added to ", c.id
            add_organization_course(curr_org, c.id)

