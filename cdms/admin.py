from django.contrib import admin
from .models import Criminal, Criminal_images, District, Thana, Officer

# Register your models here.

class ImagesAdmin(admin.StackedInline):
	model = Criminal_images
	extra = 3
	
class CriminalAdmin(admin.ModelAdmin):
	inlines =  [ImagesAdmin]

admin.site.register(Criminal, CriminalAdmin)
admin.site.register(Criminal_images)
admin.site.register(District)
admin.site.register(Thana)
admin.site.register(Officer)