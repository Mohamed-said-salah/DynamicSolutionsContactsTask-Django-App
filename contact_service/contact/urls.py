from django.urls import path
from .views import ContactListCreateView, ContactDetailView

urlpatterns = [
    path('contacts/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('contacts/<int:pk>', ContactDetailView.as_view(), name='contact-detail'),
]

