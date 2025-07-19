import pytest
import os
from django.contrib.auth.models import User
from oauth2_provider.models import Application
from rest_framework.test import APIClient

CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
CLIENT_ID = os.environ.get('CLIENT_ID')

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    user = User.objects.create_user(username='antonio', password='testpass')
    user.is_active = True
    user.save()
    return user

@pytest.fixture
def other_user():
    return User.objects.create_user(username='otro', password='testpass')

@pytest.fixture
def oauth_app(user):
    app, _ = Application.objects.get_or_create(
        name="CactusApp",
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_PASSWORD,
        user=user,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    print(app.client_id, app.client_secret, app.user)
    return app

@pytest.fixture
def token(client, user, oauth_app):
    print(oauth_app)
    response = client.post('/o/token/', data={
        'grant_type': 'password',
        'username': user.username,
        'password': 'testpass',
        'client_id': oauth_app.client_id,
        'client_secret': CLIENT_SECRET,
    })
    data = response.json()
    assert 'access_token' in data, f"OAuth2 error: {data}"
    return data['access_token']

@pytest.fixture
def auth_client(client, token):
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.mark.django_db
def test_register_user(client):
    response = client.post('/api/register/', data={'username': 'nuevo', 'password': '1234'})
    assert response.status_code == 201

@pytest.mark.django_db
def test_login_oauth2(client, user, oauth_app):
    response = client.post('/o/token/', data={
        'grant_type': 'password',
        'username': user.username,
        'password': 'testpass',
        'client_id': oauth_app.client_id,
        'client_secret': CLIENT_SECRET,
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()

@pytest.mark.django_db
def test_create_task(auth_client):
    response = auth_client.post('/api/tasks/', data={'title': 'Test', 'description': 'Desc'})
    assert response.status_code == 201
    assert response.json()['title'] == 'Test'

@pytest.mark.django_db
def test_list_tasks(auth_client):
    auth_client.post('/api/tasks/', data={'title': 'Tarea1'})
    auth_client.post('/api/tasks/', data={'title': 'Tarea2'})
    response = auth_client.get('/api/tasks/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['title'] == 'Tarea2'  # deberia estar en orden descendente

@pytest.mark.django_db
def test_user_cannot_access_others_task(auth_client, other_user):
    from tasks.models import Task
    task = Task.objects.create(user=other_user, title='Privada')
    response = auth_client.get(f'/api/tasks/{task.id}/')
    assert response.status_code == 404

@pytest.mark.django_db
def test_invalid_token_rejected(client):
    client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
    response = client.get('/api/tasks/')
    assert response.status_code == 401

@pytest.mark.django_db
def test_update_task(auth_client):
    response = auth_client.post('/api/tasks/', data={'title': 'Original'})
    task_id = response.json()['id']
    update = auth_client.put(f'/api/tasks/{task_id}/', data={'title': 'Modificada'})
    assert update.status_code == 200
    assert update.json()['title'] == 'Modificada'

@pytest.mark.django_db
def test_delete_task(auth_client):
    response = auth_client.post('/api/tasks/', data={'title': 'Eliminar'})
    task_id = response.json()['id']
    delete = auth_client.delete(f'/api/tasks/{task_id}/')
    assert delete.status_code == 204
