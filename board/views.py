from django.http import HttpResponse
from django.shortcuts import render
from article.models import User
from article.models import Article
from django.http import HttpResponseRedirect
#여러개 마커 표시
from django.http import JsonResponse # JSON 응답
from map.models import Point
from django.forms.models import model_to_dict
#거리 계산
import math
# 이메일 발송
import smtplib
from email.mime.text import MIMEText
#

def index(request):
 return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
 # 회원정보 저장
        email = request.POST.get('email')
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        user = User(email=email, name=name, pwd=pwd)
        user.save()
        return HttpResponseRedirect('/index/')

    #회원가입을 위한 양식(HTML) 전송
    return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
# 회원정보 조회
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        try:
        # select * from user where email=? and pwd=?
            user = User.objects.get(email=email, pwd=pwd)
            request.session['email'] = email
            return render(request, 'signin_success.html')
        except:
            return render(request, 'signin_fail.html')

    return render(request, 'signin.html')


def signout(request):
    del request.session['email']  # 개별 삭제
    request.session.flush()  # 전체 삭제

    return HttpResponseRedirect('/index/')

def write(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        try:
            email = request.session['email']
            # select * from user where email = ?
            user = User.objects.get(email=email)
            # insert into article (title, content, user_id) values (?, ?, ?)
            article = Article(title=title, content=content, user=user)
            article.save()
            return render(request, 'write_success.html')
        except:
            return render(request, 'write_fail.html')

    return render(request, 'write.html')

def list(request):
# select * from article order by id desc
    article_list = Article.objects.order_by('-id')
    context = {
        'article_list' : article_list
    }
    return render(request, 'list.html', context)

def detail(request, id):
    # select * from article where id = ?
    article = Article.objects.get(id=id)
    context = {
      'article' : article
    }
    return render(request, 'detail.html', context)

def update(request, id):
    # select * from article where id = ?
    article = Article.objects.get(id=id)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        try:
            # update article set title = ?, content = ? where id = ?
            article.title = title
            article.content = content
            article.save()
            return render(request, 'update_success.html')
        except:
            return render(request, 'update_fail.html')
    context = {
        'article' : article
    }
    return render(request, 'update.html', context)

def delete(request, id):
    try:
        # select * from article where id = ?
        article = Article.objects.get(id=id)
        article.delete()
        return render(request, 'delete_success.html')
    except:
        return render(request, 'delete_fail.html')

def map(request):
    return render(request, 'map.html')

def map_data(request):
    data = Point.objects.all()
    map_list = []
    for d in data:
        d = model_to_dict(d) # QuerySet -> Dict
        map_list.append(d)
    # dict가 아닌 자료는 항상 safe=False 옵션 사용
    return JsonResponse(map_list, safe=False)

def distance(lat1, lng1, lat2, lng2) :
    theta = lng1 - lng2
    dist1 = math.sin(deg2rad(lat1)) * math.sin(deg2rad(lat2))
    dist2 = math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2))
    dist2 = dist2* math.cos(deg2rad(theta))
    dist = dist1 + dist2
    dist = math.acos(dist)
    dist = rad2deg(dist) * 60 * 1.1515 * 1.609344
    return dist
def deg2rad(deg):
    return deg * math.pi / 180.0
def rad2deg(rad):
    return rad * 180.0 / math.pi

def map_data(request):
    data = Point.objects.all()
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    map_list = []
    for d in data:
        d = model_to_dict(d) # QuerySet -> Dict
        dist = distance(float(lat), float(lng), d['lat'], d['lng'])
        if(dist <= 150): # N km 이내의 장소만 응답결과로 저장
            map_list.append(d)
    # dict가 아닌 자료는 항상 safe=False 옵션 사용
    return JsonResponse(map_list, safe=False)

def contact(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        comment = request.POST.get('comment')
        # 발신자주소, 수신자주소, 메시지
        send_mail('taegyun0236@gmail.com', email, comment)
        return render(request, 'contact_success.html')

    return render(request, 'contact.html')

def send_mail(from_email, to_email, msg):
    smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465) # SMTP 설정
    smtp.login(from_email, 'ykiijmhjccbanycy') # 인증정보 설정
    msg = MIMEText(msg)
    msg['Subject'] = '[문의사항]' + to_email # 제목
    msg['To'] = from_email # 수신 이메일
    smtp.sendmail(from_email, from_email, msg.as_string())
    smtp.quit()