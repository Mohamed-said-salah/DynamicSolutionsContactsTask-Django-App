# from django.shortcuts import render
import uuid # is used for generating the lock_tokens[tokens to prevent two updates at atime]
from rest_framework import (generics, status, permissions)
from rest_framework.response import Response
from .models import Contact, User
from .utils import DistributedLock
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from .serializers import UserSerializer, ContactSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.

# Create User
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer 

    # this endpoint will only accept POST method and will handle the process of registering new user
    @extend_schema(summary="Create new user, with username, password, email")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'registration': True}) # gets string json data coming on request body as a python object
        # this will confirm unique username, and confirm password with confirmation password + extra model validation
        # There is Extra validation logic is written on the validate function on the UserSerializer
        serializer.is_valid(raise_exception=True) 
        user = serializer.save() # creates user ROW in DB
        # create the user refresh token after being signed in
        refresh = RefreshToken.for_user(user) 
        return Response({
            'refresh': str(refresh), # refresh token for. keeping user signed in
            'access': str(refresh.access_token), # to verify credentials in requests
        })

class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactSerializer # define the which serializer model is endpoint dealing with
    # To define that info or operation is for users with authentication level
    # for example authenticated is enough i.e you not have to be admin or not to be public for every one
    permission_classes = [permissions.IsAuthenticated] 
    authentication_classes = [JWTTokenUserAuthentication] # will forbidden users with no access-token with 401 response

    # will handle the process of saving new contact with only POST method
    @extend_schema(summary="Create new contact by filling the basic fields ex. phone contact_name, email")
    def post(self, request, *arg, **kwargs):
        serializer = self.get_serializer(data=request.data) # converting string json data coming on request body to python object

        if not serializer.is_valid():  # validating the coming data
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # raising bad request 400

        user_id = request.user.id # get the contact creator id from the JWT
        user_instance = User.objects.get(id=user_id) # getting user model from the db
        serializer.save(created_by=user_instance) # save the new contact with the creator
        return Response(serializer.data, status=status.HTTP_201_CREATED) # success response


class ContactDetailView(generics.RetrieveAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    # To define that info or operation is for users with authentication level
    # for example authenticated is enough i.e you not have to be admin or not to be public for every one
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTTokenUserAuthentication] # will forbidden users with no access-token with 401 response

    # get contact by id 
    @extend_schema(summary="Get contact by id")
    def get(self, request, *args, **kwargs):
        contact_id = kwargs.get('pk') # parse contact id from the coming request URL
        
        # this will try to get contact row from the DB or raising 404 response
        contact = get_object_or_404(Contact, id=contact_id) # returns 404 automatically if contact not found
        serializer = ContactSerializer(contact) # to Jsonize the The model data from the DB

        return Response(serializer.data) # response 200 with the contact


class ContactSearchView(generics.RetrieveAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    # To define that info or operation is for users with authentication level
    # for example authenticated is enough i.e you not have to be admin or not to be public for every one
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTTokenUserAuthentication] # will forbidden users with no access-token with 401 response
    
    # search for contact related to search data
    @extend_schema(parameters=[OpenApiParameter(name='q', type=str)], summary="Search contacts with name phone or email") # adding the q (query field) to the swagger docs
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q') # getting the query [searched details] from path
        search_result = Contact.objects.filter(Q(contact_name__icontains=query) | Q(email=query) | Q(phone=query)).values() # searches db with the query
        
        # raises 404 results not found if there is no related data
        if not search_result:
            return Response({"detail": "Error empty search result"},  status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message": f"Search Succeeded with {len(search_result)} result(s).", 'result': search_result})

class ContactLockEditView(generics.RetrieveAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    # To define that info or operation is for users with authentication level
    # for example authenticated is enough i.e you not have to be admin or not to be public for every one
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTTokenUserAuthentication] # will forbidden users with no access-token with 401 response
    
    # will prevent one contact to be edited from more than one place
    # only one session for editing the contact
    @extend_schema(summary="Reserve editing contact with given id to user for one update process or until lock-session expires")
    def get(self, request, *args, **kwargs) -> Response:
        contact_id = kwargs.get('pk') # parse the id for the contact will be locked

        # this will prevent some bad request from block contact that is already not found
        get_object_or_404(Contact, id=contact_id) # returns 404 if contact is not on database
        
        ## unique id for the blocking session
        lock_token = str(uuid.uuid4())
        # this will be cached as the key for blocking token in redis DB
        lock_key = f"contact_lock_{contact_id}" 
        lock = DistributedLock(lock_key, lock_token) # the object puts some values on the block-list(cache) and releases it
        if not lock.acquire():
            # this will try to add contact to block-list to be not edited by another one for 5 minutes
            # if the contact was already on block list then raises 409 conflict so it's not closes the other blocking session to new one
            return Response({'error': "Contact is locked by another user."}, status=status.HTTP_409_CONFLICT) 
        # if contact saved to the block list then will be return 200 response with the blocking key
        # this blocking key allows the carrier to only edit the contact once in a period of 5 minutes
        return Response({'lock_token': lock_token}, status=status.HTTP_200_OK) # returns lock_token to user so he can privately update the contact freely with it


class ContactEditView(generics.UpdateAPIView):
    ## This endpoint allows user carries lock_token to edit contact data
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    # To define that info or operation is for users with authentication level
    # for example authenticated is enough i.e you not have to be admin or not to be public for every one
    permission_classes = [permissions.IsAuthenticated]
    allowed_methods = ['PUT']

    # adding new contact info for users whom carrying lock_token
    @extend_schema(summary="Alters contact data with the given ones, but only for user who is locking the contact (** user who has lock_token)")
    def put(self, req, *args, **kwargs) -> Response:
        contact_id = kwargs.get('pk') # parsing the contact id from path url
        lock_key = f"contact_lock_{contact_id}" # this results with the key of the lock_token on redis caching db
        lock_token = kwargs.get('lock_token') # this is token that user updates contact if carry same one as it

        lock = DistributedLock(lock_key, lock_token) # the object puts some values on the block-list(cache) and releases it
        if not lock.verify(): # this verifies if the user carries the right lock_token
            # if lock_token failed to verify then raises 403 forbidden from editing contact
            return Response({"detail": "Invalid or expired lock token."}, status=status.HTTP_403_FORBIDDEN)
        # when user carries that right lock_token
        # then him edits get applied
        instance = self.get_object() # getting object for the contact with the mentioned id
        serializer = self.get_serializer(instance, data=req.data, partial=True) # serializer to convert json data to model and opposite
        serializer.is_valid(raise_exception=True) # validates if fields correct
        serializer.save(updated_by=self.request.user) # saving the contact with new infos and referencing the editor.
        lock.release() # unlock the contact to another updates
        return Response({'success': 'Contact updated Successfully', 'contact': serializer.data}) # 200 success message with updated contact