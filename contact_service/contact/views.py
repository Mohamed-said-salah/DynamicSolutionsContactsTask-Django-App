# from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer
from .utils import DistributedLock
from rest_framework.authentication import BasicAuthentication

# Create your views here.
class ContactListCreateView(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get(self, req, *args, **kwargs):
        return Response({"Message": "Welcome to Django."}, status=status.HTTP_200_OK)

class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    authentication_classes = [BasicAuthentication]

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

