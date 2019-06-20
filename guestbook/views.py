from django.http import HttpResponseRedirect
from django.shortcuts import render


# Create your views here.
from guestbook.models import Guestbook


def guestbooklist(request):

    guestbook = Guestbook.objects.all().order_by('-id')
    cnt = len(guestbook)
    data = {
        'guestbook': guestbook,
        'cnt': cnt
    }

    return render(request, 'guestbook/list.html', data)


def add(request):
    guestbook = Guestbook()
    guestbook.name = request.POST['name']
    guestbook.password = request.POST['password']
    guestbook.content = request.POST['content']
    guestbook.save()
    return HttpResponseRedirect('/guestbook')


def deleteform(request, id=0):
    # id가 없으면
    if id == 0:
        return HttpResponseRedirect('/guestbook')

    data = {
        'id': id
    }
    return render(request, 'guestbook/deleteform.html', data)


def delete(request):
    id = request.POST['id']
    password = request.POST['password']

    guestbook = Guestbook.objects.filter(id=id).filter(password=password)
    guestbook.delete()


    return HttpResponseRedirect('/guestbook')
