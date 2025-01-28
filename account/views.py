import functools
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from .serializers import UserRegistrationSerializer, TokenRevokeSerializer
from .models import UserProfile, EmailCode
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.generics import CreateAPIView


class RegisterView(CreateAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TokenRevokeSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            serializer.save()
        except TokenError:
            return Response(
                {"detail": "Token is blacklisted", "code": "token_not_valid"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(status=status.HTTP_200_OK)


def time_restricted_access(view_func):
    @functools.wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        current_time = timezone.localtime().time()

        view_start_time = timezone.datetime.strptime("1:00", "%H:%M").time()
        view_end_time = timezone.datetime.strptime("20:00", "%H:%M").time()

        if not (view_start_time <= current_time <= view_end_time):
            return JsonResponse(
                {
                    "error": "This view is only accessible between 09:00 and 18:00",
                    "current_time": str(current_time),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return view_func(request, *args, **kwargs)

    return wrapped_view


class TimeRestrictedTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @time_restricted_access
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response


class VerifySignupEmail(APIView):
    def get(self, *args, email: str, code: str):
        user_profile = UserProfile.objects.filter(email=email).first()
        if not user_profile:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        email_code = EmailCode.objects.filter(
            profile=user_profile,
            mail_code=code,
            is_active=True,
        ).first()
        if email_code:
            user_profile.is_active = True
            user_profile.save()
            email_code.is_active = False
            email_code.save()
        return Response(status=status.HTTP_200_OK)
