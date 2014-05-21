from rest_framework import generics

from student.models import CourseEnrollment, User

from .serializers import CourseEnrollmentSerializer, UserSerializer

class UserDetail(generics.RetrieveAPIView):
    """Read-only information about our User.

    This will be where users are redirected to after API login and will serve
    as a place to list all useful resources this user can access.

    TODO: Need to add permissions mixin + token auth
    """
    queryset = (
        User.objects.all()
        .select_related('profile', 'course_enrollments')
    )
    serializer_class = UserSerializer
    lookup_field = 'username'


class UserCourseEnrollmentsList(generics.ListAPIView):
    """Read-only list of courses that this user is enrolled in.

    TODO: Need to add permissions mixin + token auth
    """
    queryset = (
        CourseEnrollment.objects.all()
    )
    serializer_class = CourseEnrollmentSerializer
    lookup_field = 'username'

    def get_queryset(self):
        user = User.objects.get(username=self.kwargs['username'])
        return self.queryset.filter(user=user).order_by('created')
