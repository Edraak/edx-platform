"""
Administrator Dashboard views and helper functions

Contains one HTML view and two data views which return json
to logged in staff users.  These two data views are loaded from
the HTML view (ajax).
"""

import json
import calendar
import time
from datetime import date, datetime, timedelta
from operator import itemgetter

from django.http import Http404, HttpResponse
from django.db import connection
from mitxmako.shortcuts import render_to_response

from django.contrib.auth.models import User
from student.models import CourseEnrollment
from certificates.models import GeneratedCertificate


def parse_course_id(course_id):
    """
    Return the org, course, and run given a course_id slug
    
    >>> org, course, run = parse_course_id("MITx/6.002x/2012_Spring")
    >>> org
    MITx
    >>> course
    6.002x
    >>> run
    2012_Spring

    """
    return course_id.split("/")


def dictfetchall(cursor):
    """
    Returns a list of all rows from a cursor as a column: result dict.
    Borrowed from Django documentation
    """
    desc = cursor.description
    table = []
    table.append([col[0] for col in desc])

    # ensure response from db is a list, not a tuple (which is returned
    # by MySQL backed django instances)
    rows_from_cursor = cursor.fetchall()
    table = table + [list(row) for row in rows_from_cursor]
    return table


def sql_result(cursor, query_string):
    """
    Executes a raw query and returns the result as a list
    where each element is a row of the result.
    """
    cursor.execute(query_string)
    raw_result = dictfetchall(cursor)
    return raw_result


def enrollment_history_map(request, days=7):
    """
    Returns a json object mapping each course_id to the number
    of enrollments in that course in the last `days`
    """
    if not request.user.is_staff:
        raise Http404

    cursor = connection.cursor()

    # current time as a string
    start_of_interval = time.strftime("%Y-%m-%d %H:%M:%S", (datetime.now() - timedelta(days, 0)).timetuple())

    # get a list of lists [[course_id, enrollments in last 7 days ]]
    recent_enrollments = sql_result(cursor, """select course_id, count(*)
                                           from student_courseenrollment
                                           where '{week_ago}' < created
                                           group by course_id
                                           ;""".format(week_ago=start_of_interval))[1:]
    plottable_data = []
    for course_id, count in recent_enrollments:
        org, course, run = parse_course_id(course_id)
        plottable_data.append({
            "run": run,
            "course_name": course,
            "org": org,
            "value": count
        })

    data = {
        "type": "map",
        "value_type": "Enrollments this week",
        "courses": plottable_data
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')


def all_daily_values(sparse_daily_values):
    """
    Accepts a list of (date, value) pairs.

    Returns a complete list of pairs between the first and last date
    in that list with a value (that value being 0 if it doesn't exist in
    the sparse list argument)
    """
    if len(sparse_daily_values) == 0:
        # if no enrollments at all
        return []
    else:
        dt_val_lookup = {}
        for pair in sparse_daily_values:
            dt_val_lookup[as_pydt(pair[0])] = pair[1]

        first_date = min(dt_val_lookup.keys())
        last_date = max(dt_val_lookup.keys())

        for day in (first_date + timedelta(d) for d in range((last_date - first_date).days)):
            if day not in dt_val_lookup:
                dt_val_lookup[day] = 0

        # dump that lookup table back to a list with dates represented as ms since epoch
        all_enrollment_days = [(tojstime(d), dt_val_lookup[d]) for d in sorted(dt_val_lookup.keys())]

        return all_enrollment_days


def as_pydt(sqldate):
    """
    Returns the date in question as a python datetime

    Used because different db backends return different types
    """
    if isinstance(sqldate, unicode):
        # SQLite returns unicode
        pydt = datetime.strptime(sqldate, "%Y-%m-%d")
    elif isinstance(sqldate, date):
        # MySQL returns datetime.date
        pydt = datetime(sqldate.year, sqldate.month, sqldate.day)
    else:
        raise ValueError("Unknown datatype returned from django backend" + str(type(sqldate)))
    return pydt


def tojstime(some_date):
    """
    Take a date returned from the Django db backend and
    translate it into javascript time (ms since epoch)
    """
    # make sure the date is a pyhton datetime even if it's not what
    # we got from the database
    some_date = as_pydt(some_date)
    jsts = (some_date - datetime(1970, 1, 1)).total_seconds() * 1000
    return jsts


def enrollment_history_timeseries(request):
    """
    Return a json object representing enrollment history for edX as a whole.
    Format:
    {
        "type": "timeseries",
        "value_type": "enrollments over the last few weeks",
        "all_series":
        [
            {
                "label": "edX",
                "data": [
                    [date, value],
                    [date, value],
                    [date, value],
                    [date, value],
                    ...
                ]
            }
        ]
    }

    """
    if not request.user.is_staff:
        raise Http404

    cursor = connection.cursor()
    today = calendar.timegm(datetime.now().timetuple()) * 1000
    yesterday = today - 86400000
    day_before_yesterday = today - 86400000 * 2

    # get all sparse daily enrollment counts, ignore the headers
    daily_enrollments = sql_result(cursor, """select date(created), count(*)
                                           from student_courseenrollment
                                           group by date(created)
                                           order by date(created) asc;""")[1:]
    enrollments_each_day = all_daily_values(daily_enrollments)

    # get sparse daily signup counts, ignore the headers
    daily_signups = sql_result(cursor, """select date(date_joined), count(*)
                                           from auth_user
                                           group by date(date_joined)
                                           order by date(date_joined) asc;""")[1:]
    signups_each_day = all_daily_values(daily_signups)

    data = {
        "type": "timeseries",
        "all_series":
        [
            {
                "label": "Enrollments Each Day",
                "data": enrollments_each_day
            },
            {
                "label": "New Accounts Each Day",
                "data": signups_each_day
            }
        ]
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')


def course_summary_table():
    """
    Return a list of lists representing a table of course information.

    First inner list is the table headers and subsequent lists each represent
    the values of each header for each course.
    """

    # establish a direct connections to the database (for executing raw SQL)
    cursor = connection.cursor()
    enrollment_query = """
        select course_id as Course, count(user_id) as Students
        from student_courseenrollment
        group by course_id
        order by students desc;"""
    active_enrollment_query = """
        select course_id as Course, count(user_id) as Students
        from student_courseenrollment
        where is_active
        group by course_id
        order by students desc;"""
    certificate_query = """
        select course_id as Course, count(user_id) as Certificates
        from certificates_generatedcertificate
        where status="downloadable"
        group by course_id
        order by Certificates desc;
        """
    
    enrollments = sql_result(cursor, enrollment_query)
    enrollments_map = {row[0]: row[1] for row in enrollments[1:]}
    active_enrollments = sql_result(cursor, active_enrollment_query)
    active_enrollments_map = {row[0]: row[1] for row in active_enrollments[1:]}
    certificates = sql_result(cursor, certificate_query)
    certificates_map = {row[0]: row[1] for row in certificates[1:]}

    # New Headers
    headers = [["School", "Course", "Run", "Known Enrollees", "Active Enrollees", "Certificates", "% Certified"]]
    org_course_run_information = []
    # Updated Rows
    for course_id in set(certificates_map.keys()) | set(enrollments_map.keys()):
        org, course, run = parse_course_id(course_id)
        new_row = [
            org,
            course,
            run,
            enrollments_map.get(course_id, "-"),
            active_enrollments_map.get(course_id, "-"),
            certificates_map.get(course_id, "-")
        ]
        if course_id in certificates_map:
            # if we certified people calc % of known who were certified
            new_row.append("{0:.2f}".format(
                100.0 * certificates_map[course_id] / enrollments_map[course_id])
            )
        else:
            new_row.append("-")
        org_course_run_information.append(new_row)

    # sort by the number of enrolled students, descending
    org_course_run_information = sorted(org_course_run_information, key=itemgetter(3))
    org_course_run_information.reverse()

    return headers + org_course_run_information


def dashboard(request):
    """
    Shows Enrollment and Certification KPIs to edX Staff
    """
    # Show only to global staff users
    if not request.user.is_staff:
        raise Http404

    # Everything but the data for the charts are passed with the template
    results = {"scalars": [], "tables": {}}

    # Calculate heads up numbers
    results["scalars"].append(("Known Enrollments", CourseEnrollment.objects.count()))
    results["scalars"].append(("Active Enrollments", CourseEnrollment.objects.filter(is_active=True).count()))
    results["scalars"].append(("Users", User.objects.filter().count()))
    results["scalars"].append(
        ("Certificates Issued", GeneratedCertificate.objects.filter(status="downloadable").count())
    )

    # a summary list of lists (table) that shows enrollment and certificate information
    results["tables"]["Course Statistics"] = course_summary_table()

    context = {
        "results": results
    }

    return render_to_response("admin_dashboard.html", context)
