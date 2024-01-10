# from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer
from .utils import DistributedLock
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import UserSerializer, ContactSerializer, UserLoginSerializer
from django.contrib.auth import authenticate, login

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'registration': True})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED, headers=headers)

@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            token, create = Token.objects.get_or_create(user=user)
            return Response({"message": "User Logged in Successfully", 'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class ContactCreateView(generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ContactDetailView(generics.GenericAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

@method_decorator(csrf_exempt, name='dispatch')
class ContactUpdateView(generics.UpdateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def update(self, req, *args, **kwargs) -> Response:
        contact_id = kwargs.get('pk')
        lock_key = f"contact_lock_{contact_id}"

        lock = DistributedLock(lock_key)

        try :
            if lock.acquire() :
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=req.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response({"detail": "Contact is being update by another user."}, status=status.HTTP_409_CONFLICT)
        finally:
            lock.release()
