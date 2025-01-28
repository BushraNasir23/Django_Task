import datetime
import functools
import json
import jwt
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status
from account.serializers import User


class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Bypass authentication for public routes
        public_routes = [
            "/account/register/",
            "/admin/",
            "/account/login/",
            "/account/verify_signup_email/",
        ]
        if any(request.path.startswith(route) for route in public_routes):
            return self.get_response(request)

        # Check for Authorization header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse(
                {"error": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Extract and validate token
        try:
            token = auth_header.split(" ")[1]
            validated_token = self.validate_token(token, request)

            # Attach user and token info to request
            request.user = validated_token.get("user")
            request.token_payload = validated_token
        except TokenValidationError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return self.get_response(request)

    def validate_token(self, token, request):
        """
        Comprehensive token validation with multiple checks
        """
        try:
            # Decode token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Check token expiration
            exp = payload.get("exp")
            if not exp or exp < datetime.datetime.utcnow().timestamp():
                raise TokenValidationError("Token has expired")

            # Optional: Check issued at time (prevent very old tokens)
            iat = payload.get("iat")
            max_token_age = 30 * 24 * 60 * 60  # 30 days
            if iat and (datetime.datetime.utcnow().timestamp() - iat > max_token_age):
                raise TokenValidationError("Token is too old")

            # Role-based access control
            user_roles = payload.get("roles", [])
            required_roles = getattr(request, "required_roles", [])

            if required_roles and not any(
                role in user_roles for role in required_roles
            ):
                raise TokenValidationError("Insufficient permissions")

            # Time-based access control
            current_time = datetime.datetime.utcnow().time()
            access_start = payload.get("access_start")
            access_end = payload.get("access_end")

            if access_start or access_end:
                if (
                    access_start
                    and current_time
                    < datetime.datetime.strptime(access_start, "%H:%M").time()
                ):
                    raise TokenValidationError(
                        "Access not allowed before specified time"
                    )

                if (
                    access_end
                    and current_time
                    > datetime.datetime.strptime(access_end, "%H:%M").time()
                ):
                    raise TokenValidationError(
                        "Access not allowed after specified time"
                    )

            return payload

        except jwt.ExpiredSignatureError:
            raise TokenValidationError("Token signature has expired")
        except jwt.InvalidTokenError:
            raise TokenValidationError("Invalid token")


def require_roles(*roles):
    """
    Decorator to specify required roles for a view
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Attach required roles to the request
            request.required_roles = roles
            return view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


class TokenValidationError(Exception):
    """Custom exception for token validation errors"""

    pass


# Utility function to generate a token with extended claims
def generate_enhanced_token(user, roles=None, access_start=None, access_end=None):
    """
    Generate a JWT token with additional claims for role and time-based access

    :param user: User object
    :param roles: List of user roles
    :param access_start: Start time for token access (format: 'HH:MM')
    :param access_end: End time for token access (format: 'HH:MM')
    :return: JWT token
    """
    payload = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": roles or [],
        "access_start": access_start,
        "access_end": access_end,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


# Example view with role-based access
@require_roles("admin", "manager")
def admin_dashboard(request):
    # Only admins and managers can access this view
    return JsonResponse({"message": "Welcome to admin dashboard"})


# Example of generating a token with time and role constraints
def create_limited_access_token(user):
    return generate_enhanced_token(
        user, roles=["employee"], access_start="09:00", access_end="17:00"
    )


class TimeBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.role_time_restrictions = {
            "User": {
                "start_time": timezone.datetime.strptime("20:00", "%H:%M").time(),
                "end_time": timezone.datetime.strptime("23:59", "%H:%M").time(),
            },
            # Add more roles with specific time restrictions
        }

    def __call__(self, request):
        # Skip time check for public routes
        public_routes = [
            "/account/register/",
            "/admin/",
            "/account/login/",
            "/account/logout/",
            "/base/tasks/",
            "/base/tasks/<int:pk>/delete/",
            "/base/projects/<int:pk>/",
            "/account/verify_signup_email/",
        ]
        if any(request.path.startswith(route) for route in public_routes):
            return self.get_response(request)

        # Extract username and password from the request body
        if request.body:
            try:
                request_data = json.loads(request.body)  # Parse JSON body
                username = request_data.get(
                    "username"
                )  # Get username from the parsed JSON
                print(username, "usernameusernameusername")
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON body."}, status=400)
        else:
            return JsonResponse({"error": "Request body is empty."}, status=400)

        if not username:
            return JsonResponse(
                {"error": "Username not provided in the request."}, status=400
            )

        try:
            # Retrieve the user by username
            user = User.objects.get(
                username=username
            )  # Assuming username is stored in the 'username' field of User model
            user_role = (
                user.role
            )  # Assuming role is stored in the 'role' field of User model
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User with this username not found."}, status=404
            )

        current_time = timezone.localtime().time()

        # Check time-based access for the user's role
        if user_role in self.role_time_restrictions:
            role_times = self.role_time_restrictions[user_role]

            # Check if current time is within allowed window
            if not (role_times["start_time"] <= current_time <= role_times["end_time"]):
                return JsonResponse(
                    {
                        "error": f"Access denied. {user_role} role is only allowed "
                        f"from {role_times['start_time']} to {role_times['end_time']}",
                        "allowed_start": str(role_times["start_time"]),
                        "allowed_end": str(role_times["end_time"]),
                    },
                    status=403,
                )

        return self.get_response(request)


# Decorator for additional time-based access control
def time_restricted_access(view_func):
    @functools.wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        current_time = timezone.localtime().time()

        # Example: Additional view-specific time restriction
        view_start_time = timezone.datetime.strptime("1:00", "%H:%M").time()
        view_end_time = timezone.datetime.strptime("24:00", "%H:%M").time()

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


# Example usage in views
@time_restricted_access
@require_roles("User")
def user_dashboard(request):
    return JsonResponse({"message": "User dashboard accessible"})
