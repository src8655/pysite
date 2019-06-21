import math
from urllib import parse

from django.db.models import Max, F
from django.http import HttpResponseRedirect
from django.shortcuts import render


# 게시판 리스트
from board.models import Board


def boardlist(request):
    pages = int(request.GET.get('pages', 1))        # 현재 페이지
    kwd = str(request.GET.get('kwd', ''))           # 검색어
    # 공통 파라미터 --------------------------------------------------------------

    # 페이징 ------------------------------------------------------------------------------------------
    boardcnt = 5                                    # 한번에 보여질 게시글
    pagecnt = 3                                     # 페이지 버튼 개수

    count = Board.objects.filter(title__contains=kwd).count()                  # 총 게시글 개수
    lastpage = int(math.ceil(float(count)/float(boardcnt)))            # 마지막페이지
    startnum = (pages-1) * boardcnt                                    # 시작번호
    rangestart = int(int((pages-1)/pagecnt) * pagecnt+1)               # 페이지 범위 시작점
    pagerange = range(rangestart, rangestart+pagecnt)   # 페이지 범위

    paging = {
                'boardcnt': boardcnt,
                'pagecnt': pagecnt,
                'count': count,
                'lastpage': lastpage,
                'startnum': startnum,
                'rangestart': rangestart,
                'rangestart_1': rangestart-1,
                'rangestart__pagecnt': rangestart+pagecnt,
                'range': pagerange
             }
    # -------------------------------------------------------------------------------------------------

    boards = Board.objects.all().filter(title__contains=kwd).order_by('-groupno', 'orderno')[startnum:startnum+boardcnt]

    data = {
        'boards': boards,
        'paging': paging,
        'pages': pages,
        'kwd': kwd
    }

    return render(request, 'board/list.html', data)


# 작성하기
def write(request):
    pages = int(request.GET.get('pages', 1))        # 현재 페이지
    kwd = str(request.GET.get('kwd', ''))           # 검색어
    # 공통 파라미터 --------------------------------------------------------------

    # 로그인 확인
    authuser = request.session['authuser']
    if authuser is None:
        return HttpResponseRedirect('/board')

    parentno = request.GET.get('parentno', -1) # 답글인지 아닌지

    data = {
        'parentno': parentno,
        'pages': pages,
        'kwd': kwd
    }

    return render(request, 'board/write.html', data)


# 작성하기 post
def write_post(request):
    pages = int(request.POST.get('pages', 1))        # 현재 페이지
    kwd = str(request.GET.get('kwd', ''))           # 검색어
    # 공통 파라미터 --------------------------------------------------------------

    # 로그인 확인
    authuser = request.session['authuser']
    if authuser is None:
        return HttpResponseRedirect('/board')

    board = Board()
    board.user_id = authuser['id']
    board.title = request.POST['title']
    board.content = request.POST['content']

    # 부모id가 있으면 답글
    parentno = int(request.POST.get('parentno', -1))

    if parentno == -1:
        # groupno : 답글이 아니면 (Max+1)
        value = Board.objects.aggregate(max_groupno=Max('groupno'))
        max_groupno = 0 if value['max_groupno'] is None else value['max_groupno']
        board.groupno = max_groupno+1

        # orderno : 답글이 아니면 항상 1
        board.orderno = 1

        # depth : 답글이 아니면 항상 0
        board.depth = 0
    else:
        # 답글이면 일단 부모 객체를 가져온다
        parents = Board.objects.get(id=parentno)

        # groupno : 답글이면 부모것과 같게
        board.groupno = parents.groupno

        # orderno : 답글이면 (부모것+1) 보다 크거나 같은거 모두 (+1)해서 밀고 (부모것+1)
        board.orderno = parents.orderno+1
        Board.objects.filter(groupno=board.groupno).filter(orderno__gte=board.orderno).update(orderno=F('orderno') + 1)

        # depth : 답글이면 (부모것+1)
        board.depth = parents.depth + 1

        # parentno : 답글이면 부모번호
        board.parentno = parentno

    board.save()

    return HttpResponseRedirect('/board')


# 수정하기
def modify(request):
    pages = int(request.GET.get('pages', 1))        # 현재 페이지
    kwd = str(request.GET.get('kwd', ''))           # 검색어
    # 공통 파라미터 --------------------------------------------------------------

    # 로그인 확인
    authuser = request.session['authuser']
    if authuser is None:
        return HttpResponseRedirect('/board')

    # no가 없으면 잘못된 접근
    no = int(request.GET.get('no', -1))
    if no == -1:
        return HttpResponseRedirect('/board')

    boardview = Board.objects.get(id=no)

    # 내 게시글이 아니면 잘못된 접근
    if authuser['id'] != boardview.user.id:
        return HttpResponseRedirect('/board')

    data = {
        'no': no,
        'boardview': boardview,
        'pages': pages,
        'kwd': kwd
    }

    return render(request, 'board/modify.html', data)


# 수정하기 post
def modify_post(request):
    pages = int(request.POST.get('pages', 1))        # 현재 페이지
    kwd = str(request.GET.get('kwd', ''))           # 검색어
    # 공통 파라미터 --------------------------------------------------------------

    # 로그인 확인
    authuser = request.session['authuser']
    if authuser is None:
        return HttpResponseRedirect('/board')

    # no가 없으면 잘못된 접근
    no = int(request.POST.get('no', -1))
    if no == -1:
        return HttpResponseRedirect('/board')

    boardview = Board.objects.get(id=no)

    # 내 게시글이 아니면 잘못된 접근
    if authuser['id'] != boardview.user.id:
        return HttpResponseRedirect('/board')

    # boardview.title = request.POST.get('title', '')
    # boardview.content = request.POST.get('content', '')
    # boardview.save()

    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    Board.objects.filter(id=no).update(title=title, content=content)

    return HttpResponseRedirect('/board/view?no={0}&pages={1}'.format(no, pages))


# 게시글 보기
def view(request):
    pages = int(request.GET.get('pages', 1))        # 현재 페이지
    kwd = str(request.GET.get('kwd', ''))           # 검색어
    # 공통 파라미터 --------------------------------------------------------------

    # no가 없으면 잘못된 접근
    no = int(request.GET.get('no', -1))
    if no == -1:
        return HttpResponseRedirect('/board')

    boardview = Board.objects.get(id=no)

    data = {
        'no': no,
        'boardview': boardview,
        'pages': pages,
        'kwd': kwd
    }
    response = render(request, 'board/view.html', data)

    # 조회수 처리
    cookie_name = 'board_hit'   # 쿠키이름

    if cookie_name not in request.COOKIES:
        # 최초 방문하였다면 쿠키를 새로 만들어야함
        Board.objects.filter(id=no).update(hit=F('hit')+1)
        response.set_cookie(cookie_name, str(no), max_age=365*24*60*60)
    else:
        print(request.COOKIES[cookie_name])
        # 쿠키가 있으면 게시글을 방문했는지 확인
        strings = request.COOKIES[cookie_name].split('/')
        if str(no) not in strings:
            # 방문한 기록이 없으며 조회수 증가
            Board.objects.filter(id=no).update(hit=F('hit')+1)
            # 쿠키 처리
            response.set_cookie(cookie_name, request.COOKIES[cookie_name]+'/'+str(no), max_age=365 * 24 * 60 * 60)

    return response


def delete(request):
    pages = int(request.GET.get('pages', 1))        # 현재 페이지
    kwd = str(request.GET.get('kwd', ''))           # 검색어
    # 공통 파라미터 --------------------------------------------------------------

    # 로그인 확인
    authuser = request.session['authuser']
    if authuser is None:
        return HttpResponseRedirect('/board')

    # no가 없으면 잘못된 접근
    no = int(request.GET.get('no', -1))
    if no == -1:
        return HttpResponseRedirect('/board')

    boardview = Board.objects.get(id=no)

    # 내 게시글이 아니면 잘못된 접근
    if authuser['id'] != boardview.user.id:
        return HttpResponseRedirect('/board')

    # 삭제
    # 자식 개수 확인
    countchild = Board.objects.filter(parentno=no).count()
    # 자식이 있으면 상태만 삭제로 변경
    if countchild != 0:
        boardview.status = -1
        boardview.save()
    else:
        # 나한테 부모가 있는지 확인
        parentno = boardview.parentno
        # 자식이 없으면 본인것을 삭제
        boardview.delete()

        # 부모가 있으면 부모한테 올라가면서 부모가 삭제상태인지 확인하면서 반복
        if parentno != -1:
            delrepeat(parentno)

    return HttpResponseRedirect('/board?pages={0}&kwd={1}'.format(pages, kwd))


def delrepeat(no):
    boardview = Board.objects.get(id=no)

    # 상태가 삭제 상태면
    if boardview.status == -1:
        # 자식 개수 확인
        countchild = Board.objects.filter(parentno=no).count()
        # 자식이 있으면 상태만 삭제로 변경
        if countchild != 0:
            boardview.status = -1
            boardview.save()
        else:
            # 나한테 부모가 있는지 확인
            parentno = boardview.parentno
            # 자식이 없으면 본인것을 삭제
            boardview.delete()

            # 부모가 있으면 부모한테 올라가면서 부모가 삭제상태인지 확인하면서 반복
            if parentno != -1:
                delrepeat(parentno)
