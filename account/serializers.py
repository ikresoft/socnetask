from django.db import IntegrityError
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from rest_framework import serializers
from tasks import enrichment
from . import email_verifier
from rest_framework_jwt.settings import api_settings


User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is used for objects from USER model
    using small set of fields
    """
    token = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            User.USERNAME_FIELD,
            'first_name',
            'last_name',
            'token'
        )
        read_only_fields = (User.USERNAME_FIELD,)

class UserSignupSerializer(serializers.ModelSerializer):
    """
    User registration serializer used for signup process.
    """
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True
    )

    default_error_messages = {
        'cannot_create_user': u'Integrity error. User exist!',
        'email_not_verified': u'Email is not verified!',
    }

    def validate_password(self, value):
        """ Validate password using django auth validate function """
        validate_password(value)
        return value

    def validate_email(self, value):
        """ 
        After email adress is validated we have to check cached verified emails
        if its not we have to verify email with service emailhunter.
        This is done bcs some clients can make separete API call like browsers
        """
        # first we check cache
        if value in email_verifier.get_emails():
            return value
        else:
            # we make a api call
            if email_verifier.verify(value):
                return value
            else:
                raise serializers.ValidationError(
                    self.error_messages['email_not_verified']
                )

    def create(self, validated_data):
        """
        Try to save and activate user if everything is ok return instance of User
        if username exists raise Validation error! Required fields are:
        username, email, password
        """
        try:
            user = User.objects.create_user(**validated_data)
            user.is_active = True
            user.save(update_fields=['is_active'])
        except IntegrityError:
            raise serializers.ValidationError(
                self.error_messages['cannot_create_user']
            )

        # remove from cache
        email_verifier.remove(user.email)

        # enrichment data using celery, potential user shoud not 
        # wait for background processes
        enrichment.delay(user.pk)
        return user

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD, 'password',
        )


class LoginSerializer(serializers.Serializer):
    """
    Simple login user serializer based on two fields
    username and password
    """
    password = serializers.CharField(
        required=False, style={'input_type': 'password'},
        write_only=True
    )

    default_error_messages = {
        'inactive_account': u'Invalid account!',
        'invalid_credentials': 'Invalid username or password!',
    }

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None
        self.fields[User.USERNAME_FIELD] = serializers.CharField(required=False)

    def validate(self, data):
        """ if validation is ok inject JWT token into user instance """
        self.user = authenticate(
            username=data.get(User.USERNAME_FIELD),
            password=data.get('password')
        )
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(
                    self.error_messages['inactive_account']
                )
            payload = jwt_payload_handler(self.user)
            self.user.token = jwt_encode_handler(payload)
            return data
        else:
            raise serializers.ValidationError(
                self.error_messages['invalid_credentials']
            )
