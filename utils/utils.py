from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from datetime import timedelta, datetime
from jwt.exceptions import DecodeError
import json
import jwt

from utils.responses import MISSING_PARAMETERS, INVALID_CREDENTIALS, BAD_REQUEST, SERVER_ERROR, WRONG_CONTENT_TYPE

JWT_KEY = "ftpetIyX4B0FklTtzFM44Ix5oTmbvcNKw7eWQiFYbZD3SNDtX6"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class BaseView(View):
    body = None
    fields_required = None
    content_type = None
    login_required = False
    data_required = False

    def parse_data(self, request):

        if request.method != 'POST' and request.method != 'PUT':
            return None

        if not self.data_required:
            return None

        try:
            if self.body is None:
                data = json.loads(request.body.decode('utf8'))
            else:
                data = json.loads(request.POST.get(self.body))

            if data is None:
                return JsonResponse(MISSING_PARAMETERS, status=422)

        except json.decoder.JSONDecodeError:
            return JsonResponse(BAD_REQUEST, status=400)

        if self.fields_required is not None and not all(field in data for field in self.fields_required):
            return JsonResponse(MISSING_PARAMETERS, status=422)

        return data

    def get_user(self, request):
        if not self.login_required:
            return None

        if 'HTTP_AUTHORIZATION' in request.META:
            header = request.META.get('HTTP_AUTHORIZATION')
        else:
            return JsonResponse(INVALID_CREDENTIALS, status=403)

        fields = header.split(' ')
        if len(fields) == 2 and fields[0] == 'Bearer':
            token = fields[1]

        try:
            credentials = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
        except DecodeError as e:
            print(e)
            return JsonResponse(BAD_REQUEST, status=400)
        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)

        if credentials is None:
            return JsonResponse(INVALID_CREDENTIALS, status=403)

        now = datetime.now()
        generated = datetime.strptime(
            credentials['generation'].split(".")[0], TIME_FORMAT)
        expires = datetime.strptime(
            credentials['expiration'].split(".")[0], TIME_FORMAT)

        if generated is None or expires is None:
            return JsonResponse(INVALID_CREDENTIALS, status=403)

        if not (generated < now < expires):
            return JsonResponse(INVALID_CREDENTIALS, status=403)

        if request.session.session_key is None:
            request.session._set_session_key(credentials['id'])

        valid_key = request.session._validate_session_key(
            request.session.session_key
        )
        session = request.session._get_session()

        try:
            user = User.objects.get(username=credentials['username'])
        except User.DoesNotExist as e:
            print(e)
            return JsonResponse(INVALID_CREDENTIALS, status=403)

        if valid_key and len(session.keys()) > 0:
            return user

        return JsonResponse(INVALID_CREDENTIALS, status=403)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if self.content_type is not None and request.content_type != self.content_type:
            return JsonResponse(WRONG_CONTENT_TYPE, status=415)

        data = self.parse_data(request)
        if isinstance(data, JsonResponse):
            return data

        user = self.get_user(request)
        if isinstance(user, JsonResponse):
            return user
        return super().dispatch(request, data=data, user=user, *args, **kwargs)


def generate_token(request, username):
    now = datetime.now()

    expiration = now + timedelta(hours=6)

    payload = {
        "id": request.session.session_key,
        "username": username,
        'generation': str(now),
        'expiration': str(expiration),
    }

    return jwt.encode(payload, JWT_KEY, algorithm='HS256')
