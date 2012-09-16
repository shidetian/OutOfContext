from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cardsagainsthumanity.views.home', name='home'),
    # url(r'^cardsagainsthumanity/', include('cardsagainsthumanity.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^$', 'cah.views.home'),
    url(r'^game$','cah.views.game'),
    url(r'^editor$','cah.views.editor'),
    url(r'^cah/ping/(?P<round>\d+)/', 'cah.views.ping'),
    url(r'^cah/newround/', 'cah.views.newround'),
    url(r'^cah/tvote/(?P<round>\d+)/', 'cah.views.tvote'),
    url(r'^cah/wcards/', 'cah.views.wcards'),
    url(r'^cah/record/(?P<timestamp>\d+)/', 'cah.views.record'),
    url(r'^cah/info/(?P<timestamp>\d+)/', 'cah.views.info'),
    url(r'^cah/stats/(?P<black>\d+)/(?P<white>\d+)/', 'cah.views.stats'),
    url(r'^cah/update/', 'cah.views.update'),



    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^facebook/login$', 'facebook.views.login'),
    url(r'^facebook/authentication_callback$', 'facebook.views.authentication_callback'),
    url(r'^logout$', 'django.contrib.auth.views.logout'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
