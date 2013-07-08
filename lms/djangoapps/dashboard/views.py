# Create your views here.
import json
import calendar
import functools
import time
from datetime import date, datetime, timedelta
from django.http import Http404, HttpResponse
from mitxmako.shortcuts import render_to_response
from django.db import connections
from django.conf import settings

from student.models import CourseEnrollment, CourseEnrollmentAllowed
from certificates.models import GeneratedCertificate
from django.contrib.auth.models import User

class prefer_secondary_db(object):
    """
    Decorator. 

    If an "replica" db is specified in django settings, 
    it is provided to the function as the the value of the
    argument `readonly_db`.

    Example:

    @prefer_secondary_db('replica')
    def count_users(secondary_db=None):
        assert secondary_db is not None
        return User.objects.using(secondary_db).filter().count()

    count_users()
    
    will provide different results depending on the dbs defined in
    settings.py.  If a database named 'replica' is defined, it will
    return the number of users in the replica database.  If no such
    db is specified, it will return the number of users in the default
    db

    """
    def __init__(self, secondary_db):
        if secondary_db in settings.DATABASES:
            self.secondary_db = secondary_db
        else:
            self.secondary_db = 'default'

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            print "calling wrapped function with args", args, "end of args"
            kwargs['secondary_db'] = self.secondary_db
            print "calling wrapped function with kwargs", kwargs
            return fn(*args, **kwargs)

        return decorated

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

@prefer_secondary_db('replica')
def enrollment_history_map(request, days=7, secondary_db=None):
    """
    Returns a json object mapping each course_id to the number
    of enrollments in that course in the last `days`

    """
    if not request.user.is_staff:
        raise Http404
    assert secondary_db is not None

    cursor = connections[secondary_db].cursor() 
    
    # current time as a string
    start_of_interval = time.strftime("%Y-%m-%d %H:%M:%S", (datetime.now() - timedelta(days, 0)).timetuple())
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

def tojstime(sqldate):
    print "Converting", sqldate, "to jstime.  It's of type", type(sqldate)
    pydt = None

    # depending on which db backend the django orm uses, we get different
    # types back on this query
    if isinstance(sqldate, unicode):
        # SQLite returns unicode
        pydt = datetime.strptime(sqldate, "%Y-%m-%d")
    elif isinstance(sqldate, date):
        # MySQL returns datetime.date 
        pydt = datetime(sqldate.year, sqldate.month, sqldate.day)
    
    print "python datetime is", pydt, type(pydt)
    jsts = (pydt - datetime(1970, 1, 1)).total_seconds()*1000
    print "jstime timestamp is", jsts
    return jsts

@prefer_secondary_db('replica')
def enrollment_history_timeseries(request, secondary_db=None):
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
    assert secondary_db is not None
    
    cursor = connections[secondary_db].cursor()
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

@prefer_secondary_db('replica')
def get_course_summary_table(secondary_db=None):
    # establish a direct connections to the database (for executing raw SQL)
    cursor = connections[secondary_db].cursor()
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

@prefer_secondary_db('replica')
def dashboard(request, secondary_db=None):
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

    results["scalars"].append(("Total Enrollments Across All Courses", CourseEnrollment.objects.using(secondary_db).count()))
    results["scalars"].append(("Unique Usernames", User.objects.using(secondary_db).filter().count()))
    results["scalars"].append(("Activated Usernames", User.objects.using(secondary_db).filter(is_active=1).count()))
    results["scalars"].append(("Certificates Issued", GeneratedCertificate.objects.using(secondary_db).filter(status="downloadable").count() + 7157))
 
    # a summary list of lists (table) that shows enrollment and certificate information
    results["tables"]["Course Enrollments"] = get_course_summary_table()

    context = {
        "results":results
    }

    return render_to_response("admin_dashboard.html",context)
