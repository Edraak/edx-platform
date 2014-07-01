from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from rest_framework import generics, permissions
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from student.models import CourseEnrollment, User

from .serializers import CourseEnrollmentSerializer, UserSerializer


class IsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class UserDetail(generics.RetrieveAPIView):
    """Read-only information about our User.

    This will be where users are redirected to after API login and will serve
    as a place to list all useful resources this user can access.
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsUser)
    queryset = (
        User.objects.all()
        .select_related('profile', 'course_enrollments')
    )
    serializer_class = UserSerializer
    lookup_field = 'username'


class UserCourseEnrollmentsList(generics.ListAPIView):
    """Read-only list of courses that this user is enrolled in."""
    authentication_classes = (OAuth2Authentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, IsUser)
    queryset = CourseEnrollment.objects.all()
    serializer_class = CourseEnrollmentSerializer
    lookup_field = 'username'

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs['username'])
        return self.queryset.filter(user=user).order_by('created')

    def get(self, request, *args, **kwargs):
        if request.user.username != kwargs['username']:
            raise PermissionDenied

        return super(UserCourseEnrollmentsList, self).get(self, request, *args, **kwargs)

def my_user_info(request):
    if not request.user:
        raise PermissionDenied
    return redirect("user-detail", username=request.user.username)
