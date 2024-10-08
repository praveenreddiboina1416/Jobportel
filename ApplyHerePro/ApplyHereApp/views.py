

# Create your views here.
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer , LogoutSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .password_reset_file import reset_password
from .send_otp_logic import sendOtp
from rest_framework.decorators import api_view


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
# Create your views here.
class userregistration(APIView):
    
    def post(self, request, formate=None):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            Tokens=get_tokens_for_user(user)
            return Response({'Tokens' :Tokens, 'msg': 'Registration successfull'}, status =status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class userlogin(APIView):
    def post(self, request, formate=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email = email, password=password)
            if user is not None:
                Tokens=get_tokens_for_user(user)
                return Response({'Tokens' :Tokens, 'msg': 'login successfull'}, status =status.HTTP_200_OK)
            else:
                return Response({'msg': ['email or password is not valid']},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     
    
class profileview(APIView):
    Permission_classes = [IsAuthenticated]
    def get(self,request,  formate=None):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
    
    
class userlogout(APIView):       #here we have to pass access token 
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



@csrf_exempt
@api_view(['POST'])
def send_otp(request):
    email = (json.loads(request.body))['email']
    # email = request.POST["email"]
    
    resp = sendOtp(email)
    return JsonResponse({"message": "OTP sent successfully","status":resp.status_code}, status=status.HTTP_200_OK)

@api_view(['POST'])
def confirm_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    cached_otp = cache.get(email)
    if cached_otp is None or cached_otp != otp:
        return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')

    result = reset_password(email, password, confirm_password)  
    return result 
