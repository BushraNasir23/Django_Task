import functools
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from .serializers import UserRegistrationSerializer
from .models import RevokedToken ,UserProfile
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import  urlsafe_base64_decode
from django.contrib import messages


class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully. Please check your email for verification.'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if refresh_token:
            revoked_token = RevokedToken(token=refresh_token)
            revoked_token.save()

        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)



def time_restricted_access(view_func):
    @functools.wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        current_time = timezone.localtime().time()

       
        view_start_time = timezone.datetime.strptime('1:00', '%H:%M').time()
        view_end_time = timezone.datetime.strptime('20:00', '%H:%M').time()

        if not (view_start_time <= current_time <= view_end_time):
            return JsonResponse({
                'error': 'This view is only accessible between 09:00 and 18:00',
                'current_time': str(current_time)
            }, status=status.HTTP_403_FORBIDDEN)

        return view_func(request, *args, **kwargs)

    return wrapped_view



class TimeRestrictedTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @time_restricted_access
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response
    
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserProfile._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')



