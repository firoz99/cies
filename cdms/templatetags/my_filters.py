from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter(name='imageFieldAddClass')
def imageFieldAddClass(value, arg):
    return value.as_widget(attrs={'class': arg, 'multiple': True, 'data-placeholder': "No File"})

@register.filter(name='thanaFieldAddClass')
def thanaFieldAddClass(value, arg):
    return value.as_widget(attrs={'class': arg, 'disabled':'disabled'})
	
@register.filter(name='labelColor')
def labelColor(value):
	if value == 'N':
		return "label-success"
	elif value == 'US':
		return "label-warning"
	elif value == 'C':
		return "label-info"
	elif value == 'I':
		return "label-primary"
	elif value == 'D':
		return "label-default"
	else:
		return "label-danger"
		
@register.filter(name="isSelected")		
def isSelected(value, arg):
	if str(value) == arg:
		return "selected"
	else:
		return ""

@register.filter(name="sizeLimit")
def sizeLimit(value):
	if len(value) > 30:
		return value[:30]+"..."
	else: 
		return value
		

@register.filter(name="attachmentClip")
def attachmentClip(value):
	if value >= 1:
		return "fa fa-paperclip"		
		
@register.filter(name="getExtension")
def getExtension(value):
	return value.split('.')[-1]
	
@register.filter(name="fileNameFiltering")
def fileNameFiltering(value):
	value = value.split('/')[-1]
	value = value.split('.')[1]
	if len(value) > 20:
		return value[:20]+"..."
	else: 
		return value
	