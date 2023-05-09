from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from friend_list_service.models import *


class TestUserCreate(APITestCase):
    def test_create_user_accout(self):
        url = reverse('user-create')
        username = 'Dummy1'
        body = {
            'username': username
        }
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username=username).username, username)
        response = self.client.post(url, body) # Trying to create new user with same username
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


class TestUserCRUD(APITestCase):

    default_username = 'Dummy1'

    def setUp(self):
        self.user_id = User.objects.create(username=self.default_username).id
        self.url = reverse('user-detail', kwargs={'pk': self.user_id})

    def test_get_user_detail_by_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.default_username)

    
    def test_put_user_detail_by_id(self):
        response = self.client.put(self.url, {'username': 'Changed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Changed')

    
    def test_delete_user_by_id(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
