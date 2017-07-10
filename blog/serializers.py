from functools import wraps
from django.contrib.auth import get_user_model
from rest_framework import serializers, authentication
from models import *


User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    authentication_classses = (authentication.TokenAuthentication)

    class Meta:
        model = Post
        fields = '__all__'


class BaseLikeUnlikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    likes = serializers.IntegerField(required=False, read_only=True)

    default_error_messages = {
        'post_not_found': u'Post not found!',
        'user_not_found': u'User not found!',
        'cant_like_post': u'User cant like own post!'
    }

    def __init__(self, post_id, *args, **kwargs):
        super(BaseLikeUnlikeSerializer, self).__init__(*args, **kwargs)
        self.post_id = post_id

    def validate(self, data):
        try:
            self.post = Post.objects.get(pk=self.post_id)
        except Post.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages['post_not_found']
            )
        
        try:
            self.user = User.objects.get(pk=data['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages['post_not_found']
            )
        
        if self.user.pk == self.post.user.pk:
            raise serializers.ValidationError(
                self.error_messages['cant_like_post']
            )
        return data


def inject_likes(func):
    """ decorator for injecting total likes of post """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """ wrapper function """
        data = func(self, *args, **kwargs)
        data['likes'] = self.post.likes.count()
        return data
    return wrapper


class LikeSerializer(BaseLikeUnlikeSerializer):
    
    @inject_likes
    def validate(self, data):
        data = super(LikeSerializer, self).validate(data)
        if self.user.pk == self.post.user.pk:
            raise serializers.ValidationError(
                self.error_messages['cant_like_post']
            )

        self.post.likes.add(self.user)
        return data


class UnlikeSerializer(BaseLikeUnlikeSerializer):
    
    @inject_likes
    def validate(self, data):
        data = super(UnlikeSerializer, self).validate(data)

        self.post.likes.remove(self.user)
        return data
