from django.conf.urls import url, include
from views import *

urlpatterns = [
    url(r'^signup/$', SignupAPIView.as_view(), name='signup'),
    url(r'^verify/$', EmailVierifyAPIView.as_view(), name='verify'),
    url(r'^login/$', LoginAPIView.as_view(), name='login'),
    url(r'^$', AppAPIView.as_view(), name='apis')
]