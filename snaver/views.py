from django.template import loader
from django.http import HttpResponse




def index(request):
	context = {}
	context['segment'] = 'index'

	html_template = loader.get_template('index.html')
	return HttpResponse(html_template.render(context, request))

