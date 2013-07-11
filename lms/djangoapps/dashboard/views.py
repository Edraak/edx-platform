from django.http import Http404
from mitxmako.shortcuts import render_to_response
from django.db import connections

from student.models import CourseEnrollment
from django.contrib.auth.models import User
from util.databases import prefer_alternate_db


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

@prefer_alternate_db('replica')
def dashboard(request, alternate_db=None):
    """
    Slightly less hackish hack to show staff enrollment numbers and other
    simple queries.  

    All queries here should be indexed and simple.  Mostly, this means don't
    touch courseware_studentmodule, as tempting as it may be.

    """
    if not request.user.is_staff:
        raise Http404

    results = {"scalars":{},"tables":{}}

    results["scalars"]["Total Enrollments Across All Courses"] = CourseEnrollment.objects.using(alternate_db).count()
    results["scalars"]["Unique Usernames"] = User.objects.using(alternate_db).filter().count()
    results["scalars"]["Activated Usernames"] = User.objects.using(alternate_db).filter(is_active=1).count()
    # establish a direct connection to the database (for executing raw SQL)
    cursor = connections[alternate_db].cursor()

    # define the queries that will generate our user-facing tables
    # table queries need not take the form of raw SQL, but do in this case since
    # the MySQL backend for django isn't very friendly with group by or distinct
    table_queries = {}
    table_queries["course enrollments"]= \
        "select "+ \
        "course_id as Course, "+ \
        "count(user_id) as Students " + \
        "from student_courseenrollment "+ \
        "group by course_id "+ \
        "order by students desc;"
    table_queries["number of students in each number of classes"]= \
        "select registrations as 'Registered for __ Classes' , "+ \
        "count(registrations) as Users "+ \
        "from (select count(user_id) as registrations "+ \
               "from student_courseenrollment "+ \
               "group by user_id) as registrations_per_user "+ \
        "group by registrations;"

    # add the result for each of the table_queries to the results object
    for query in table_queries.keys():
        cursor.execute(table_queries[query])
        results["tables"][query] = SQL_query_to_list(cursor, table_queries[query])

    context={"results":results}

    return render_to_response("admin_dashboard.html",context)
