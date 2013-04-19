# Create your views here.
import json
import calendar
from time import strptime, strftime
from datetime import datetime, timedelta
from django.http import Http404, HttpResponse
from mitxmako.shortcuts import render_to_response
from django.db import connection

from student.models import CourseEnrollment, CourseEnrollmentAllowed
from django.contrib.auth.models import User


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


def enrollment_history_map(request):
    """
    A demo hack to return enrollment history, per course.

    """
    if not request.user.is_staff:
        raise Http404
    cursor = connection.cursor()
    
    # current time as a string
    one_week_ago = strftime("%Y-%m-%d %H:%M:%S", (datetime.now() - timedelta(7, 0)).timetuple())
    print "one week ago was", one_week_ago

    # get a list of lists [[course_id, enrollments in last 7 days ]]
    recent_enrollments = SQL_query_to_list(cursor, """select course_id, count(*) 
                                           from student_courseenrollment 
                                           where '{week_ago}' < created
                                           group by course_id
                                           ;""".format(week_ago=one_week_ago))[1:]  
    plottable_data = []
    for course_id, count in recent_enrollments:
        org, course, run = course_id.split("/")
        plottable_data.append({
            "run": run,
            "course_name": course,
            "org": org,
            "value": count
            })
    
    data = {
        "type": "map",
        "value_type": "Enrollements by course",
        "courses": plottable_data
    }
    
    return HttpResponse(json.dumps(data), mimetype='application/json')

def tojstime(sqltime):
    print sqltime
    pydt = strptime(sqltime, "%Y-%m-%d")
    return calendar.timegm(pydt)*1000

def enrollment_history_timeseries(request):
    """
    A demo hack to return enrollment history, per course.

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
    plottable_data = [[tojstime(entry[0]) ,entry[1]] for entry in daily_enrollments]
    print plottable_data
    data = {
        "type": "timeseries",
        "value_type": "Enrollments over the last few weeks",
        "all_series": 
        [
            {
                "label": "edX",
                "data": plottable_data
            }
        ]
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')

def dashboard(request):
    """
    Slightly less hackish hack to show staff enrollment numbers and other
    simple queries.  

    All queries here should be indexed and simple.  Mostly, this means don't
    touch courseware_studentmodule, as tempting as it may be.

    """
    if not request.user.is_staff:
        raise Http404

    # results are passed to the template.  The template knows how to render
    # two types of results: scalars and tables.  Scalars should be represented
    # as "Visible Title": Value and tables should be lists of lists where each
    # inner list represents a single row of the table
    results = {"scalars":{},"tables":{}}

    # count how many users we have
    results["scalars"]["Unique Usernames"]=User.objects.filter().count()
    results["scalars"]["Activated Usernames"]=User.objects.filter(is_active=1).count()
    
    # count how many enrollments we have
    results["scalars"]["Total Enrollments Across All Courses"]=CourseEnrollment.objects.count()

    # establish a direct connection to the database (for executing raw SQL)
    cursor = connection.cursor()

    # define the queries that will generate our user-facing tables
    # table queries need not take the form of raw SQL, but do in this case since
    # the MySQL backend for django isn't very friendly with group by or distinct
    table_queries = {}
    table_queries["course enrollments"]= """
        select course_id as Course, count(user_id) as Students 
        from student_courseenrollment
        group by course_id
        order by students desc;"""
    table_queries["number of students in each number of classes"]= """
        select registrations as 'Registered for __ Classes',
        count(registrations) as Users
        from (select count(user_id) as registrations
               from student_courseenrollment
               group by user_id) as registrations_per_user
        group by registrations;"""

    # add the result for each of the table_queries to the results object
    for query in table_queries.keys():
        cursor.execute(table_queries[query])
        results["tables"][query] = SQL_query_to_list(cursor, table_queries[query])

    context={"results":results

    }

    return render_to_response("admin_dashboard.html",context)
