from utils.utils import BaseView, generate_token
from utils.responses import SERVER_ERROR, WRONG_USERNAME_PASSWORD, ALL_OK
from django.http import JsonResponse
from django.contrib.auth import authenticate, get_user_model, login, logout

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
            print('here')
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)


class Logout(BaseView):
    login_required = True

    def post(self, request, user, *args, **kwargs):
        try:
            logout(request)
        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)

        return JsonResponse(ALL_OK)
