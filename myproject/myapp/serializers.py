from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from myapp.models import UserInfo, Make, Model, VehicleInfo, SaleInfo

class VehicleSerializer(serializers.ModelSerializer):
    make = serializers.CharField(required=True)
    model = serializers.CharField(required=True)

    class Meta:
        model = VehicleInfo
        fields = ("id","vin","make","model","year")

class SaleSerializer(serializers.ModelSerializer):
    seller = serializers.CharField(required=True)
    buyer = serializers.CharField(required=True)
    vehicle = serializers.IntegerField(required=True)

    class Meta:
        model = SaleInfo
        fields = ("id","seller","buyer","vehicle","price")

class MakeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Make
        fields = ("id","name",)

class ModelSerializer(serializers.ModelSerializer):
    make = MakeSerializer(read_only=True)
    class Meta:
        model = Model
        fields = ("id","name","make",)

class VehicleInfoSerializer(serializers.ModelSerializer):
    make = MakeSerializer(read_only=True)
    model = ModelSerializer(read_only=True)

    class Meta:
        model = VehicleInfo
        fields = ("id","vin","make","model","year")

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','first_name','last_name')

class SaleInfoSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    buyer = UserSerializer(read_only=True)
    vehicle = VehicleInfoSerializer(read_only=True)

    class Meta:
        model = SaleInfo
        fields = ("id","seller","buyer","vehicle","price","sale_date")

class ModelPostSerializer(serializers.ModelSerializer):
    make = serializers.CharField(required=True)
    class Meta:
        model = Model
        fields = ("id","name","make",)

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password', 'confirm_password', )

class RegistrationSerializer(UserRegistrationSerializer):
    class Meta(UserRegistrationSerializer.Meta):
        model = UserInfo
        fields = UserRegistrationSerializer.Meta.fields + ('dealership','location',)

    def create(self, validated_data):
        del validated_data["confirm_password"]
        return super(RegistrationSerializer, self).create(validated_data)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Those passwords don't match.")
        return attrs

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    default_error_messages = {
        'inactive_account': _('User account is disabled.'),
        'invalid_credentials': _('Unable to login with provided credentials.')
    }

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        self.user = authenticate(username=attrs.get("username"), password=attrs.get('password'))
        if self.user:
            if not self.user.is_active:
                raise serializers.ValidationError(self.error_messages['inactive_account'])
            return attrs
        else:
            raise serializers.ValidationError(self.error_messages['invalid_credentials'])

class TokenSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')

    class Meta:
        model = Token
        fields = ("auth_token",)
