from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .forms import *
from .models import *
import numpy as np
import cv2
from .choices import *
import os
from PIL import Image
from .methods import *
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

def criminal_fir_list(request, criminal_id):
	criminal = get_object_or_404(Criminal, pk=criminal_id)
	context = {
		'criminal' : criminal
	}
	return render(request, 'cdms/criminal_fir_list.html', context)

def print_gd(request, gd_id):	
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3() or request.user.officer.is_level_4()):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		gd = get_object_or_404(GeneralDiary, pk=gd_id)
		context = {
			'gd' : gd
		}
		return render(request, 'cdms/print_gd.html', context)

def toggle_case_state(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id) or (request.user.officer.is_level_4() and (is_active_investigation_officer(case.id, request.user.id)))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		case.case_closed = not case.case_closed
		case.save()
		return HttpResponseRedirect(reverse('cdms:charge_sheet', kwargs={'case_id': case.id}))

def change_password(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		if request.method == "POST" and request.POST.get('old_password') and request.POST.get('new_password'):
			if request.user.check_password(request.POST.get('old_password')):
				request.user.set_password(request.POST['new_password']);
				request.user.save()
				context = {
					'error_message': "Password successfully changed!"
				}
				return render(request, 'cdms/change_password.html', context)
			else:
				context = {
					'error_message': "Password doesn't match!"
				}
				return render(request, 'cdms/change_password.html', context)
				
		return render(request, 'cdms/change_password.html')
				
		
def profile(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officer_temp = request.user
		context = {
			'officer_temp' : officer_temp
		}
		return render(request, 'cdms/profile.html', context)

def case_transfer(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id) or (request.user.officer.is_level_4() and (is_active_investigation_officer(case.id, request.user.id)))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		districts = District.objects.all()
		if request.method == "POST" and request.POST.get('thana'):
			district_id = request.POST.get('district')
			thana_id = request.POST.get('thana')
			district = District.objects.get(pk=district_id)
			thana = Thana.objects.get(pk=thana_id)
			case.district = district
			case.thana = thana
			case.save()
			return HttpResponseRedirect(reverse('cdms:case_list'))
		
		context = {
			'districts': districts
		}
		return render(request, 'cdms/case_transfer.html', context)

def case_verdict(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id) or (request.user.officer.is_level_4() and (is_active_investigation_officer(case.id, request.user.id)))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		context = {
			'case': case,
			'BtnValue': 'verdictBtn'
		}
		return render(request, 'cdms/case_verdict.html', context)

def add_case_verdict(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		verdict_files_form_set = VerdictFilesFormSet(request.POST or None, request.FILES or None)
		if all([verdict_files_form_set.is_valid()]):
			for verdict_files_form in verdict_files_form_set:
				verdict_files = verdict_files_form.save(commit=False)
				verdict_files.case = case
				if verdict_files.file:
					verdict_files.save()
			
			return HttpResponseRedirect(reverse('cdms:case_verdict', kwargs={'case_id': case.id}))
		context = {
			"verdict_files_form_set": verdict_files_form_set,
		}
		return render(request, 'cdms/add_case_verdict.html', context)
		
def add_charge_sheet(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		charge_sheet_form_set = ChargeSheetFormSet(request.POST or None)
		if all([charge_sheet_form_set.is_valid()]):
			for charge_sheet_form in charge_sheet_form_set:
				charge_sheet = charge_sheet_form.save(commit=False)
				charge_sheet.accused_by = request.user
				charge_sheet.case = case
				if charge_sheet.name:
					charge_sheet.save()
			
			return HttpResponseRedirect(reverse('cdms:charge_sheet', kwargs={'case_id': case.id}))
		context = {
			"charge_sheet_form_set": charge_sheet_form_set,
		}
		return render(request, 'cdms/add_charge_sheet.html', context)

def charge_sheet(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id) or (request.user.officer.is_level_4() and (is_active_investigation_officer(case.id, request.user.id)))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		context = {
			'case': case,
			'BtnValue': 'chargeSheetBtn'
		}
		return render(request, 'cdms/charge_sheet.html', context)

def case_update_form(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id) or (request.user.officer.is_level_4() and (is_active_investigation_officer(case.id, request.user.id)))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		update_form = CaseUpdateForm(request.POST or None)
		update_files_form_set = CaseUpdateFilesFormSet(request.POST or None, request.FILES or None)
		
		if all([update_form.is_valid(), update_files_form_set.is_valid()]):
			update = update_form.save(commit=False)
			update.update_by = request.user
			update.date_time = timezone.now()
			update.case = case
			update.save()
			
			case_up = Case_Update.objects.get(pk=update.id)
			
			for update_files_form in update_files_form_set:
				update_files = update_files_form.save(commit=False)
				update_files.case_update = case_up
				if update_files.file:
					update_files.save()
		
			return HttpResponseRedirect(reverse('cdms:case_updates', kwargs={'case_id': case.id}))#print_view
		context = {
			"update_form": update_form,
			"update_files_form_set": update_files_form_set,
		}
		return render(request, 'cdms/case_update_form.html', context)

def case_updates(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id) or (request.user.officer.is_level_4() and (is_active_investigation_officer(case.id, request.user.id)))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		context = {
			'case': case,
			'BtnValue': 'caseUpdatesBtn'
		}
		return render(request, 'cdms/case_updates.html', context)

def close_form_case(request, officer_id):
	officer = get_object_or_404(Investigation_Officer, pk=officer_id)
	case = get_object_or_404(Case, pk=officer.case.id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officer.closed = 1
		officer.closing_date_time = timezone.now()
		officer.save()
		return HttpResponseRedirect(reverse('cdms:case_investigation_officers', kwargs={'case_id': case.id}))
		
def assign_investigation_officer(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officers = User.objects.filter(
							Q(officer__thana = case.thana.id ),
							~Q(officer__admin_type = 'OC' )
							)
		
		if request.method == "POST" and request.POST.get('officer'):
			user_id = request.POST.get('officer')
			officer_temp = User.objects.get(pk=user_id)
			if officer_temp is not None:
				case.investigation_officer_set.create(officer = officer_temp, assign_by = request.user)
				return HttpResponseRedirect(reverse('cdms:case_investigation_officers', kwargs={'case_id': case.id}))
		
		context = {
			'officers': officers
		}
		return render(request, 'cdms/assign_investigation_officer.html', context)
		

def case_investigation_officers(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	

		context = {
			
			'case': case,
			'BtnValue': 'investigatinOfficerBtn',
		}
		return render(request, 'cdms/case_investigation_officers.html', context)
		

def case_list(request):
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3() or request.user.officer.is_level_4()):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		cases = Case.objects.all().order_by('-date_time')
		if request.user.officer.is_level_3():
			if request.user.officer.district is not None:
				cases = cases.filter(district = request.user.officer.district)
			if request.user.officer.thana is not None:
				cases = cases.filter(thana = request.user.officer.thana) 
		else:
			cases = cases.filter(
							Q(investigation_officer__officer = request.user),
							Q(investigation_officer__closed = 0)
							)
		context = {
			"cases": cases
		}
		return render(request, 'cdms/case_list.html', context)

def case_details(request, case_id):
	case = get_object_or_404(Case, pk=case_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=case.thana.id, district_id=case.thana.district.id) or (request.user.officer.is_level_4() and (is_active_investigation_officer(case.id, request.user.id)))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		if request.user.officer.is_level_4():
			case.seen_by_sub = 1
		else:
			case.seen_by_sup = 1
		case.save()
		context = {
			'case': case,
			'BtnValue': 'caseDetailsBtn'
		}
		return render(request, 'cdms/case_details.html', context)

def print_fir(request, case_id):	
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3() or request.user.officer.is_level_4()):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		case = get_object_or_404(Case, pk=case_id)
		context = {
			'case' : case
		}
		return render(request, 'cdms/fir.html', context)

def fir_form(request):
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3() or request.user.officer.is_level_4()):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		fir_form = FIRForm(request.POST or None)
		fir_files_form_set = FIRFilesFormSet(request.POST or None, request.FILES or None)
		complainant_form = ComplainantForm(request.POST or None)
		victim_form_set = VictimFormSet(request.POST or None)
		defendant_form_set = DefendantFormFormSet(request.POST or None)
		
		if all([fir_form.is_valid(), fir_files_form_set.is_valid(), complainant_form.is_valid(), victim_form_set.is_valid(), defendant_form_set.is_valid()]):
			fir = fir_form.save(commit=False)
			fir.duty_officer = request.user
			fir.district = request.user.officer.district
			fir.thana = request.user.officer.thana
			fir.save()
			case = Case.objects.get(pk=fir.id)
			
			complainant = complainant_form.save(commit=False)
			complainant.case = case
			complainant.save()
			
			for victim_form in victim_form_set:
				victim = victim_form.save(commit=False)
				victim.case = case
				if victim.vname:
					victim.save()
			
			for defendant_form in defendant_form_set:
				defendant = defendant_form.save(commit=False)
				defendant.case = case
				if defendant.name:
					defendant.save()
					if defendant.criminal_id:
						criminalID = defendant.criminal_id
						criminal = Criminal.objects.get(criminal_id=criminalID)
						if criminal is not None:
							criminal.criminal_fir_list_set.create(fir_number=fir.fir_number, fir_id = fir.id)
			
			for fir_files_form in fir_files_form_set:
				fir_file = fir_files_form.save(commit=False)
				fir_file.case = case
				if fir_file.file:
					fir_file.save()
					
			return HttpResponseRedirect(reverse('cdms:print_fir', kwargs={'case_id': case.id}))#print_view
		context = {
			"fir_form": fir_form,
			"fir_files_form_set": fir_files_form_set,
			"complainant_form":complainant_form,
			"victim_form_set": victim_form_set,
			"defendant_form_set":defendant_form_set,
		}
		return render(request, 'cdms/fir_form.html', context)
	

def gd_action(request, gd_id):
	gd = get_object_or_404(GeneralDiary, pk=gd_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=gd.thana.id, district_id=gd.thana.district.id) or (request.user.officer.is_level_4(thana_id=gd.thana.id) or (request.user.id == gd.action_officer.id))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		if request.method == "POST" and request.POST.get('action'):
			gd.action_details = request.POST.get('action')
			gd.is_action_taken = 1
			gd.save()
			return HttpResponseRedirect(reverse('cdms:gd_details', kwargs={'gd_id': gd.id}))
		if gd.action_details:
			context = {
				'action_details': gd.action_details
			}
			return render(request, 'cdms/gd_action.html', context)
		return render(request, 'cdms/gd_action.html')
		
def remove_action_officer(request, gd_id):
	gd = get_object_or_404(GeneralDiary, pk=gd_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=gd.thana.id, district_id=gd.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		gd.action_officer = None
		gd.assigned_by = None
		gd.save()
		return HttpResponseRedirect(reverse('cdms:gd_details', kwargs={'gd_id': gd.id}))

def assign_action_officer(request, gd_id):
	gd = get_object_or_404(GeneralDiary, pk=gd_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=gd.thana.id, district_id=gd.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officers = User.objects.filter(
							Q(officer__thana = gd.thana.id ),
							~Q(officer__admin_type = 'OC' )
							)
		
		if request.method == "POST" and request.POST.get('officer'):
			user_id = request.POST.get('officer')
			officer_temp = User.objects.get(pk=user_id)
			if officer_temp is not None:
				gd.action_officer = officer_temp
				gd.assigned_by = request.user
				gd.save()
				return HttpResponseRedirect(reverse('cdms:gd_details', kwargs={'gd_id': gd.id}))
		
		context = {
			'officers': officers
		}
		return render(request, 'cdms/assign_action_officer.html', context)

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('cdms:login'))

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('cdms:dashboard'))
            else:
                return render(request, 'cdms/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'cdms/login.html', {'error_message': 'Invalid login'})
    return render(request, 'cdms/login.html')

def appoint_oc(request, thana_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officers = User.objects.filter(
								Q(officer__officer_type = 'R'),
								Q(officer__rank = 'I')
								)
		thana = get_object_or_404(Thana, pk=thana_id)
		district = get_object_or_404(District, pk=thana.district.id)
		
		if request.method == "POST" and request.POST.get('officer'):
			user_id = request.POST.get('officer')
			oc = get_object_or_404(User, pk=user_id)
			if oc is not None and thana is not None:
				oc.officer.admin_type = 'OC'
				oc.officer.officer_type = 'C'
				oc.officer.position = "Officer-in-charge"
				oc.officer.thana = thana
				oc.officer.district = district
				oc.officer.save()
				return HttpResponseRedirect(reverse('cdms:thana_details', kwargs={'thana_id': thana.id}))
		
		context = {
			'officers': officers
		}
		return render(request, 'cdms/appoint_oc.html', context)

def remove_officer(request, user_id, thana_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officer_temp = get_object_or_404(User, pk=user_id)
		if officer_temp is not None:
			officer_temp.officer.admin_type = ''
			officer_temp.officer.officer_type = 'R'
			officer_temp.officer.thana = None
			officer_temp.officer.district = None
			officer_temp.officer.position = ""
			officer_temp.officer.save()
		return HttpResponseRedirect(reverse('cdms:thana_details', kwargs={'thana_id': thana_id}))

def appoint_officer(request, thana_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officers = User.objects.filter(
								Q(officer__officer_type = 'R'),
								Q(officer__rank = 'I')|
								Q(officer__rank = 'SI')|
								Q(officer__rank = 'ASI')
								
								)
		thana = get_object_or_404(Thana, pk=thana_id)
		district = get_object_or_404(District, pk=thana.district.id)
		
		if request.method == "POST" and request.POST.get('officer'):
			user_id = request.POST.get('officer')
			officer_temp = get_object_or_404(User, pk=user_id)
			if officer_temp is not None and thana is not None:
				officer_temp.officer.officer_type = 'C'
				officer_temp.officer.thana = thana
				officer_temp.officer.district = district
				officer_temp.officer.save()
				return HttpResponseRedirect(reverse('cdms:thana_details', kwargs={'thana_id': thana.id}))
		
		context = {
			'officers': officers
		}
		return render(request, 'cdms/appoint_officer.html', context)
		

def thana_details(request, thana_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		thana = get_object_or_404(Thana, pk=thana_id)
		ocs = User.objects.filter(
							Q(officer__thana = thana.id ),
							Q(officer__admin_type = 'OC' )
							)
		officers = User.objects.filter(
							Q(officer__thana = thana.id ),
							~Q(officer__admin_type = 'OC' )
							)
		context = {
			'thana' : thana,
			'ocs': ocs,
			'officers': officers
		}
		return render(request, 'cdms/thana_details.html', context)

def update_officer(request, user_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officer_temp = get_object_or_404(User, pk=user_id)
		officer = get_object_or_404(Officer, pk=officer_temp.officer.id)
		user_form = UpdateUserForm(request.POST or None, instance = officer_temp)
		officer_form = OfficerForm(request.POST or None, request.FILES or None, instance = officer)
		update_user_password_form = UpdateUserPasswordForm(request.POST or None, instance = officer_temp)
		
		if user_form.is_valid() and officer_form.is_valid():
			officer_temp = user_form.save(commit=False)
			officer_temp.save()
			userID = officer_temp.id
			officer = officer_form.save(commit=False)
			officer.user = User.objects.get(pk=userID)
			officer.save()
			return HttpResponseRedirect(reverse('cdms:officer_details', kwargs={'user_id': officer_temp.id}))
		elif update_user_password_form.is_valid():
			officer_temp = update_user_password_form.save(commit=False)
			password = update_user_password_form.cleaned_data['password']
			officer_temp.set_password(password)
			officer_temp.save()
			return HttpResponseRedirect(reverse('cdms:officer_details', kwargs={'user_id': officer_temp.id}))
			
		context = {
			"user_form": user_form,
			"officer_form": officer_form,
			"update_user_password_form": update_user_password_form,
			"officer": officer
		}
		return render(request, 'cdms/update_officer.html', context)


def officer_details(request, user_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officer_temp = get_object_or_404(User, pk=user_id)
		context = {
			'officer_temp' : officer_temp
		}
		return render(request, 'cdms/officer_details.html', context)

def add_officer(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		user_form = UserForm(request.POST or None)
		officer_form = OfficerForm(request.POST or None, request.FILES or None)
		
		if user_form.is_valid() and officer_form.is_valid():
			officer_temp = user_form.save(commit=False)
			password = user_form.cleaned_data['password']
			officer_temp.set_password(password)
			officer_temp.save()
			userID = officer_temp.id
			officer = officer_form.save(commit=False)
			officer.user = User.objects.get(pk=userID)
			officer.save()
			
			return HttpResponseRedirect(reverse('cdms:officer_list'))
		context = {
			"user_form": user_form,
			"officer_form": officer_form,
		}
		return render(request, 'cdms/add_officer.html', context)

				
def officer_list(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officers = User.objects.filter(
							Q(officer__officer_type = 'C' )
							)

		context = {
			"officers": officers,
			"BtnValue": "thanaBtn"
		}
		return render(request, 'cdms/officer_list.html', context)
	
def officer_list_admin(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officers = User.objects.filter(
							Q(officer__officer_type = 'A' ),
							Q(officer__admin_type = None )
							)

		context = {
			"officers": officers,
			"BtnValue": "adminBtn"
		}
		return render(request, 'cdms/officer_list.html', context)
	
def officer_list_reserve(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officers = User.objects.filter(
							Q(officer__officer_type = 'R' )
							)

		context = {
			"officers": officers,
			"BtnValue": "reserveBtn"
		}
		return render(request, 'cdms/officer_list.html', context)

def toggle_admin_state(request, user_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_1():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officer_temp = get_object_or_404(User, pk=user_id)
		if officer_temp.officer.admin_type == 'A':
			officer_temp.officer.admin_type = None
			officer_temp.officer.save()
			return HttpResponseRedirect(reverse('cdms:officer_details', kwargs={'user_id': officer_temp.id}))	
		else:
			officer_temp.officer.admin_type = 'A'
			officer_temp.officer.thana = None
			officer_temp.officer.save()
			return HttpResponseRedirect(reverse('cdms:admin_details', kwargs={'user_id': officer_temp.id}))
	
def toggle_user_state(request, user_id, type):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:	
		officer_temp = get_object_or_404(User, pk=user_id)
		officer_temp.is_active = not officer_temp.is_active
		officer_temp.save()
		if type == "admin":
			return HttpResponseRedirect(reverse('cdms:admin_details', kwargs={'user_id': officer_temp.id}))
		else:
			return HttpResponseRedirect(reverse('cdms:officer_details', kwargs={'user_id': officer_temp.id}))
		
def update_admin(request, user_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_1():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		officer_temp = get_object_or_404(User, pk=user_id)
		super_admin = officer_temp.officer.admin_type
		officer = get_object_or_404(Officer, pk=officer_temp.officer.id)
		user_form = UpdateUserForm(request.POST or None, instance = officer_temp)
		admin_form = AdminForm(request.POST or None, request.FILES or None, instance = officer)
		update_user_password_form = UpdateUserPasswordForm(request.POST or None, instance = officer_temp)
		
		if user_form.is_valid() and admin_form.is_valid():
			officer_temp = user_form.save(commit=False)
			officer_temp.save()
			userID = officer_temp.id
			officer = admin_form.save(commit=False)
			if request.POST.get('is_super_admin') == 'S':
				officer.admin_type = 'S'
			else:
				officer.admin_type = 'A'
			officer.user = User.objects.get(pk=userID)
			officer.save()
			return HttpResponseRedirect(reverse('cdms:admin_details', kwargs={'user_id': officer_temp.id}))
		elif update_user_password_form.is_valid():
			officer_temp = update_user_password_form.save(commit=False)
			password = update_user_password_form.cleaned_data['password']
			officer_temp.set_password(password)
			officer_temp.save()
			return HttpResponseRedirect(reverse('cdms:admin_details', kwargs={'user_id': officer_temp.id}))
			
		context = {
			"user_form": user_form,
			"admin_form": admin_form,
			"update_user_password_form": update_user_password_form,
			"super_admin": super_admin
		}
		return render(request, 'cdms/update_admin.html', context)
	
def admin_details(request, user_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_1():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		officer_temp = get_object_or_404(User, pk=user_id)
		context = {
			'officer_temp' : officer_temp
		}
		return render(request, 'cdms/admin_details.html', context)

def add_admin(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_1():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		user_form = UserForm(request.POST or None)
		admin_form = AdminForm(request.POST or None, request.FILES or None)
		
		if user_form.is_valid() and admin_form.is_valid():
			officer_temp = user_form.save(commit=False)
			password = user_form.cleaned_data['password']
			officer_temp.set_password(password)
			officer_temp.save()
			userID = officer_temp.id
			officer = admin_form.save(commit=False)
			if request.POST.get('is_super_admin') == 'S':
				officer.admin_type = 'S'
			else:
				officer.admin_type = 'A'
			officer.user = User.objects.get(pk=userID)
			officer.save()
			
			return HttpResponseRedirect(reverse('cdms:admin_list'))
		context = {
			"user_form": user_form,
			"admin_form": admin_form,
		}
		return render(request, 'cdms/add_admin.html', context)

def admin_list(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_1():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		super_admins = User.objects.filter(officer__admin_type = 'S')
		admins = User.objects.filter(officer__admin_type = 'A')
		context = {
			"super_admins": super_admins,
			"admins": admins,
		}
		return render(request, 'cdms/admin_list.html', context)

def search_criminal(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		districts = District.objects.all()
		criminals = Criminal.objects.all()
		
		form = TempImagesForm(request.POST or None, request.FILES or None)
		ids = []
		if form.is_valid():
			tempImg = form.save(commit=False)
			tempImg.image = request.FILES['image']
			tempImg.save()
			orginalName = tempImg.image.name.split('/')[-1]
			mugPath = "media/temps/" + orginalName
			ids = detect_n_predict(mugPath)
			
		cid_q = request.GET.get('criminal_id')
		dist_q = request.GET.get('district')
		thana_q = request.GET.get('thana')
		cs_q = request.GET.get('criminal_status')
		name_q = request.GET.get('nameOrAlias')
		
		if ids or cid_q or dist_q or thana_q or cs_q or name_q:
			if ids:
				criminals = criminals.filter(id__in = ids)
			elif cid_q:
				criminals = criminals.filter(criminal_id__icontains = cid_q)
			else:
				if dist_q:
					criminals = criminals.filter(district_id = dist_q)
				if thana_q:
					criminals = criminals.filter(thana_id = thana_q)
				if cs_q:
					criminals = criminals.filter(criminal_status = cs_q)
				if name_q:
					criminals = criminals.filter(
						Q(name__icontains = name_q)|
						Q(aliases__icontains = name_q)
					).distinct()
			context = {
				'districts' : districts,
				'cs' : dict(CRIMINAL_STATUS),
				'criminals' : criminals
			}
			return render(request, 'cdms/search.html', context)
		else:
			context = {
				'districts' : districts,
				'cs' : dict(CRIMINAL_STATUS)
			}
			return render(request, 'cdms/search.html', context)

def search_thana(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		districts = District.objects.all()
		thanas = Thana.objects.all()
		thana = Thana.objects.none()
		
		dist_q = request.GET.get('district')
		thana_q = request.GET.get('thana')
		
		if dist_q and thana_q:
			thana = get_object_or_404(Thana, pk=thana_q)
			
			context={
				"districts": districts,
				"thanas": thanas,
				"thana": thana
			}
			return render(request, 'cdms/search_thana.html', context)
		else:
			context = {
				'districts' : districts,
				"thanas": thanas,
			}
			return render(request, 'cdms/search_thana.html', context)

def get_thanas(request, district_id):
    district = District.objects.get(pk=district_id)
    thanas = Thana.objects.filter(district=district)
    thana_dict = {}
    for thana in thanas:
        thana_dict[thana.id] = thana.name
		
    return JsonResponse(thana_dict)
	

def add_criminal(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_3():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		form = CriminalForm(request.POST or None)
		if form.is_valid():
			criminal = form.save(commit=False)
			criminal.save()
			return HttpResponseRedirect(reverse('cdms:add_images', kwargs={'criminal_id': criminal.id}))
		context = {
			"form": form,
		}
		return render(request, 'cdms/add_criminal.html', context)

def criminal_details(request, criminal_id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		criminal = get_object_or_404(Criminal, pk=criminal_id)
		context = {
			'criminal' : criminal
		}
		return render(request, 'cdms/criminal_details.html', context)
	
def update_criminal(request, criminal_id):
	criminal = get_object_or_404(Criminal, pk=criminal_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=criminal.thana.id, district_id=criminal.thana.district.id):
		context = {
			'criminal' : criminal,
			'danger_message': "Unauthorized access !"
		}
		return render(request, 'cdms/criminal_details.html', context)
	else:
		
		form = CriminalForm(request.POST or None, instance = criminal)
		if form.is_valid():
			criminal = form.save(commit=False)
			criminal.save()
			return HttpResponseRedirect(reverse('cdms:criminal_details', kwargs={'criminal_id': criminal.id}))
		context = {
			"form": form,
			"criminal": criminal
		}
		return render(request, 'cdms/update_criminal.html', context)

def add_district(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		form = DistrictForm(request.POST or None)
		if form.is_valid():
			district = form.save(commit=False)
			district.save()
			return HttpResponseRedirect(reverse('cdms:district_list'))
		context = {
			"form": form,
		}
		return render(request, 'cdms/add_district.html', context)
	
def gd_form(request):
	form = GDForm(request.POST or None)
	filesFormSet = GDFilesFormSet(request.POST or None, request.FILES or None)
	if all([form.is_valid(), filesFormSet.is_valid()]):
		gd = form.save(commit=False)
		gd.date_time = timezone.now()
		gd.save()
		gd_id = gd.id

		for fileForm in filesFormSet:
			gd_file = fileForm.save(commit=False)
			gd_file.gd= GeneralDiary.objects.get(pk=gd_id)
			if gd_file.file:
				gd_file.save()
		return HttpResponseRedirect(reverse('cdms:index'))
	context = {
		"form": form,
		"filesFormSet": filesFormSet
	}
	return render(request, 'cdms/gd_form.html', context)

def gd_list(request):
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3() or request.user.officer.is_level_4()):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		gds = GeneralDiary.objects.all().order_by('-date_time')
		if request.user.officer.is_level_3():
			if request.user.officer.district is not None:
				gds = gds.filter(district = request.user.officer.district)
			if request.user.officer.thana is not None:
				gds = gds.filter(thana = request.user.officer.thana) 
		else:
			gds = gds.filter(
							Q(thana = request.user.officer.thana),
							Q(action_officer = request.user)
							)
		context = {
			"gds": gds
		}
		return render(request, 'cdms/gd_list.html', context)
	
def gd_details(request, gd_id):
	gd = get_object_or_404(GeneralDiary, pk=gd_id)
	if not request.user.is_authenticated() or not (request.user.officer.is_level_3(thana_id=gd.thana.id, district_id=gd.thana.district.id) or (request.user.officer.is_level_4(thana_id=gd.thana.id) or (request.user.id == gd.action_officer.id))):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		if request.user.officer.is_level_4():
			gd.seen_by_sub = 1
		else:
			gd.seen_by_sup = 1
		gd.save()
		context = {
			'gd': gd
		}
		return render(request, 'cdms/gd_details.html', context)
	
	
def district_list(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		districts = District.objects.all()
		context = {
			"districts": districts
		}
		return render(request, 'cdms/districts.html', context)

def update_district(request, district_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		district = get_object_or_404(District, pk=district_id)
		form = DistrictForm(request.POST or None, instance=district)
		if form.is_valid():
			district = form.save(commit=False)
			district.save()
			return HttpResponseRedirect(reverse('cdms:district_list'))
		context = {
			"form": form,
			"district": district
		}
		return render(request, 'cdms/update_district.html', context)

def add_thana(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		form = ThanaForm(request.POST or None)
		if form.is_valid():
			thana = form.save(commit=False)
			thana.save()
			return HttpResponseRedirect(reverse('cdms:thana_list'))
		context = {
			"form": form,
		}
		return render(request, 'cdms/add_thana.html', context)
	
def thana_list(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		districts = District.objects.all()
		thanas = Thana.objects.all().order_by('district')
		q = request.GET.get('q')
		if q:
			thanas = thanas.filter(district = q)
		context = {
			"districts": districts,
			"thanas": thanas
		}
		return render(request, 'cdms/thana_list.html', context)

def update_thana(request, thana_id):
	if not request.user.is_authenticated() or not request.user.officer.is_level_2():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		thana = get_object_or_404(Thana, pk=thana_id)
		form = ThanaForm(request.POST or None, instance=thana)
		if form.is_valid():
			thana = form.save(commit=False)
			thana.save()
			return HttpResponseRedirect(reverse('cdms:thana_details', kwargs={'thana_id': thana.id}))
		context = {
			"form": form,
			"thana": thana
		}
		return render(request, 'cdms/update_thana.html', context)
	
def add_images(request, criminal_id):
	criminal = get_object_or_404(Criminal, pk=criminal_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=criminal.thana.id, district_id=criminal.thana.district.id):
		context = {
			'criminal' : criminal,
			'danger_message': "Unauthorized access !"
		}
		return render(request, 'cdms/criminal_details.html', context)
	else:
		form = CriminalImagesForm(request.POST or None, request.FILES or None)
		
		
		if form.is_valid():
			files = request.FILES.getlist('image')
			for file in files:
				img = form.save(commit=False)
				img.image = file
				img.criminal = criminal
				img.save()
				
				orginalName = img.image.name.split('/')[-1]
				mugPath = "media/raw/" + orginalName
				mugShot = cv2.imread(mugPath)
				gray = cv2.cvtColor(mugShot, cv2.COLOR_BGR2GRAY)
				detector = cv2.CascadeClassifier("media/xmls/haarcascade_frontalface_default.xml")
				rects = detector.detectMultiScale(gray, 1.3, 5)
				mugShotFinal = "media/faces/" + orginalName
				x,y,w,h = 0,0,0,0
				for (x, y, w, h) in rects:
					pass
				if x and y and w and h:
					imgRe = gray[y:y + h, x:x + w]
					imgRe = cv2.resize(imgRe, (128, 128))
					cv2.imwrite(mugShotFinal, imgRe)
					img.face = 'faces/'+orginalName
					img.save()
				img.id +=1
			context = {
				'criminal': criminal,
				'form': form,
			}
			return render(request, 'cdms/add_images.html', context) 
		context = {
			'criminal': criminal,
			'form': form,
		}	
		return render(request, 'cdms/add_images.html', context)
	
	
def delete_image(request, criminal_id, criminal_images_id):
	criminal = get_object_or_404(Criminal, pk=criminal_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=criminal.thana.id, district_id=criminal.thana.district.id):
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		criminal = get_object_or_404(Criminal, pk=criminal_id)
		criminal_image = Criminal_images.objects.get(pk=criminal_images_id)
		criminal_image.delete()
		return HttpResponseRedirect(reverse('cdms:add_images', kwargs={'criminal_id': criminal.id}))

def delete_criminal(request, criminal_id):
	criminal = get_object_or_404(Criminal, pk=criminal_id)
	if not request.user.is_authenticated() or not request.user.officer.is_level_3(thana_id=criminal.thana.id, district_id=criminal.thana.district.id):
		context = {
			'criminal' : criminal,
			'danger_message': "Unauthorized access !"
		}
		return render(request, 'cdms/criminal_details.html', context)
	else:
		criminal.delete()
		return HttpResponseRedirect(reverse('cdms:search_criminal'))
	
def train(request):
	if not request.user.is_authenticated() or not request.user.officer.is_level_3():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		recognizer = cv2.createLBPHFaceRecognizer()
		path = "media/faces"

		def getImageAndID(path):
			imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
			faces = []
			IDs = []
			for imagePath in imagePaths:
				faceImg = Image.open(imagePath).convert('L')
				faceNp = np.array(faceImg, 'uint8')
				ID = int(os.path.split(imagePath)[-1].split('.')[0])
				faces.append(faceNp)
				IDs.append(ID)
			return IDs, faces

		Ids, faces = getImageAndID(path)
		recognizer.train(faces, np.array(Ids))
		recognizer.save('media/xmls/trainingData.yml')
		return HttpResponseRedirect(reverse('cdms:dashboard'))

def most_wanted(request):
	criminals = Criminal.objects.filter(criminal_status = 'MW')
	context = {
		'criminals' : criminals
	}
	return render(request, 'cdms/most_wanted.html', context)

def wanted(request):
	criminals = Criminal.objects.filter(criminal_status = 'W')
	context = {
		'criminals' : criminals
	}
	return render(request, 'cdms/wanted.html', context)
	
def index(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('cdms:logout'))
	else:
		return render(request, 'cdms/index.html')

def dashboard(request):
	
	
	return render(request, 'cdms/dashboard.html')

def criminal_details2(request, criminal_id):
	criminal = get_object_or_404(Criminal, pk=criminal_id)
	context = {
		'criminal' : criminal
	}
	return render(request, 'cdms/criminal_details2.html', context)
	
	
	
#utility functions

def is_active_investigation_officer(case_id, user_id):
	case = Case.objects.get(pk=case_id)
	officers = case.investigation_officer_set.all()
	for officer in officers:
		if (officer.officer.id == user_id and officer.closed == 0):
			return True
	return False
	