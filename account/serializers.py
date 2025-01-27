from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from rest_framework import serializers


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator()]
    )
    username = serializers.CharField(
        required=True,
        min_length=3,
        max_length=50
    )
    role = serializers.ChoiceField(
        choices=['User', 'Admin', 'Manager'],
        default='User'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def validate(self, data):
        # Additional custom validations
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already in use"})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'User')
        )
        send_mail(
            'Verify your account',
            'Click the link to verify your account: <verification-link>',
            'admin@example.com',
            [user.email],
            fail_silently=False,
        )
        return user