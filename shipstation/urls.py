from django.conf.urls import patterns, url

from shipstation import views

urlpatterns = patterns('',
    # ex: /ups/
    url(r'^$', views.shipstation_home, name='shipstation_home'),
    url(r'^shipstation_home/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})$', views.shipstation_home_dates, name='shipstation_home_dates'),
    url(r'^shipstation_sku_report/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})$', views.shipstation_sku_report, name='shipstation_sku_report'),
    url(r'^shipstation_customer_report/(?P<startDate>\d{2}-\d{2}-\d{4})/(?P<stopDate>\d{2}-\d{2}-\d{4})$', views.shipstation_customer_report, name='shipstation_customer_report'),
    )