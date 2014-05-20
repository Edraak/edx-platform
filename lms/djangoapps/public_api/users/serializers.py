from rest_framework import serializers

from student.models import CourseEnrollment, User


class CourseEnrollmentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CourseEnrollment
        fields = ('course_id', 'created', 'mode', 'is_active')
        lookup_field = 'username'


class UserSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.Field(source='profile.name')
    course_enrollments = serializers.HyperlinkedIdentityField(
        view_name='courseenrollment-detail',
        lookup_field='username'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'course_enrollments')
        lookup_field = 'username'
