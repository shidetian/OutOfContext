from django.db import models
from django.contrib.auth.models import User
import datetime
import time

# Create your models here.
class Card(models.Model):
    user_id=models.ForeignKey(User)
    question = models.BooleanField()
    text = models.CharField(max_length=200)

    def info(self):
        return (self.id,self.question,self.text)

    def __str__(self):
        return "("+str(self.id)+") ";

    @classmethod
    def random_question(cls):
        return Card.objects.filter(question=True).order_by('?')[0]

    @classmethod
    def random_answers(cls,n):
        return Card.objects.filter(question=False).order_by('?')[:n]



class Round(models.Model):
    master = models.ForeignKey(User, related_name="master")
    black_card = models.ForeignKey(Card)
    participants = models.CommaSeparatedIntegerField(max_length=1024,blank=True,null=True)
    completed = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True);

    def is_complete(self):
        if self.completed:
            return True
        # all participants have voted or have timed out
        all_votes = TemporaryVotes.objects.filter(round=self)
        if not TemporaryPing.objects.filter(round=self, user=self.master):
            return True
        complete = True
        for tp in TemporaryPing.objects.filter(round=self):
            u = tp.user
            time = tp.check()
            if not all_votes.filter(user_id = u):
                complete = False
        #if completed:
            #self.completed = True
            #self.save()
        return complete

    def vote(self, card, comment = ""):
        v = Vote(user_id = self.master, black_card = self.black_card, white_card1 = card, comment = comment)
        v.save()
        self.completed = True
        self.save()
        return v

class Vote(models.Model):
    user_id = models.ForeignKey(User, related_name="user_id")
    pub_dat = models.DateTimeField(auto_now_add=True)
    black_card = models.ForeignKey(Card, related_name="black_card")
    white_card1 = models.ForeignKey(Card, related_name="white_card1")
    white_card2 = models.ForeignKey(Card, blank=True,null=True, related_name="white_card2")
    round = models.ForeignKey(Round)
    comment = models.TextField()

    @classmethod
    def cum_white(cls,b,card):
        return len(Vote.objects.filter(black_card = card,white_card1 = card))

    @classmethod
    def cum_black(cls,card):
        return len(Vote.objects.filter(black_card = card))

class TemporaryPing(models.Model):
    user = models.ForeignKey(User)
    round = models.ForeignKey(Round)
    time = models.DateTimeField(auto_now_add=True)

    def ping(self):
        if not self.check(): return
        self.time = datetime.datetime.now()
        self.save()

    def check(self):
        print "in check", datetime.datetime.now() - self.time
        if datetime.datetime.now() - self.time > datetime.timedelta(seconds=10):
            print "wtf"
            # kick out
            self.delete()
            #self.save()
            return None
        return self.time

class Comment(models.Model):
    author = models.ForeignKey(User, related_name="author")
    time = models.DateTimeField(auto_now_add=True)
    round = models.ForeignKey(Round)

class TemporaryVotes(models.Model):
    user_id = models.ForeignKey(User, related_name="tuser_id")
    pub_dat = models.DateTimeField(auto_now_add=True)
    black_card = models.ForeignKey(Card, related_name="tblack_card")
    white_card1 = models.ForeignKey(Card, related_name="twhite_card1")
    white_card2 = models.ForeignKey(Card, blank=True,null=True, related_name="twhite_card2")
    round = models.ForeignKey(Round, related_name="tround")

    def delete_round(self, round):
        return self.objects.filter(round=round).delete()



