from django import forms
from django.contrib.auth.models import User
from django.forms import formset_factory
from .models import *
from django.contrib.auth.models import User


def set_field_html_name(cls, new_name):

    old_render = cls.widget.render
    def _widget_render_wrapper(name, value, attrs=None):
        return old_render(new_name, value, attrs)

    cls.widget.render = _widget_render_wrapper

class CriminalForm(forms.ModelForm):
	thana = forms.ModelChoiceField(queryset=Thana.objects.all())
	class Meta:
		model = Criminal
		fields = ['criminal_id', 'criminal_status', 'district', 'thana', 'name', 'aliases', 'hair', 'eyes', 'height', 'weight', 'gender', 'race', 'scars_and_marks', 'nationality', 'crime_titles', 'description', 'rewards', 'remarks', 'cautions', 'dob', 'birth_place', 'father_name', 'mother_name', 'present_address', 'permanent_address']

class CriminalImagesForm(forms.ModelForm):

    class Meta:
        model = Criminal_images
        fields = ['image']		

class TempImagesForm(forms.ModelForm):

    class Meta:
        model = TempImages
        fields = ['image']		
		
		
class DistrictForm(forms.ModelForm):

    class Meta:
        model = District
        fields = ['name']	
		
class ThanaForm(forms.ModelForm):

    class Meta:
        model = Thana
        fields = ['district','name','mobile','email','address']	

class GDForm(forms.ModelForm):
	
	class Meta:
		model = GeneralDiary
		fields = ['district', 'thana', 'name', 'father_name', 'mother_name', 'present_address', 'permanent_address', 'national_id', 'mobile', 'email', 'description']

class GDFilesForm(forms.ModelForm):

    class Meta:
        model = GD_files
        fields = ['file']	
		
GDFilesFormSet = formset_factory(GDFilesForm, extra=3)


class UserForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'username', 'password']
		widgets = {
            'password': forms.PasswordInput(),
        }

class UpdateUserForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'username']

class UpdateUserPasswordForm(forms.ModelForm):
	
	class Meta:
		model = User
		fields = ['password']
		widgets = {
            'password': forms.PasswordInput(),
        }
		
class AdminForm(forms.ModelForm):
	class Meta:
		model = Officer
		fields = ['rank', 'position', 'officer_type', 'officer_id', 'area', 'mobile', 'pro_pic']
		
class OfficerForm(forms.ModelForm):
	class Meta:
		model = Officer
		fields = ['thana', 'district', 'rank', 'position', 'officer_type', 'officer_id', 'area', 'mobile', 'pro_pic']

class FIRForm(forms.ModelForm):
	class Meta:
		model = Case
		fields = ['fir_number', 'section', 'description', 'location', 'reason']

class FIRFilesForm(forms.ModelForm):

    class Meta:
        model = Case_FIR_Files
        fields = ['file']	
		
FIRFilesFormSet = formset_factory(FIRFilesForm, extra=3)

class ComplainantForm(forms.ModelForm):
	class Meta:
		model = Complainant
		fields = ['name', 'father_name', 'mother_name', 'present_address', 'permanent_address', 'national_id', 'mobile']

class VictimForm(forms.ModelForm):

	class Meta:
		model = Victim
		fields = ['vname', 'vfather_name', 'vmother_name', 'vpresent_address', 'vpermanent_address', 'vnational_id', 'vmobile']
		
VictimFormSet = formset_factory(VictimForm, extra=1)
		
class DefendantForm(forms.ModelForm):
	class Meta:
		model = Defendant
		fields = ['name', 'father_name', 'mother_name', 'present_address', 'permanent_address', 'criminal_id', 'mobile']

DefendantFormFormSet = formset_factory(DefendantForm, extra=1)
		
class CaseUpdateForm(forms.ModelForm):
	
	class Meta:
		model = Case_Update
		fields = ['title', 'description']
		
class CaseUpdateFilesForm(forms.ModelForm):

    class Meta:
        model = Case_Update_Files
        fields = ['file']	
		
CaseUpdateFilesFormSet = formset_factory(CaseUpdateFilesForm, extra=3)

class ChargeSheetForm(forms.ModelForm):

    class Meta:
        model = Charge_sheet
        fields = ['name', 'aliases', 'father_name', 'mother_name', 'present_address', 'permanent_address', 'charges']

ChargeSheetFormSet = formset_factory(ChargeSheetForm, extra=1)		

class VerdictFilesForm(forms.ModelForm):

    class Meta:
        model = Verdict_Files
        fields = ['file']	
		
VerdictFilesFormSet = formset_factory(VerdictFilesForm, extra=3)

		