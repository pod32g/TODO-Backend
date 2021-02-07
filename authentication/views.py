from utils.utils import BaseView, generate_token
from utils.responses import SERVER_ERROR, WRONG_USERNAME_PASSWORD, ALL_OK, BAD_REQUEST
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# Create your views here.


class Login(BaseView):
    content_type = "application/json"
    data_required = True
    fields_required = [
        'username',
        'password'
    ]

    def post(self, request, data, *args, **kwargs):
        try:
            user = authenticate(
                request=request,
                username=data['username'],
                password=data['password']
            )

            if user is not None:
                login(request, user)

                if not request.session.exists(request.session.session_key):
                    request.session.create()

                response = {
                    "token": generate_token(request, data['username']),
                    "user": data['username'],
                    "session_key": request.session.session_key
                }

                return JsonResponse(response, status=200)

            else:
                return JsonResponse(WRONG_USERNAME_PASSWORD, status=401)

        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)


class SignUp(BaseView):
    login_required = False
    data_required = True
    fields_required = [
        'username',
        'email',
        'password'
    ]

    def post(self, request, data, *args, **kwargs):
        try:
            User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )

            user = authenticate(
                request=request,
                username=data['username'],
                password=data['password']
            )

            if user is not None:
                login(request, user)

                if not request.session.exists(request.session.session_key):
                    request.session.create()

                response = {
                    "token": generate_token(request, data['username']),
                    "user": data['username'],
                    "session_key": request.session.session_key
                }

                return JsonResponse(response, status=200)
            return JsonResponse(BAD_REQUEST, status=400)

        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)


class Logout(BaseView):
    login_required = True

    def get(self, request, *args, **kwargs):
        try:
            logout(request)
        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)

        return JsonResponse(ALL_OK)
