from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
import json
# Create your tests here.


class AuthTest(TestCase):

    def setUp(self):
        self.c = Client()
        User.objects.create_user(
            username="test", email="test@test.com", password="test")

    def test_login(self):

        response = self.c.post('/api/authentication/login',
                               {"username": "test", "password": "test"}, content_type='application/json')

        self.assertEquals(response.status_code, 200)

        body = json.loads(response.content)

        assert 'token' in body
        assert 'user' in body
        assert 'session_key' in body

    def test_login_fail(self):
        response = self.c.post('/api/authentication/login',
                               {"username": "test", "password": "wrongpassword"}, content_type='application/json')

        self.assertEquals(response.status_code, 401)

        body = json.loads(response.content)

        assert 'error' in body
        assert 'code' in body

    def test_logout(self):
        login = self.c.post('/api/authentication/login',
                            {"username": "test", "password": "test"}, content_type='application/json')

        self.assertEquals(login.status_code, 200)

        body = json.loads(login.content)

        logout = self.c.post('/api/authentication/logout',
                             HTTP_AUTHORIZATION='Bearer ' + body['token'])

        self.assertEquals(logout.status_code, 200)

        body = json.loads(logout.content)

        assert 'status' in body
        assert 'code' in body

    def test_logout_fail(self):
        logout = self.c.post('/api/authentication/logout')

        self.assertEquals(logout.status_code, 403)

        body = json.loads(logout.content)

        assert 'error' in body
        assert 'code' in body
