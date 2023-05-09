from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from friend_list_service.models import *
from uuid import uuid4


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


class TestFriendshipRequests(APITestCase):

    def setUp(self):
        self.user_id_1 = User.objects.create(username='Dummy1').id
        self.user_id_2 = User.objects.create(username='Dummy2').id
        self.user_id_3 = User.objects.create(username='Dummy3').id
        self.user_id_4 = User.objects.create(username='Dummy4').id # friend of Dummy1
        self.user_id_5 = User.objects.create(username='Dummy5').id

        User.objects.get(pk=self.user_id_1).friend_list.add(User.objects.get(pk=self.user_id_4))


    def send_friend_request(self, from_user, to_user):
        url = reverse('send-friend-request')
        body = {
            'from_user': from_user,
            'to_user': to_user
        }
        response = self.client.post(url, body)
        return response
        
    def test_send_friend_request(self):
        # Send friend request
        response = self.send_friend_request(self.user_id_1, self.user_id_2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Repeating request
        response = self.send_friend_request(self.user_id_1, self.user_id_2)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # User fields are equal
        response = self.send_friend_request(self.user_id_1, self.user_id_1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test auto-accept same friend request
        response = self.send_friend_request(self.user_id_2, self.user_id_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": f"The same request already existed and was successfully accepted."})

        # Test sending request to a friend
        response = self.send_friend_request(self.user_id_1, self.user_id_2)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Invalid
        response = self.send_friend_request(uuid4(), uuid4())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.send_friend_request('invalid', 'invalid')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_or_reject_friend_request(self):
        url = reverse('send-friend-request')
        friend_requests = []
        response = self.send_friend_request(self.user_id_1, self.user_id_2)
        friend_requests.append(response.data['id'])

        response = self.send_friend_request(self.user_id_1, self.user_id_3)
        friend_requests.append(response.data['id'])

        # Test accept request
        url = reverse('accept-or-reject-friend-request', kwargs={'pk': friend_requests[0]})
        body = {'action': 'accept'}
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('request-detail', kwargs={'pk': friend_requests[0]})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test invalid parametrs passed into action field
        url = reverse('accept-or-reject-friend-request', kwargs={'pk': friend_requests[1]})
        body['action'] = 'invalid'
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        body['action'] = ''
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test reject friend request
        body['action'] = 'reject'
        response = self.client.post(url, body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('request-detail', kwargs={'pk': friend_requests[1]})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
