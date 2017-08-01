import os
from django.core.files.storage import default_storage
from django.db.models import FileField

def file_cleanup(sender, instance, **kwargs):

	instance.image.delete(False)
	
