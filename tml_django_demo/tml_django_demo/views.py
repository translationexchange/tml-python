# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render_to_response
from django.utils import translation
from django.http import HttpResponse
from json import dumps
from django.views.decorators.csrf import csrf_exempt
from django_tml import tr


def home(request):
    language = translation.get_language_from_request(request, True)
    translation.activate(language)
    user = {'gender': request.GET.get('user_gender','male'),'name': request.GET.get('user_name','Вася')}
    to = {'gender': request.GET.get('to_gender','female'),'name': request.GET.get('to_name','Маша')}
    count = request.GET.get('count', 5)
    return render_to_response('index.html', {'user':user, 'to': to, 'count': count, 'language': language})


@csrf_exempt
def translate(request):
    label = request.POST.get('label')
    locale = request.POST.get('locale')
    translation.activate(locale)
    result = translation.ugettext(label)
    return HttpResponse(dumps({'result': result}))

