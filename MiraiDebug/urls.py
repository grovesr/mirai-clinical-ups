from django.conf.urls import patterns, include, url
from django.contrib import admin
from MiraiDebug import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MiraiDebug.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^ups/', include('ups.urls', namespace='ups')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.home),
)
