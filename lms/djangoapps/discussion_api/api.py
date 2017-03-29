"""
Discussion API internal interface
"""
from collections import defaultdict
from urllib import urlencode
from urlparse import urlunparse

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import Http404
import itertools

from rest_framework.exceptions import PermissionDenied

from opaque_keys import InvalidKeyError
from opaque_keys.edx.locator import CourseKey
from courseware.courses import get_course_with_access

from discussion_api.exceptions import ThreadNotFoundError, CommentNotFoundError, DiscussionDisabledError
from discussion_api.forms import CommentActionsForm, ThreadActionsForm
from discussion_api.permissions import (
    can_delete,
    get_editable_fields,
    get_initializable_comment_fields,
    get_initializable_thread_fields,
)
from discussion_api.serializers import CommentSerializer, ThreadSerializer, get_context
from django_comment_client.base.views import track_comment_created_event, track_thread_created_event
from django_comment_common.signals import (
    thread_created,
    thread_edited,
    thread_deleted,
    thread_voted,
    comment_created,
    comment_edited,
    comment_voted,
    comment_deleted,
)
from django_comment_client.utils import get_accessible_discussion_modules, is_commentable_cohorted
from lms.djangoapps.discussion_api.pagination import DiscussionAPIPagination
from lms.lib.comment_client.comment import Comment
from lms.lib.comment_client.thread import Thread
from lms.lib.comment_client.utils import CommentClientRequestError
from openedx.core.djangoapps.course_groups.cohorts import get_cohort_id
from openedx.core.lib.exceptions import CourseNotFoundError, PageNotFoundError


def _get_course(course_key, user):
    """
    Get the course descriptor, raising CourseNotFoundError if the course is not found or
    the user cannot access forums for the course, and DiscussionDisabledError if the
    discussion tab is disabled for the course.
    """
    try:
        course = get_course_with_access(user, 'load', course_key, check_if_enrolled=True)
    except Http404:
        raise CourseNotFoundError("Course not found.")
    if not any([tab.type == 'discussion' and tab.is_enabled(course, user) for tab in course.tabs]):
        raise DiscussionDisabledError("Discussion is disabled for the course.")
    return course


def _get_thread_and_context(request, thread_id, retrieve_kwargs=None):
    """
    Retrieve the given thread and build a serializer context for it, returning
    both. This function also enforces access control for the thread (checking
    both the user's access to the course and to the thread's cohort if
    applicable). Raises ThreadNotFoundError if the thread does not exist or the
    user cannot access it.
    """
    retrieve_kwargs = retrieve_kwargs or {}
    try:
        if "mark_as_read" not in retrieve_kwargs:
            retrieve_kwargs["mark_as_read"] = False
        cc_thread = Thread(id=thread_id).retrieve(**retrieve_kwargs)
        course_key = CourseKey.from_string(cc_thread["course_id"])
        course = _get_course(course_key, request.user)
        context = get_context(course, request, cc_thread)
        if (
                not context["is_requester_privileged"] and
                cc_thread["group_id"] and
                is_commentable_cohorted(course.id, cc_thread["commentable_id"])
        ):
            requester_cohort = get_cohort_id(request.user, course.id)
            if requester_cohort is not None and cc_thread["group_id"] != requester_cohort:
                raise ThreadNotFoundError("Thread not found.")
        return cc_thread, context
    except CommentClientRequestError:
        # params are validated at a higher level, so the only possible request
        # error is if the thread doesn't exist
        raise ThreadNotFoundError("Thread not found.")


def _get_comment_and_context(request, comment_id):
    """
    Retrieve the given comment and build a serializer context for it, returning
    both. This function also enforces access control for the comment (checking
    both the user's access to the course and to the comment's thread's cohort if
    applicable). Raises CommentNotFoundError if the comment does not exist or the
    user cannot access it.
    """
    try:
        cc_comment = Comment(id=comment_id).retrieve()
        _, context = _get_thread_and_context(request, cc_comment["thread_id"])
        return cc_comment, context
    except CommentClientRequestError:
        raise CommentNotFoundError("Comment not found.")


def _is_user_author_or_privileged(cc_content, context):
    """
    Check if the user is the author of a content object or a privileged user.

    Returns:
        Boolean
    """
    return (
        context["is_requester_privileged"] or
        context["cc_requester"]["id"] == cc_content["user_id"]
    )


def get_thread_list_url(request, course_key, topic_id_list=None, following=False):
    """
    Returns the URL for the thread_list_url field, given a list of topic_ids
    """
    path = reverse("thread-list")
    query_list = (
        [("course_id", unicode(course_key))] +
        # Edraak (fix): Supporting some of the discussion topics written in Arabic
        [("topic_id", topic_id.encode('utf-8')) for topic_id in topic_id_list or []] +
        ([("following", following)] if following else [])
    )
    return request.build_absolute_uri(urlunparse(("", "", path, "", urlencode(query_list), "")))


def get_course(request, course_key):
    """
    Return general discussion information for the course.

    Parameters:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        course_key: The key of the course to get information for

    Returns:

        The course information; see discussion_api.views.CourseView for more
        detail.

    Raises:

        CourseNotFoundError: if the course does not exist or is not accessible
        to the requesting user
    """
    course = _get_course(course_key, request.user)
    return {
        "id": unicode(course_key),
        "blackouts": [
            {"start": blackout["start"].isoformat(), "end": blackout["end"].isoformat()}
            for blackout in course.get_discussion_blackout_datetimes()
        ],
        "thread_list_url": get_thread_list_url(request, course_key),
        "following_thread_list_url": get_thread_list_url(request, course_key, following=True),
        "topics_url": request.build_absolute_uri(
            reverse("course_topics", kwargs={"course_id": course_key})
        )
    }


def get_course_topics(request, course_key):
    """
    Return the course topic listing for the given course and user.

    Parameters:

    course_key: The key of the course to get topics for
    user: The requesting user, for access control

    Returns:

    A course topic listing dictionary; see discussion_api.views.CourseTopicViews
    for more detail.
    """
    def get_module_sort_key(module):
        """
        Get the sort key for the module (falling back to the discussion_target
        setting if absent)
        """
        return module.sort_key or module.discussion_target
    course = _get_course(course_key, request.user)
    discussion_modules = get_accessible_discussion_modules(course, request.user)
    modules_by_category = defaultdict(list)
    for module in discussion_modules:
        modules_by_category[module.discussion_category].append(module)

    def get_sorted_modules(category):
        """Returns key sorted modules by category"""
        return sorted(modules_by_category[category], key=get_module_sort_key)

    courseware_topics = [
        {
            "id": None,
            "name": category,
            "thread_list_url": get_thread_list_url(
                request,
                course_key,
                [item.discussion_id for item in get_sorted_modules(category)]
            ),
            "children": [
                {
                    "id": module.discussion_id,
                    "name": module.discussion_target,
                    "thread_list_url": get_thread_list_url(request, course_key, [module.discussion_id]),
                    "children": [],
                }
                for module in get_sorted_modules(category)
            ],
        }
        for category in sorted(modules_by_category.keys())
    ]

    non_courseware_topics = [
        {
            "id": entry["id"],
            "name": name,
            "thread_list_url": get_thread_list_url(request, course_key, [entry["id"]]),
            "children": [],
        }
        for name, entry in sorted(
            course.discussion_topics.items(),
            key=lambda item: item[1].get("sort_key", item[0])
        )
    ]

    return {
        "courseware_topics": courseware_topics,
        "non_courseware_topics": non_courseware_topics,
    }


def get_thread_list(
        request,
        course_key,
        page,
        page_size,
        topic_id_list=None,
        text_search=None,
        following=False,
        view=None,
        order_by="last_activity_at",
        order_direction="desc",
):
    """
    Return the list of all discussion threads pertaining to the given course

    Parameters:

    request: The django request objects used for build_absolute_uri
    course_key: The key of the course to get discussion threads for
    page: The page number (1-indexed) to retrieve
    page_size: The number of threads to retrieve per page
    topic_id_list: The list of topic_ids to get the discussion threads for
    text_search A text search query string to match
    following: If true, retrieve only threads the requester is following
    view: filters for either "unread" or "unanswered" threads
    order_by: The key in which to sort the threads by. The only values are
        "last_activity_at", "comment_count", and "vote_count". The default is
        "last_activity_at".
    order_direction: The direction in which to sort the threads by. The only
        values are "asc" or "desc". The default is "desc".

    Note that topic_id_list, text_search, and following are mutually exclusive.

    Returns:

    A paginated result containing a list of threads; see
    discussion_api.views.ThreadViewSet for more detail.

    Raises:

    ValidationError: if an invalid value is passed for a field.
    ValueError: if more than one of the mutually exclusive parameters is
      provided
    CourseNotFoundError: if the requesting user does not have access to the requested course
    PageNotFoundError: if page requested is beyond the last
    """
    exclusive_param_count = sum(1 for param in [topic_id_list, text_search, following] if param)
    if exclusive_param_count > 1:  # pragma: no cover
        raise ValueError("More than one mutually exclusive param passed to get_thread_list")

    cc_map = {"last_activity_at": "activity", "comment_count": "comments", "vote_count": "votes"}
    if order_by not in cc_map:
        raise ValidationError({
            "order_by":
                ["Invalid value. '{}' must be 'last_activity_at', 'comment_count', or 'vote_count'".format(order_by)]
        })
    if order_direction not in ["asc", "desc"]:
        raise ValidationError({
            "order_direction": ["Invalid value. '{}' must be 'asc' or 'desc'".format(order_direction)]
        })

    course = _get_course(course_key, request.user)
    context = get_context(course, request)

    query_params = {
        "user_id": unicode(request.user.id),
        "group_id": (
            None if context["is_requester_privileged"] else
            get_cohort_id(request.user, course.id)
        ),
        "page": page,
        "per_page": page_size,
        "text": text_search,
        "sort_key": cc_map.get(order_by),
        "sort_order": order_direction,
    }

    text_search_rewrite = None

    if view:
        if view in ["unread", "unanswered"]:
            query_params[view] = "true"
        else:
            ValidationError({
                "view": ["Invalid value. '{}' must be 'unread' or 'unanswered'".format(view)]
            })

    if following:
        paginated_results = context["cc_requester"].subscribed_threads(query_params)
    else:
        query_params["course_id"] = unicode(course.id)
        query_params["commentable_ids"] = ",".join(topic_id_list) if topic_id_list else None
        query_params["text"] = text_search
        paginated_results = Thread.search(query_params)
    # The comments service returns the last page of results if the requested
    # page is beyond the last page, but we want be consistent with DRF's general
    # behavior and return a PageNotFoundError in that case
    if paginated_results.page != page:
        raise PageNotFoundError("Page not found (No results on this page).")

    results = [ThreadSerializer(thread, context=context).data for thread in paginated_results.collection]

    paginator = DiscussionAPIPagination(
        request,
        paginated_results.page,
        paginated_results.num_pages,
        paginated_results.thread_count
    )
    return paginator.get_paginated_response({
        "results": results,
        "text_search_rewrite": paginated_results.corrected_text,
    })


def get_comment_list(request, thread_id, endorsed, page, page_size):
    """
    Return the list of comments in the given thread.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        thread_id: The id of the thread to get comments for.

        endorsed: Boolean indicating whether to get endorsed or non-endorsed
          comments (or None for all comments). Must be None for a discussion
          thread and non-None for a question thread.

        page: The page number (1-indexed) to retrieve

        page_size: The number of comments to retrieve per page

    Returns:

        A paginated result containing a list of comments; see
        discussion_api.views.CommentViewSet for more detail.
    """
    response_skip = page_size * (page - 1)
    cc_thread, context = _get_thread_and_context(
        request,
        thread_id,
        retrieve_kwargs={
            "recursive": False,
            "user_id": request.user.id,
            "response_skip": response_skip,
            "response_limit": page_size,
        }
    )

    # Responses to discussion threads cannot be separated by endorsed, but
    # responses to question threads must be separated by endorsed due to the
    # existing comments service interface
    if cc_thread["thread_type"] == "question":
        if endorsed is None:
            raise ValidationError({"endorsed": ["This field is required for question threads."]})
        elif endorsed:
            # CS does not apply resp_skip and resp_limit to endorsed responses
            # of a question post
            responses = cc_thread["endorsed_responses"][response_skip:(response_skip + page_size)]
            resp_total = len(cc_thread["endorsed_responses"])
        else:
            responses = cc_thread["non_endorsed_responses"]
            resp_total = cc_thread["non_endorsed_resp_total"]
    else:
        if endorsed is not None:
            raise ValidationError(
                {"endorsed": ["This field may not be specified for discussion threads."]}
            )
        responses = cc_thread["children"]
        resp_total = cc_thread["resp_total"]

    # The comments service returns the last page of results if the requested
    # page is beyond the last page, but we want be consistent with DRF's general
    # behavior and return a PageNotFoundError in that case
    if not responses and page != 1:
        raise PageNotFoundError("Page not found (No results on this page).")
    num_pages = (resp_total + page_size - 1) / page_size if resp_total else 1

    results = [CommentSerializer(response, context=context).data for response in responses]
    paginator = DiscussionAPIPagination(request, page, num_pages, resp_total)
    return paginator.get_paginated_response(results)


def _check_fields(allowed_fields, data, message):
    """
    Checks that the keys given in data is in allowed_fields

    Arguments:
        allowed_fields (set): A set of allowed fields
        data (dict): The data to compare the allowed_fields against
        message (str): The message to return if there are any invalid fields

    Raises:
        ValidationError if the given data contains a key that is not in
            allowed_fields
    """
    non_allowed_fields = {field: [message] for field in data.keys() if field not in allowed_fields}
    if non_allowed_fields:
        raise ValidationError(non_allowed_fields)


def _check_initializable_thread_fields(data, context):  # pylint: disable=invalid-name
    """
    Checks if the given data contains a thread field that is not initializable
    by the requesting user

    Arguments:
        data (dict): The data to compare the allowed_fields against
        context (dict): The context appropriate for use with the thread which
            includes the requesting user

    Raises:
        ValidationError if the given data contains a thread field that is not
            initializable by the requesting user
    """
    _check_fields(
        get_initializable_thread_fields(context),
        data,
        "This field is not initializable."
    )


def _check_initializable_comment_fields(data, context):  # pylint: disable=invalid-name
    """
    Checks if the given data contains a comment field that is not initializable
    by the requesting user

    Arguments:
        data (dict): The data to compare the allowed_fields against
        context (dict): The context appropriate for use with the comment which
            includes the requesting user

    Raises:
        ValidationError if the given data contains a comment field that is not
            initializable by the requesting user
    """
    _check_fields(
        get_initializable_comment_fields(context),
        data,
        "This field is not initializable."
    )


def _check_editable_fields(cc_content, data, context):
    """
    Raise ValidationError if the given update data contains a field that is not
    editable by the requesting user
    """
    _check_fields(
        get_editable_fields(cc_content, context),
        data,
        "This field is not editable."
    )


def _do_extra_actions(api_content, cc_content, request_fields, actions_form, context):
    """
    Perform any necessary additional actions related to content creation or
    update that require a separate comments service request.
    """
    for field, form_value in actions_form.cleaned_data.items():
        if field in request_fields and form_value != api_content[field]:
            api_content[field] = form_value
            if field == "following":
                if form_value:
                    context["cc_requester"].follow(cc_content)
                else:
                    context["cc_requester"].unfollow(cc_content)
            elif field == "abuse_flagged":
                if form_value:
                    cc_content.flagAbuse(context["cc_requester"], cc_content)
                else:
                    cc_content.unFlagAbuse(context["cc_requester"], cc_content, removeAll=False)
            else:
                assert field == "voted"
                signal = thread_voted if cc_content.type == 'thread' else comment_voted
                signal.send(sender=None, user=context["request"].user, post=cc_content)
                if form_value:
                    context["cc_requester"].vote(cc_content, "up")
                    api_content["vote_count"] += 1
                else:
                    context["cc_requester"].unvote(cc_content)
                    api_content["vote_count"] -= 1


def create_thread(request, thread_data):
    """
    Create a thread.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        thread_data: The data for the created thread.

    Returns:

        The created thread; see discussion_api.views.ThreadViewSet for more
        detail.
    """
    course_id = thread_data.get("course_id")
    user = request.user
    if not course_id:
        raise ValidationError({"course_id": ["This field is required."]})
    try:
        course_key = CourseKey.from_string(course_id)
        course = _get_course(course_key, user)
    except InvalidKeyError:
        raise ValidationError({"course_id": ["Invalid value."]})

    context = get_context(course, request)
    _check_initializable_thread_fields(thread_data, context)
    if (
            "group_id" not in thread_data and
            is_commentable_cohorted(course_key, thread_data.get("topic_id"))
    ):
        thread_data = thread_data.copy()
        thread_data["group_id"] = get_cohort_id(user, course_key)
    serializer = ThreadSerializer(data=thread_data, context=context)
    actions_form = ThreadActionsForm(thread_data)
    if not (serializer.is_valid() and actions_form.is_valid()):
        raise ValidationError(dict(serializer.errors.items() + actions_form.errors.items()))
    serializer.save()
    cc_thread = serializer.instance
    thread_created.send(sender=None, user=user, post=cc_thread)
    api_thread = serializer.data
    _do_extra_actions(api_thread, cc_thread, thread_data.keys(), actions_form, context)

    track_thread_created_event(request, course, cc_thread, actions_form.cleaned_data["following"])

    return api_thread


def create_comment(request, comment_data):
    """
    Create a comment.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        comment_data: The data for the created comment.

    Returns:

        The created comment; see discussion_api.views.CommentViewSet for more
        detail.
    """
    thread_id = comment_data.get("thread_id")
    if not thread_id:
        raise ValidationError({"thread_id": ["This field is required."]})
    cc_thread, context = _get_thread_and_context(request, thread_id)

    # if a thread is closed; no new comments could be made to it
    if cc_thread['closed']:
        raise PermissionDenied

    _check_initializable_comment_fields(comment_data, context)
    serializer = CommentSerializer(data=comment_data, context=context)
    actions_form = CommentActionsForm(comment_data)
    if not (serializer.is_valid() and actions_form.is_valid()):
        raise ValidationError(dict(serializer.errors.items() + actions_form.errors.items()))
    serializer.save()
    cc_comment = serializer.instance
    comment_created.send(sender=None, user=request.user, post=cc_comment)
    api_comment = serializer.data
    _do_extra_actions(api_comment, cc_comment, comment_data.keys(), actions_form, context)

    track_comment_created_event(request, context["course"], cc_comment, cc_thread["commentable_id"], followed=False)

    return api_comment


def update_thread(request, thread_id, update_data):
    """
    Update a thread.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        thread_id: The id for the thread to update.

        update_data: The data to update in the thread.

    Returns:

        The updated thread; see discussion_api.views.ThreadViewSet for more
        detail.
    """
    cc_thread, context = _get_thread_and_context(request, thread_id)
    _check_editable_fields(cc_thread, update_data, context)
    serializer = ThreadSerializer(cc_thread, data=update_data, partial=True, context=context)
    actions_form = ThreadActionsForm(update_data)
    if not (serializer.is_valid() and actions_form.is_valid()):
        raise ValidationError(dict(serializer.errors.items() + actions_form.errors.items()))
    # Only save thread object if some of the edited fields are in the thread data, not extra actions
    if set(update_data) - set(actions_form.fields):
        serializer.save()
        # signal to update Teams when a user edits a thread
        thread_edited.send(sender=None, user=request.user, post=cc_thread)
    api_thread = serializer.data
    _do_extra_actions(api_thread, cc_thread, update_data.keys(), actions_form, context)
    return api_thread


def update_comment(request, comment_id, update_data):
    """
    Update a comment.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        comment_id: The id for the comment to update.

        update_data: The data to update in the comment.

    Returns:

        The updated comment; see discussion_api.views.CommentViewSet for more
        detail.

    Raises:

        CommentNotFoundError: if the comment does not exist or is not accessible
        to the requesting user

        PermissionDenied: if the comment is accessible to but not editable by
          the requesting user

        ValidationError: if there is an error applying the update (e.g. raw_body
          is empty or thread_id is included)
    """
    cc_comment, context = _get_comment_and_context(request, comment_id)
    _check_editable_fields(cc_comment, update_data, context)
    serializer = CommentSerializer(cc_comment, data=update_data, partial=True, context=context)
    actions_form = CommentActionsForm(update_data)
    if not (serializer.is_valid() and actions_form.is_valid()):
        raise ValidationError(dict(serializer.errors.items() + actions_form.errors.items()))
    # Only save comment object if some of the edited fields are in the comment data, not extra actions
    if set(update_data) - set(actions_form.fields):
        serializer.save()
        comment_edited.send(sender=None, user=request.user, post=cc_comment)
    api_comment = serializer.data
    _do_extra_actions(api_comment, cc_comment, update_data.keys(), actions_form, context)
    return api_comment


def get_thread(request, thread_id):
    """
    Retrieve a thread.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        thread_id: The id for the thread to retrieve

    """
    cc_thread, context = _get_thread_and_context(
        request,
        thread_id,
        retrieve_kwargs={"user_id": unicode(request.user.id)}
    )
    serializer = ThreadSerializer(cc_thread, context=context)
    return serializer.data


def get_response_comments(request, comment_id, page, page_size):
    """
    Return the list of comments for the given thread response.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        comment_id: The id of the comment/response to get child comments for.

        page: The page number (1-indexed) to retrieve

        page_size: The number of comments to retrieve per page

    Returns:

        A paginated result containing a list of comments

    """
    try:
        cc_comment = Comment(id=comment_id).retrieve()
        cc_thread, context = _get_thread_and_context(
            request,
            cc_comment["thread_id"],
            retrieve_kwargs={
                "recursive": True,
            }
        )
        if cc_thread["thread_type"] == "question":
            thread_responses = itertools.chain(cc_thread["endorsed_responses"], cc_thread["non_endorsed_responses"])
        else:
            thread_responses = cc_thread["children"]
        response_comments = []
        for response in thread_responses:
            if response["id"] == comment_id:
                response_comments = response["children"]
                break

        response_skip = page_size * (page - 1)
        paged_response_comments = response_comments[response_skip:(response_skip + page_size)]
        if len(paged_response_comments) == 0 and page != 1:
            raise PageNotFoundError("Page not found (No results on this page).")

        results = [CommentSerializer(comment, context=context).data for comment in paged_response_comments]

        comments_count = len(response_comments)
        num_pages = (comments_count + page_size - 1) / page_size if comments_count else 1
        paginator = DiscussionAPIPagination(request, page, num_pages, comments_count)
        return paginator.get_paginated_response(results)
    except CommentClientRequestError:
        raise CommentNotFoundError("Comment not found")


def delete_thread(request, thread_id):
    """
    Delete a thread.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        thread_id: The id for the thread to delete

    Raises:

        PermissionDenied: if user does not have permission to delete thread

    """
    cc_thread, context = _get_thread_and_context(request, thread_id)
    if can_delete(cc_thread, context):
        cc_thread.delete()
        thread_deleted.send(sender=None, user=request.user, post=cc_thread)
    else:
        raise PermissionDenied


def delete_comment(request, comment_id):
    """
    Delete a comment.

    Arguments:

        request: The django request object used for build_absolute_uri and
          determining the requesting user.

        comment_id: The id of the comment to delete

    Raises:

        PermissionDenied: if user does not have permission to delete thread

    """
    cc_comment, context = _get_comment_and_context(request, comment_id)
    if can_delete(cc_comment, context):
        cc_comment.delete()
        comment_deleted.send(sender=None, user=request.user, post=cc_comment)
    else:
        raise PermissionDenied
