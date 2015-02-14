from django.conf.urls import patterns, url

from shipstation import views

urlpatterns = patterns('',
    # ex: /ups/
    url(r'^$', views.shipstation_home, name='shipstation_home'),
    url(r'^shipstation_reports/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})$', views.shipstation_reports, name='shipstation_reports'),
    url(r'^shipstation_sku_report/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})$', views.shipstation_sku_report, name='shipstation_sku_report'),
    )