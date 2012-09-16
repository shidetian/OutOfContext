# Create your views here.

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse
from json import *
from models import *

@csrf_exempt
def home(request):
    facebook_profile = None
    try:
        facebook_profile = request.user.get_profile().get_facebook_profile()
        return render_to_response('homepage.html',
            { 'facebook_profile': facebook_profile },
        context_instance=RequestContext(request))
    except:
        return redirect("/facebook/login")

@csrf_exempt
def ping(request, round):
    if not request.user.is_authenticated():
        return HttpResponse(dumps({"error":"auth"}))
    tp = None
    try:
        round = Round.objects.get(id=round)

    except:
        return HttpResponse(dumps({"error":"round_id"}))

    completed = round.is_complete()

    try:
        tp = TemporaryPing.objects.get(user=request.user, round = round)
    except:
        return HttpResponse(dumps({"error":"tping"}))

    u = request.user
    tp.ping()

    # return the full state of the round
    votes = [(x.user_id.id, x.white_card1.info(), x.white_card2.info() if x.white_card2 else None) for x in TemporaryVotes.objects.filter(round=round)]

    return HttpResponse(dumps({"is_completed":completed, "votes_so_far":votes}))

@csrf_exempt
def newround(request):
    if not request.user.is_authenticated():
        return HttpResponse(dumps({"error":"auth"}))
    round = Round(master = request.user, participants="", black_card = Card.random_question())
    round.save()
    tp = TemporaryPing(user = request.user, round = round)
    tp.save()

    # return a new round id
    return HttpResponse(dumps({"round_id":round.id,"bc":round.black_card.info()}))

@csrf_exempt
def tvote(request, round):
    if not request.user.is_authenticated():
        return HttpResponse(dumps({"error":"auth"}))
    ping(request, round)
    try:
        round = Round.objects.get(id=round)
    except:
        return HttpResponse(dumps({"error":"round_id"}))

    cid = 1;
    card = None;
    if (request.method == 'GET'):
        cid = request.GET['cid']

    print request.method

    try:
        card = Card.objects.get(id=cid)
    except:
        return HttpResponse(dumps({"error":"card_id"}))

    # create a temporaryvote object
    tvote = TemporaryVotes(user_id = request.user,black_card=round.black_card,white_card1=card, round=round)
    tvote.save()

    return HttpResponse(dumps({"success":True}))

@csrf_exempt
def vote(request, round):
    if not request.user.is_authenticated():
        return HttpResponse(dumps({"error":"auth"}))
    ping(request, round)
    try:
        round = Round.objects.get(id=round)
    except:
        return HttpResponse(dumps({"error":"round_id"}))

    cid = 1;
    card = None;
    comment = "";
    if (request.method == 'GET'):
        cid = request.GET['cid']

    try:
        card = Card.objects.get(id=cid)
    except:
        return HttpResponse(dumps({"error":"card_id"}))

    # create a temporaryvote object
    tvote = Vote(user_id = request.user,black_card=round.black_card,white_card1=card, round=round,comment=comment)
    tvote.save()

    return HttpResponse(dumps({"success":True}))

@csrf_exempt
def wcards(request):
    return HttpResponse(dumps([c.info() for c in Card.random_answers(9)]))

@csrf_exempt
def record(request,timestamp):
    # only return those after the timestamp
    rounds = [(r.id, r.completed, [(v.user_id.id,v.black_card.info(),v.white_card1.info()) for v in TemporaryVotes.objects.filter(round=r)] or None, Vote.objects.filter(round=r) or None) for r in Round.objects.order_by('time').exclude(time__lt = datetime.datetime.fromtimestamp(float(timestamp)))[:80]]
    return HttpResponse(dumps({"rounds":rounds,"timestamp":time.time()}))

@csrf_exempt
def info(request,timestamp):
    rounds = None
    if request.method == 'GET':
        rounds = map(int,request.GET['rounds'].split(','))
    else:
        return record(request, timestamp)

    bundle = {}
    for round_id in rounds:
        # return completed or not
        round = None
        try:
            round = Round.objects.get(id=round_id)
        except:
            continue
        c0 = round.is_complete()
        c1 = round.completed
        tv = [(v.user_id.id,v.white_card1.info()) for v in TemporaryVotes.objects.filter(round=round).order_by('pub_dat').exclude(pub_dat__lt = datetime.datetime.fromtimestamp(float(timestamp)))] or None
        av = [(v.white_card1.info()) for v in Vote.objects.filter(round=round)] or None
        com = [(c.author.id, c.time) for c in Comment.objects.filter(round=round).order_by('time').exclude(time__lt = datetime.datetime.fromtimestamp(float(timestamp)))]
        bundle[round_id] = (c0,c1,tv,av,com)

    return HttpResponse(dumps({"bundle":bundle,"timestamp":time.time()}))

@csrf_exempt
def stats(request, black, white):
    try:
        black = Card.objects.get(id=black)
        white = Card.objects.get(id=white)
    except:
        return HttpResponse(dumps({"error","card_id"}))

    num = Vote.cum_white(black,white)
    den = Vote.cum_black(black)

    if den < 1:
        return HttpResponse(dumps({"stats":num}))
    return HttpResponse(dumps({"stats":num/float(den)}))

@csrf_exempt
def update(request):
    if request.method != "POST":
        return HttpResponse(dumps({"error","POST"}))

    if not request.user.is_authenticated():
        return HttpResponse(dumps({"error":"auth"}))

    type = request.POST['type']
    text = request.POST['text']
    u = request.user

    c = Card(user_id=u,question=(type=="bl"),text=text)
    c.save()
    return HttpResponse(dumps({"success":1}))

@csrf_exempt
def game(request):
    if not request.user.is_authenticated():
        return redirect("/facebook/login")
    round = Round(master = request.user, participants="", black_card = Card.random_question())
    round.save()
    tp = TemporaryPing(user = request.user, round = round)
    tp.save()

    # return a new round id
    return render_to_response('scrolling.html',
            { 'round_id': round.id, 'bc':dumps(round.black_card.info()), 'cards': dumps([c.info() for c in Card.random_answers(9)])})

@csrf_exempt
def editor(request):
    if not request.user.is_authenticated():
        return redirect("/facebook/login")

    # return a new round id
    return render_to_response('editor.html')

