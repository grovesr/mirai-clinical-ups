from django.conf.urls import patterns, url

from ups import views

urlpatterns = patterns('',
     # ex: /ups/
    url(r'^$', views.index, name='index'),
    url(r'^file_selection$', views.file_selection, name='file_selection'),
    url(r'^(?P<pk>\d+)/pick_ticket_detail/$', views.pick_ticket_detail, name='pick_ticket_detail'),
    url(r'^(?P<pk>\d+)/pick_ticket_edit/$', views.pick_ticket_edit, name='pick_ticket_edit'),
    url(r'^(?P<pk>\d+)/pick_ticket_report/$', views.pick_ticket_report, name='pick_ticket_report'),
    url(r'^(?P<pk>\d+)/pick_ticket_error_report/$', views.pick_ticket_error_report, name='pick_ticket_error_report'),
    url(r'^(?P<pk>\d+)/pick_ticket_pkt_report/$', views.pick_ticket_pkt_report, name='pick_ticket_pkt_report'),
    url(r'^pick_ticket_index/$', views.pick_ticket_index, name='pick_ticket_index'),
    url(r'^blank/$', views.blank, name='blank'),
    )