# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
from rest_framework import views, viewsets, permissions, generics, status
from rest_framework.exceptions import NotFound
from rest_framework.reverse import reverse
from rest_framework.response import Response
from serializers import PostSerializer, LikeSerializer, UnlikeSerializer
from account.serializers import UserSerializer
from django.db.models import Max, Count
from django.contrib.auth import get_user_model
from models import Post


User = get_user_model()


class AppAPIView(views.APIView):
    """ App url addresses """
    permission_classes = (
        permissions.AllowAny,
    )

    def get(self, request, format=None):
        return Response({
            'create': reverse('api:create', request=request, format=format),
            'like': reverse('api:like', args=[1], request=request, format=format),
            'unlike': reverse('api:unlike', args=[1], request=request, format=format),
            'topuser': reverse('api:topuser', request=request, format=format)
        })


class CreatePostAPIView(generics.CreateAPIView):
    """ API for creating post """
    serializer_class = PostSerializer


class LikeOrUnlikeMixin(object):
    """ Mixin for like or unlike View """
    def put(self, request, pk):
        serializer = self.get_serializer(post_id=pk, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class LikePostAPIView(LikeOrUnlikeMixin, generics.UpdateAPIView):
    """ Like post API View """
    serializer_class = LikeSerializer


class UnlikePostAPIView(LikeOrUnlikeMixin, generics.UpdateAPIView):
    """ Unlike post API View """
    serializer_class = UnlikeSerializer


class UserMostPosted(views.APIView):
    """ API View for user who has most posts and has not reached max likes """

    def get(self, request, format=None):
        """ get method with request holding maxlikes value """
        max_likes = request.query_params.get('maxlikes', 3)
        users = User.objects.annotate(
            total_likes=Count('likes'),
            total_posts=Count('posts')
        ).filter(
            total_likes__lt=max_likes
        )
        if not users:
            raise NotFound()
        user = users.latest('total_posts')
        serializer = UserSerializer(user)
        data = serializer.data
        data.update({
            'total_posts': user.total_posts,
            'likes': user.total_likes
        })
        return Response(data=data)


class RandomPostAPIView(generics.RetrieveAPIView):
    """ API View for random posts from users who have at least one post with 0 likes """
    serializer_class = PostSerializer

    def get_object(self):
        """ return object with 0 likes """
        likes_zero = Post.objects.annotate(
            total_likes=Count('likes')
        ).filter(
            total_likes=0
        )
        if 'user_id' in self.request.data:
            likes_zero = likes_zero.exclude(
                user=self.request.data['user_id']
            )

        count = likes_zero.count()
        if count:
            random_index = random.randint(0, count - 1)
            return likes_zero[random_index]
        raise NotFound()
