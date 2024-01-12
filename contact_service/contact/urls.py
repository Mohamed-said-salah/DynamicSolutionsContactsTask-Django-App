from django.urls import path, include # to include our views on the api
from . import views # had all of our endpoints views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # Login, RefreshToken endpoints

# User creation and Auth(Login)
user_urls = [
    path('register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('login/', TokenObtainPairView.as_view(), name='user_login'),
]

# Manage Tokens
token_urls = [
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Contacts 
contact_urls = [
    path("create/", views.ContactCreateView.as_view(), name='contact-create'),
    path("search/", views.ContactSearchView.as_view(), name='contact-details'),
    path("detail/<int:pk>/", views.ContactDetailView.as_view(), name='contact-details'),
    path("lock/<int:pk>/", views.ContactLockEditView.as_view(), name='contact-lock-edit'),
    path("edit/<int:pk>/<str:lock_token>/", views.ContactEditView.as_view(), name='contact-edit'),
    # Add other contact-related URL patterns as needed
]

urlpatterns = [
    path('users/', include(user_urls), name='users'), # links user views to the api
    path('contacts/', include(contact_urls), name='contacts'), # links contacts views to the api
    path('token/', include(token_urls), name='tokens'), # links token refreshing to the api
]

