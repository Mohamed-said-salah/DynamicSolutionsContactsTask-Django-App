from rest_framework import serializers
from .models import Contact
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# class UserSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
#     confirm_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'password', 'confirm_password', 'email']
#         extra_kwargs = {'password': {'write_only': True}}

#     def validate(self, data):
#         is_registration = self.context.get('registration', False)

#         if is_registration:
#             password = data.get('password')
#             confirm_password = data.get('confirm_password')

#             if password != confirm_password:
#                 raise serializers.ValidationError("Passwords do not match.")

#             # Add your additional password complexity requirements here if needed
#         else:
#             username = data.get('username')
#             password = data.get('password')

#             user = authenticate(username=username, password=password)

#             if user is None:
#                 raise serializers.ValidationError("Invalid credentials.")

#         return data

#     def create(self, validated_data):
#         validated_data.pop('confirm_password', None)
#         return super().create(validated_data)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField() 
    password = serializers.CharField(style={'input_type': 'password'})

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'contact_name', 'email', 'phone']