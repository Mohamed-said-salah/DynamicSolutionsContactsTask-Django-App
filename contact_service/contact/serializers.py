from rest_framework import serializers
from .models import Contact
from django.contrib.auth.models import User
from django.contrib.auth import authenticate 

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}, 'email': {'required': True}}

    # check if the user is not already on DB
    # and checks if username is not used before
    # and password is equal to confirm password
    def validate(self, data):
        is_registration = self.context.get('registration', False)

        if is_registration:
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if password != confirm_password:
                raise serializers.ValidationError("Passwords do not match.")

        else:
            username = data.get('username')
            password = data.get('password')

            user = authenticate(username=username, password=password)

            if user is None:
                raise serializers.ValidationError("Invalid credentials.")

        return data
        

    def create(self, validated_data):
        validated_data.pop('confirm_password') # remove confirm_password to not conflict with orm db model fields
        user = User.objects.create_user(**validated_data)
        return user

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        extra_kwargs = {
                'created_by': {'required': False, 'read_only': True},
                'updated_by': {'required': False, 'read_only': True},
            }