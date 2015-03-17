# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render_to_response
from django.utils import translation
from django.http import HttpResponse
from json import dumps
from django.views.decorators.csrf import csrf_exempt


def home(request):
    return render_to_response('index.html')

@csrf_exempt
def translate(request):
    label = request.POST.get('label')
    locale = request.POST.get('locale')
    translation.activate(locale)
    result = translation.ugettext(label)
    print result
    return HttpResponse(dumps({'result': result}))

