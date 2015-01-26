from django.conf.urls import patterns, url

from ups import views

urlpatterns = patterns('',
    # ex: /ups/
    url(r'^$', views.ups_home, name='ups_home'),
    url(r'^pick_ticket_detail/(?P<pk>\d+)$', views.pick_ticket_detail, name='pick_ticket_detail'),
    url(r'^pick_ticket_detail/(?P<pk>\d+)$', views.pick_ticket_detail, name='pick_ticket_detail'),
    url(r'^pick_ticket_edit/(?P<pk>\d+)$', views.pick_ticket_edit, name='pick_ticket_edit'),
    url(r'^pick_ticket_edit_ph/(?P<pk>\d+)$', views.pick_ticket_edit_ph, name='pick_ticket_edit_ph'),
    url(r'^pick_ticket_report/(?P<pk>\d+)$', views.pick_ticket_report, name='pick_ticket_report'),
    url(r'^pick_ticket_error_report/(?P<pk>\d+)$', views.pick_ticket_error_report, name='pick_ticket_error_report'),
    url(r'^pick_ticket_pkt_report/(?P<pk>\d+)/$', views.pick_ticket_pkt_report, name='pick_ticket_pkt_report'),
    url(r'^pick_ticket_file_report/(?P<pk>\d+)/$', views.pick_ticket_file_report, name='pick_ticket_file_report'),
    url(r'^pick_ticket_index/$', views.pick_ticket_index, name='pick_ticket_index'),
    url(r'^blank/$', views.blank, name='blank'),
    )