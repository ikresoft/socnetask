from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^post/create/$', CreatePostAPIView.as_view(), name='create'),
    url(r'^post/(?P<pk>\d+)/like/$', LikePostAPIView.as_view(), name='like'),
    url(r'^post/(?P<pk>\d+)/unlike/$', UnlikePostAPIView.as_view(), name='unlike'),
    url(r'^post/topuser/$', UserMostPosted.as_view(), name='topuser'),
    url(r'^post/random/$', RandomPostAPIView.as_view(), name='random'),
    url(r'^$', AppAPIView.as_view())
]