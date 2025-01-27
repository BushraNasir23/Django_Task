from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    RegisterView,
    LogoutView,
    TimeRestrictedTokenObtainPairView,
)
from . import views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', TimeRestrictedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('activate/<uidb64>/<token>/',views.activate,name='activate'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
