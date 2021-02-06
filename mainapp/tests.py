from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
import json
# Create your tests here.


class TodoTest(TestCase):

    def setUp(self):
        self.c = Client()
        User.objects.create_user(
            username="test", email="test@test.com", password="test")

    def get_token(self):
        login = self.c.post('/api/authentication/login',
                            {"username": "test", "password": "test"}, content_type='application/json')

        self.assertEquals(login.status_code, 200)

        return json.loads(login.content)['token']

    def test_new_todo(self):
        response = self.c.post('/api/todo/', {
            "title": "test",
            "content": "test"
        }, content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.get_token())

        self.assertEquals(response.status_code, 200)

        body = json.loads(response.content)

        assert 'id' in body
        assert 'title' in body
        assert 'content' in body
        assert 'date' in body
        assert 'status' in body

    def test_new_todo_unauthorized(self):
        response = self.c.post('/api/todo/', {
            "title": "test",
            "content": "test"
        }, content_type='application/json')

        self.assertEquals(response.status_code, 403)

        body = json.loads(response.content)

        assert 'error' in body
        assert 'code' in body

    def test_get_todos(self):
        post = self.c.post('/api/todo/', {
            "title": "test",
            "content": "test"
        }, content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.get_token())

        self.assertEquals(post.status_code, 200)

        response = self.c.get(
            '/api/todo/', HTTP_AUTHORIZATION='Bearer ' + self.get_token())

        self.assertEquals(response.status_code, 200)

        body = json.loads(response.content)

        assert 'todos' in body
        assert 'id' in body['todos'][0]
        assert 'title' in body['todos'][0]
        assert 'content' in body['todos'][0]
        assert 'date' in body['todos'][0]
        assert 'status' in body['todos'][0]

    def test_get_todos_unauthorized(self):
        response = self.c.get('/api/todo/')

        self.assertEquals(response.status_code, 403)

        body = json.loads(response.content)

        assert 'error' in body
        assert 'code' in body

    def test_modify_todo(self):
        post = self.c.post('/api/todo/', {
            "title": "test",
            "content": "test"
        }, content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + self.get_token())

        self.assertEquals(post.status_code, 200)

        body = json.loads(post.content)

        body['title'] = 'test2'

        post = self.c.put('/api/todo/', json.dumps(body), content_type='application/json',
                          HTTP_AUTHORIZATION='Bearer ' + self.get_token())

        body = json.loads(post.content)

        self.assertEquals(post.status_code, 200)

        assert 'id' in body
        assert 'title' in body
        assert 'content' in body
        assert 'date' in body
        assert 'status' in body

        self.assertEquals(body['title'], 'test2')

    def test_modify_todo_fail(self):
        response = self.c.put('/api/todo/', {}, content_type='application/json',
                              HTTP_AUTHORIZATION='Bearer ' + self.get_token())

        self.assertEquals(response.status_code, 422)

        body = json.loads(response.content)

        assert 'error' in body
        assert 'code' in body
