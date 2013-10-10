# Create your views here.

from videonotes.models import VideoNote

def add_note(request):
	timestamp = request.POST.get('timestamp')
	user = request.POST.get('user')
	course_id = request.POST.get('course_id')

	VideoNote.objects.create(
		user=user, timestamp=timestamp, course_id=course_id
	)

	