from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": { "type": "string", "example": "antonio" },
                "password": { "type": "string", "example": "testpass" }
            },
            "required": ["username", "password"]
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": { "type": "string", "example": "User created successfully" }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": { "type": "string", "example": "Username already exists" }
            }
        }
    },
    description="Registra un nuevo usuario. No requiere autenticación."
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
