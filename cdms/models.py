from __future__ import unicode_literals
from uuid import uuid4
import os
from django.db import models
from .choices import *
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.deconstruct import deconstructible
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path, model_name):
		self.path = sub_path
		self.model_name = model_name
		
    def __call__(self, instance, filename):
		ext = filename.split('.')[-1]
		complaint_id = "%s" %  (getattr(instance, self.model_name).pk)
		random_id = "%s" % (uuid4().hex,)
		filename = '{}.{}.{}'.format(complaint_id, random_id, ext)
		return os.path.join(self.path, filename)

path_and_rename = PathAndRename("raw", "criminal")

path_and_rename_for_pro_pics = PathAndRename("pro_pics", "user")

@deconstructible
class PathAndRenameForGD(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
		ext = filename.split('.')[-1]
		lastIndexOfDot = filename.rindex('.')
		orgName = filename[:lastIndexOfDot]
		gd_id = "%s" % (instance.gd.pk,)
		random_id = "%s" % (uuid4().hex,)
		filename = '{}.{}.{}.{}'.format(gd_id, orgName, random_id, ext)
		return os.path.join(self.path, filename)

path_and_rename_for_gd = PathAndRenameForGD("gd_files")

@deconstructible
class PathAndRenameForCase(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
		ext = filename.split('.')[-1]
		lastIndexOfDot = filename.rindex('.')
		orgName = filename[:lastIndexOfDot]
		gd_id = "%s" % (instance.case.pk,)
		random_id = "%s" % (uuid4().hex,)
		filename = '{}.{}.{}.{}'.format(gd_id, orgName, random_id, ext)
		return os.path.join(self.path, filename)

path_and_rename_for_case = PathAndRenameForCase("case_files")

@deconstructible
class PathAndRenameForCaseUpdate(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
		ext = filename.split('.')[-1]
		lastIndexOfDot = filename.rindex('.')
		orgName = filename[:lastIndexOfDot]
		gd_id = "%s" % (instance.case_update.pk,)
		random_id = "%s" % (uuid4().hex,)
		filename = '{}.{}.{}.{}'.format(gd_id, orgName, random_id, ext)
		return os.path.join(self.path, filename)

path_and_rename_for_case_update = PathAndRenameForCaseUpdate("case_files")



class District(models.Model):
	name = models.CharField(max_length = 100)
	
	def __str__(self):
		return self.name
	
class Thana(models.Model):
	district = models.ForeignKey(District)
	name = models.CharField(max_length = 250)
	mobile = models.CharField(max_length = 50, null = True, blank = True)
	email = models.CharField(max_length = 200, null = True, blank = True)
	address = models.TextField(null = True, blank = True)
	
	def __str__(self):
		return self.name

class Criminal(models.Model):
	criminal_id = models.CharField(max_length = 100)
	criminal_status = models.CharField(max_length = 10, choices=CRIMINAL_STATUS, blank = True)
	district = models.ForeignKey(District)
	thana = models.ForeignKey(Thana)
	name = models.CharField(max_length = 250)
	aliases = models.CharField(max_length = 1000, blank = True)
	dob = models.DateField("Date of Birth", null = True, blank = True)
	birth_place = models.CharField(max_length = 100, null = True, blank = True)
	father_name = models.CharField(max_length = 200, null = True, blank = True)
	mother_name = models.CharField(max_length = 200, null = True, blank = True)
	present_address = models.CharField(max_length = 300, null = True, blank = True)
	permanent_address = models.CharField(max_length = 300, null = True, blank = True)
	hair = models.CharField(max_length = 100, blank = True)
	eyes = models.CharField(max_length = 100, blank = True)
	height = models.CharField(max_length = 50, blank = True)
	weight = models.CharField(max_length = 50, blank = True)
	gender = models.CharField(max_length = 10, choices=GENDER, blank = True)
	race = models.CharField(max_length = 50, blank = True)
	scars_and_marks = models.CharField(max_length = 300, blank = True)
	nationality = models.CharField(max_length = 50, blank = True)
	crime_titles = models.CharField(max_length = 1000, blank = True)
	description = models.TextField(blank = True)
	rewards = models.CharField(max_length = 1000, blank = True)
	remarks = models.TextField(blank = True)
	cautions = models.CharField(max_length = 500, blank = True)
	
	def __str__(self):
		return self.criminal_id + ' - ' + self.name
		
class Criminal_images(models.Model):
	criminal = models.ForeignKey(Criminal, on_delete = models.CASCADE)
	image = models.ImageField(upload_to=path_and_rename)
	face = models.ImageField(upload_to='faces', null = True, blank = True)
	
class TempImages(models.Model):
	image = models.ImageField(upload_to='temps')

class Criminal_fir_list(models.Model):
	criminal = models.ForeignKey(Criminal, on_delete = models.CASCADE)
	fir_number = models.CharField(max_length = 100)
	fir_id = models.CharField(max_length = 100, null = True)

class GeneralDiary(models.Model):
	district = models.ForeignKey(District)
	thana = models.ForeignKey(Thana)
	name = models.CharField(max_length = 100)
	father_name = models.CharField("Father's Name",max_length = 100, blank = True)
	mother_name = models.CharField("Mother's Name", max_length = 100, blank = True)
	present_address = models.CharField(max_length = 300, blank = True)
	permanent_address = models.CharField(max_length = 300, blank = True)
	national_id = models.CharField(max_length = 100, blank = True)
	mobile = models.CharField(max_length = 50, blank = True)
	email = models.CharField(max_length = 150, blank = True)
	description = models.TextField()
	date_time = models.DateTimeField()
	seen_by_sup = models.BooleanField(default=False)
	seen_by_sub = models.BooleanField(default=False)
	assigned_by = models.ForeignKey(User, related_name='+', blank = True, null = True)
	action_officer = models.ForeignKey(User, related_name='+', blank = True, null = True)
	action_details = models.TextField(blank = True)
	is_action_taken = models.BooleanField(default=False)
	
class GD_files(models.Model):
	gd = models.ForeignKey(GeneralDiary, on_delete = models.CASCADE)
	file = models.FileField(upload_to=path_and_rename_for_gd)


	
class Officer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	rank = models.CharField(max_length = 10, choices=RANK)
	position = models.CharField(max_length = 100, null = True, blank = True)
	officer_id = models.CharField(max_length = 50, blank = True)
	area = models.CharField(max_length = 300, null = True, blank = True)
	district = models.ForeignKey(District, null=True, blank = True)
	thana = models.ForeignKey(Thana, null=True, blank = True)
	admin_type = models.CharField(max_length = 10, choices=ADMIN_TYPE, null=True, blank = True)
	officer_type = models.CharField(max_length = 10, choices=OFFICER_TYPE, default='R')
	mobile = models.CharField("Mobile numbers", max_length = 50, blank = True)
	pro_pic = models.ImageField("Profile picture", upload_to=path_and_rename_for_pro_pics, null = True, blank = True)

	def __str__(self):
		return self.user.get_full_name()
		
	def is_level_1(self):
		if self.admin_type == 'S':
			return True
		else:
			return False
	
	def is_level_2(self):
		if self.admin_type == 'S' or self.admin_type == 'A':
			return True
		else:
			return False
			
	def is_level_3(self, thana_id=None, district_id=None):
		if self.admin_type == 'OC' or (self.officer_type == 'C' and not (self.rank == 'I' or self.rank == 'SI' or self.rank == 'ASI' )):
			if thana_id is not None and self.thana is not None:
				if self.thana.id == thana_id:
					return True
				else:
					return False
			if district_id is not None and self.district is not None:
				if self.district.id == district_id:
					return True
				else:
					return False
			return True
		else:
			return False
			
	def is_level_4(self, thana_id=None):
		if self.officer_type == 'C' and not self.admin_type == 'OC' and (self.rank == 'I' or self.rank == 'SI' or self.rank == 'ASI' ):
			if thana_id is not None and self.thana is not None:
				if self.thana.id == thana_id:
					return True
				else:
					return False
			return True
		else:
			return False
	
@receiver(post_delete, sender=Criminal_images)
def photo_post_delete_handler(sender, **kwargs):
	photo = kwargs['instance']
	storage, path = photo.image.storage, photo.image.path
	storage.delete(path)
	if photo.face:
		storage, path = photo.face.storage, photo.face.path
		storage.delete(path)


class Case(models.Model):
	district = models.ForeignKey(District)
	thana = models.ForeignKey(Thana)
	fir_number = models.CharField("FIR number", max_length = 100)
	section = models.CharField("Section of a rule", max_length = 300)
	date_time = models.DateTimeField(auto_now_add=True)
	duty_officer = models.ForeignKey(User)
	location = models.CharField("Location and Distance", max_length = 300, null=True)
	description = models.TextField()
	reason = models.CharField("Why late to file a FIR", max_length = 300, null=True,blank=True)
	seen_by_sup = models.BooleanField(default=False)
	seen_by_sub = models.BooleanField(default=False)
	case_closed = models.BooleanField(default=False)

class Case_FIR_Files(models.Model):
	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	file = models.FileField(upload_to=path_and_rename_for_case)
		
class Complainant(models.Model):
	case = models.OneToOneField(Case, on_delete = models.CASCADE)
	name = models.CharField(max_length = 100)
	father_name = models.CharField("Father's Name",max_length = 100, blank = True)
	mother_name = models.CharField("Mother's Name", max_length = 100, blank = True)
	present_address = models.CharField(max_length = 300, blank = True)
	permanent_address = models.CharField(max_length = 300, blank = True)
	national_id = models.CharField(max_length = 100, blank = True)
	mobile = models.CharField("Mobile Numbers", max_length = 50, blank = True)
	
class Victim(models.Model):
	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	vname = models.CharField("Name",max_length = 100) #v: conflict with defendent name in formset
	vfather_name = models.CharField("Father's Name",max_length = 100, blank = True)
	vmother_name = models.CharField("Mother's Name", max_length = 100, blank = True)
	vpresent_address = models.CharField("Present Address", max_length = 300, blank = True)
	vpermanent_address = models.CharField("Permanent Address", max_length = 300, blank = True)
	vnational_id = models.CharField("National ID",max_length = 100, blank = True)
	vmobile = models.CharField("Mobile Numbers", max_length = 50, blank = True)
	
class Defendant(models.Model):
	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	name = models.CharField(max_length = 100)
	father_name = models.CharField("Father's Name",max_length = 100, blank = True)
	mother_name = models.CharField("Mother's Name", max_length = 100, blank = True)
	present_address = models.CharField(max_length = 300, blank = True)
	permanent_address = models.CharField(max_length = 300, blank = True)
	criminal_id = models.CharField(max_length = 100, blank = True)
	mobile = models.CharField("Mobile Numbers", max_length = 50, blank = True)
		
class Investigation_Officer(models.Model):
	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	officer = models.ForeignKey(User, related_name='+')
	assign_by = models.ForeignKey(User, related_name='+')
	date_time = models.DateTimeField(auto_now_add=True)
	closed = models.BooleanField(default=False)
	closing_date_time = models.DateTimeField(null=True, blank=True)
	
class Case_Update(models.Model):
	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	title = models.CharField(max_length = 300)
	date_time = models.DateTimeField(auto_now_add=True)
	update_by = models.ForeignKey(User)
	description = models.TextField()
	
class Case_Update_Files(models.Model):
	case_update = models.ForeignKey(Case_Update, on_delete = models.CASCADE)
	file = models.FileField(upload_to=path_and_rename_for_case_update)

	
class Charge_sheet(models.Model):
	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	name = models.CharField("Name of accused", max_length = 100)
	aliases = models.CharField("Aliases of accused", max_length = 1000, blank = True)
	father_name = models.CharField("Father's Name",max_length = 100, blank = True)
	mother_name = models.CharField("Mother's Name", max_length = 100, blank = True)
	present_address = models.CharField(max_length = 300, blank = True)
	permanent_address = models.CharField(max_length = 300, blank = True)
	accused_by = models.ForeignKey(User)
	charges = models.TextField("Charges and Specifications", null=True)
	
	
class Verdict_Files(models.Model):
	case = models.ForeignKey(Case, on_delete = models.CASCADE)
	file = models.FileField(upload_to=path_and_rename_for_case)
	
