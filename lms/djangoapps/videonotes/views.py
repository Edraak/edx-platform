# Create your views here.

from videonotes.models import VideoNote
from util.json_request import JsonResponse


def add_note(request):
	note_text = request.POST.get('note_text')
	timestamp = request.POST.get('timestamp')
	user = request.user
	import ipdb; ipdb.set_trace()
	course_id = request.POST.get('course_id')

	VideoNote.objects.create(
		user=user, timestamp=timestamp, course_id=course_id, note_text=note_text
	)

	return JsonResponse({"success": "success"}, status=200)
	