# Create your views here.
import json
import calendar
from time import strptime, strftime
from datetime import datetime, timedelta
from django.http import Http404, HttpResponse
from mitxmako.shortcuts import render_to_response
from django.db import connection

from student.models import CourseEnrollment, CourseEnrollmentAllowed
from certificates.models import GeneratedCertificate
from django.contrib.auth.models import User

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
    start_of_interval = strftime("%Y-%m-%d %H:%M:%S", (datetime.now() - timedelta(days, 0)).timetuple())
    print "summing enrollments since", start_of_interval

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

def tojstime(sqltime):
    print sqltime
    pydt = strptime(sqltime, "%Y-%m-%d")
    return calendar.timegm(pydt)*1000

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
    data = {
        "type": "timeseries",
        "value_type": "Enrollments over the last few weeks",
        "all_series": 
        [
            {
                "label": "edX-Wide Enrollments Each Day",
                "data": enrollments_each_day
            }
        ]
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')

def get_course_summary_table():
    # establish a direct connection to the database (for executing raw SQL)
    cursor = connection.cursor()
    enrollment_query = """
        select course_id as Course, count(user_id) as Students 
        from student_courseenrollment
        group by course_id
        order by students desc;"""
    certificate_query = """
        select course_id as Course, count(user_id) as Certificates 
        from certificates_generatedcertificate
        where status in ("downloadable", "restricted")
        group by course_id
        order by Certificates desc;
        """
    course_id_enrollments = SQL_query_to_list(cursor, enrollment_query)
    course_id_enrollments_map = {row[0]:row[1] for row in course_id_enrollments[1:]}
    course_id_certificates = SQL_query_to_list(cursor, certificate_query)
    course_id_certificates_map = {row[0]:row[1] for row in course_id_certificates[1:]}

    # New Headers
    org_course_run_information = [["School", "Course", "Run", "Enrollees", "Certificates"]]

    # Updated Rows
    for course_id in set(course_id_certificates_map.keys()) | set(course_id_enrollments_map.keys()):
        org, course, run = parse_course_id(course_id)
        new_row = [org, course, run, \
            course_id_enrollments_map.get(course_id, "-"), \
            course_id_certificates_map.get(course_id, "-")]
        org_course_run_information.append(new_row) 

    return org_course_run_information

    # define the queries that will generate our user-facing tables
    # table queries need not take the form of raw SQL, but do in this case since
    # the MySQL backend for django isn't very friendly with group by or distinct
    # table_queries = {}
    # table_queries["Course Enrollments"]= 
    # table_queries["Certificates Granted"]= 

    # # add the result for each of the table_queries to the results object
    # for query in table_queries.keys():
    #     cursor.execute(table_queries[query])
    #     results["tables"][query] = table_queries[query])

def dashboard(request):
    """
    Shows Enrollment and Certification KPIs to edX Staff

    """
    if not request.user.is_staff:
        raise Http404

    # results are passed to the template.  The template knows how to render
    # two types of results: scalars and tables.  Scalars should be represented
    # as "Visible Title": Value and tables should be lists of lists where each
    # inner list represents a single row of the table
    results = {"scalars":[],"tables":{}}

    results["scalars"].append(("Total Enrollments Across All Courses", CourseEnrollment.objects.count()))
    results["scalars"].append(("Unique Usernames", User.objects.filter().count()))
    results["scalars"].append(("Activated Usernames", User.objects.filter(is_active=1).count()))
    results["scalars"].append(("Certificates Issued", GeneratedCertificate.objects.filter(status="downloadable").count()))

    # a summary list of lists (table) that shows enrollment and certificate information
    results["tables"]["Course Enrollments"] = get_course_summary_table()

    context = {
        "results":results
    }

    return render_to_response("admin_dashboard.html",context)
