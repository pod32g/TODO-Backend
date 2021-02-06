from utils.utils import BaseView
from django.http import JsonResponse
from mainapp.models import Todo
from utils.responses import SERVER_ERROR, BAD_REQUEST
from datetime import datetime
import json
# Create your views here.


class MainApp(BaseView):
    login_required = True
    data_required = True
    fields_required = [
        'content',
        'title'
    ]

    def post(self, request, data, user, *args, **kwargs):
        try:
            todo = Todo.objects.create(title=data['title'], content=data['content'],
                                       status="todo", author=user)

            resp = {
                "id": todo.id,
                "title": todo.title,
                "content": todo.content,
                "date": todo.timestamp.strftime('%m/%d/%Y'),
                "status": todo.status
            }

            return JsonResponse(resp, status=200)

        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)

    def get(self, *args, **kwargs):
        try:
            todos = Todo.objects.filter(author=kwargs['user'])

            todos = [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "content": todo.content,
                    "date": todo.timestamp.strftime('%m/%d/%Y'),
                    "status": todo.status
                }
                for todo in todos
            ]

            return JsonResponse({
                "todos": todos
            }, status=200)

        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)

    def put(self, request, data, *args, **kwargs):
        try:
            aux = {
                **data,
                "timestamp": datetime.strptime(data['date'], '%m/%d/%Y')
            }
            aux.pop('date', None)

            todo = Todo.objects.filter(id=data['id'])

            if len(todo) == 0:
                return JsonResponse(BAD_REQUEST, status=400)

            todo = todo.update(**aux)

            todo = Todo.objects.filter(id=data['id'])[0]

            resp = {
                "id": todo.id,
                "title": todo.title,
                "content": todo.content,
                "date": todo.timestamp.strftime('%m/%d/%Y'),
                "status": todo.status
            }

            return JsonResponse(resp, status=200)

        except Exception as e:
            print(e)
            return JsonResponse(SERVER_ERROR, status=500)
