# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render_to_response
from django.utils import translation
from django.http import HttpResponse
from json import dumps, loads
from django.views.decorators.csrf import csrf_exempt
from django_tml import tr, activate, activate_source, deactivate_source
from django_tml import inline_translations


def home(request):
    language = translation.get_language_from_request(request, True)
    translation.activate(language)
    user = {'gender': request.GET.get('user_gender','male'),'name': request.GET.get('user_name','Вася')}
    to = {'gender': request.GET.get('to_gender','female'),'name': request.GET.get('to_name','Маша')}
    count = request.GET.get('count', 5)
    return render_to_response('index.html', {'user':user,
                                             'to': to,
                                             'count': count,
                                             'language': language,
                                             'inline_tranlations_enabled': inline_translations.enabled})


@csrf_exempt
def translate(request):
    label = request.POST.get('label')
    description = request.POST.get('description')
    locale = request.POST.get('locale')
    json = request.POST.get('data')
    if json:
        data = loads(json)
    else:
        data = {}
    activate(locale)
    source = request.POST.get('source')
    if source:
        # init source:
        activate_source(source)
    result = tr(label, data, description)
    deactivate_source() # reset source
    return HttpResponse(dumps({'result': result}))

@csrf_exempt
def inline_mode(request):
    if request.POST.get('inline_mode', False):
        inline_translations.turn_on_for_session()
    else:
        inline_translations.turn_off_for_session()
    return redirect('/')

