from rest_framework import generics

from student.models import CourseEnrollment, User

from .serializers import CourseEnrollmentSerializer, UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = (
        User.objects.all()
        .select_related('profile', 'course_enrollments')
    )
    serializer_class = UserSerializer
    lookup_field = 'username'


class UserCourseEnrollmentsList(generics.ListAPIView):
    queryset = (
        CourseEnrollment.objects.all()
    )
    serializer_class = CourseEnrollmentSerializer
    lookup_field = 'username'

    def get_queryset(self):
        username = self.kwargs['username']
        return self.queryset.filter(user__username=username).order_by('created')