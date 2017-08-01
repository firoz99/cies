from .models import GeneralDiary
from django.db.models import Q


def new_gd_number(request):
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3() or request.user.officer.is_level_4()):
		return {
			'gd_number': 0
		}
	else:
		if request.user.officer.is_level_3():
			gd_number = GeneralDiary.objects.filter(seen_by_sup = 0)
			if request.user.officer.district is not None:
				gd_number = gd_number.filter(district = request.user.officer.district)
			if request.user.officer.thana is not None:
				gd_number = gd_number.filter(thana = request.user.officer.thana) 
		else:
			gd_number = GeneralDiary.objects.filter(seen_by_sub = 0)
			gd_number = gd_number.filter(
							Q(thana = request.user.officer.thana),
							Q(action_officer = request.user)
							)
		return {
			'gd_number': gd_number.count()
		}