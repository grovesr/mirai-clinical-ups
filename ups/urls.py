from django.conf.urls import patterns, url

from ups import views

urlpatterns = patterns('',
     # ex: /ups/
    url(r'^$', views.index, name='index'),
    url(r'^file_selection$', views.file_selection, name='file_selection'),
    url(r'^(?P<pk>\d+)/file_creation/$', views.file_creation, name='file_creation'),
    url(r'^create_pkt_file$', views.index, name='create_pkt_file'),
    )