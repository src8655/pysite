from django.forms import model_to_dict
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render


# Create your views here.
from user.models import User


def joinform(request):
    return render(request, 'user/joinform.html')


def join(request):
    user = User()

    user.name = request.POST['name']
    user.email = request.POST['email']
    user.gender = request.POST['gender']
    user.password = request.POST['password']

    # 스크립트를 무시하고 잘못된 정보를 줬을 때
    if user.name == '':
        return HttpResponseRedirect('/')
    if user.email == '':
        return HttpResponseRedirect('/')
    if user.gender == '':
        return HttpResponseRedirect('/')
    if user.password == '':
        return HttpResponseRedirect('/')

    user.save()

    return HttpResponseRedirect('/user/joinsuccess')


def joinsuccess(request):
    return render(request, 'user/joinsuccess.html')


def loginform(request):
    return render(request, 'user/loginform.html')


def login(request):
    results = User.objects.filter(email=request.POST['email']).filter(password=request.POST['password'])

    # 로그인 실패
    if len(results) == 0:
        return HttpResponseRedirect('/user/loginform?result=fail')

    # 로그인 처리
    authuser = results[0]
    request.session['authuser'] = model_to_dict(authuser)

    return HttpResponseRedirect('/')


def logout(request):
    request.session['authuser'] = None
    return HttpResponseRedirect('/')


def updateform(request):
    user = User.objects.get(id=request.session['authuser']['id'])
    data = {
        'user': user
    }
    return render(request, 'user/updateform.html', data)


def update(request):
    user = User.objects.get(id=request.session['authuser']['id'])
    user.name = request.POST['name']
    user.gender = request.POST['gender']
    if request.POST['password'] is not '':
        user.password = request.POST['password']

    # 스크립트를 무시하고 잘못된 정보를 줬을 때
    if user.name == '':
        return HttpResponseRedirect('/')
    if user.gender == '':
        return HttpResponseRedirect('/')

    user.save()

    request.session['authuser'] = model_to_dict(user)

    return HttpResponseRedirect('/user/updateform?result=success')


def checkemail(request):
    email = request.GET['email']
    if email is None:
        result = {
            'result': 'fail',
            'data': None
        }
        return JsonResponse(result)

    user = User.objects.filter(email=email)

    data = False
    if len(user) != 0:
        data = True

    result = {
        'result': 'success',
        'data': data
    }
    return JsonResponse(result)
