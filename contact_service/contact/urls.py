from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

user_urls = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    # Add other user-related URL patterns as needed
]

token_urls = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

contact_urls = [
    path('create/', ContactCreateView.as_view(), name='contact-create'),
    path('<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    path('update/<int:pk>/', ContactUpdateView.as_view(), name='contact-update'),
    # Add other contact-related URL patterns as needed
]

urlpatterns = [
    path('users/', include(user_urls)),
    path('contacts/', include(contact_urls)),
]

