# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics, views, permissions, status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from serializers import UserSignupSerializer, LoginSerializer, UserSerializer
from . import email_verifier


# Create your views here.
class AppAPIView(views.APIView):
    permission_classes = (
        permissions.AllowAny,
    )

    def get(self, request, format=None):
        return Response({
            'signup': reverse('api:signup', request=request, format=format),
            'verify': reverse('api:verify', request=request, format=format),
            'login': reverse('api:login', request=request, format=format)
        })


class EmailVierifyAPIView(views.APIView):
    permission_classes = (
        permissions.AllowAny,
    )

    def get(self, request, format=None):
        result = email_verifier.verify(request.query_params.get('email', None))
        return Response({
            'verified': result
        })


class SignupAPIView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = (
        permissions.AllowAny,
    )


class LoginAPIView(generics.GenericAPIView):
    """
    Use this endpoint to obtain user authentication token.
    """
    serializer_class = LoginSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get user from serializer after validation
        user = serializer.user

        # serialize to user serializer
        user_serializer = UserSerializer(user)
        return Response(
            data=user_serializer.data,
            status=status.HTTP_200_OK,
        )
