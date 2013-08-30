import json
import calendar
import time
from datetime import date, datetime, timedelta
from operator import itemgetter

from django.http import Http404, HttpResponse
from django.db import connection
from django.conf import settings
from mitxmako.shortcuts import render_to_response

from django.contrib.auth.models import User
from student.models import CourseEnrollment, CourseEnrollmentAllowed
from certificates.models import GeneratedCertificate
from util.databases import prefer_alternate_db

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
    '''Returns a list of all rows from a cursor as a column: result dict.
    Borrowed from Django documentation'''
    desc = cursor.description
    table = []
    table.append([col[0] for col in desc])
    
    # ensure response from db is a list, not a tuple (which is returned
    # by MySQL backed django instances)
    rows_from_cursor=cursor.fetchall()
    table = table + [list(row) for row in rows_from_cursor]
    return table

def SQL_query_to_list(cursor, query_string):
    cursor.execute(query_string)
    raw_result=dictfetchall(cursor)
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
    recent_enrollments = SQL_query_to_list(cursor, """select course_id, count(*) 
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

def tojstime(sqldate):
    pydt = None

    # depending on which db backend the django orm uses, we get different
    # types back on this query
    if isinstance(sqldate, unicode):
        # SQLite returns unicode
        pydt = datetime.strptime(sqldate, "%Y-%m-%d")
    elif isinstance(sqldate, date):
        # MySQL returns datetime.date 
        pydt = datetime(sqldate.year, sqldate.month, sqldate.day)
    
    jsts = (pydt - datetime(1970, 1, 1)).total_seconds()*1000
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
    day_before_yesterday = today - 86400000*2
    
    # get all daily enrollment counts, ignore the headers
    daily_enrollments = SQL_query_to_list(cursor, """select date(created), count(*) 
                                           from student_courseenrollment 
                                           group by date(created)
                                           order by date(created) asc;""")[1:]    
    enrollments_each_day = [[tojstime(entry[0]), entry[1]] for entry in daily_enrollments]
    
    # get all daily signup counts, ignore the headers
    daily_signups = SQL_query_to_list(cursor, """select date(date_joined), count(*) 
                                           from auth_user 
                                           group by date(date_joined)
                                           order by date(date_joined) asc;""")[1:]    
    signups_each_day = [[tojstime(entry[0]), entry[1]] for entry in daily_signups]
   
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

def get_course_summary_table():
    # establish a direct connections to the database (for executing raw SQL)
    cursor = connection.cursor()
    enrollment_query = """
        select course_id as Course, count(user_id) as Students 
        from student_courseenrollment
        group by course_id
        order by students desc;"""
    certificate_query = """
        select course_id as Course, count(user_id) as Certificates 
        from certificates_generatedcertificate
        where status="downloadable"
        group by course_id
        order by Certificates desc;
        """
    course_id_enrollments = SQL_query_to_list(cursor, enrollment_query)
    course_id_enrollments_map = {row[0]:row[1] for row in course_id_enrollments[1:]}
    course_id_certificates = SQL_query_to_list(cursor, certificate_query)
    course_id_certificates_map = {row[0]:row[1] for row in course_id_certificates[1:]}

    # New Headers
    headers = [["School", "Course", "Run", "Current Enrollees", "Certificates", "% Certified"]]
    org_course_run_information = []
    # Updated Rows
    for course_id in set(course_id_certificates_map.keys()) | set(course_id_enrollments_map.keys()):
        org, course, run = parse_course_id(course_id)
        new_row = [org, course, run, \
            course_id_enrollments_map.get(course_id, "-"), \
            course_id_certificates_map.get(course_id, "-")]
        if new_row[-1] is not "-":
            new_row.append("{0:.2f}".format(100.0*new_row[-1]/new_row[-2]))
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
    results = {"scalars":[],"tables":{}}

    # Calculate heads up numbers
    results["scalars"].append(("Enrollments", CourseEnrollment.objects.count()))
    results["scalars"].append(("Users", User.objects.filter().count()))
    results["scalars"].append(("Certificates Issued", GeneratedCertificate.objects.filter(status="downloadable").count() + settings.MITX_FEATURES.get('LEGACY_CERT_COUNT', 0)))
 
    # a summary list of lists (table) that shows enrollment and certificate information
    results["tables"]["Course Statistics"] = get_course_summary_table()

    context = {
        "results": results
    }

    return render_to_response("admin_dashboard.html",context)
