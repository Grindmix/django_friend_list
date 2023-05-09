from rest_framework import serializers
from friend_list_service.models import *

class UserHyperlinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'friend_list')

class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'friend_list')


class RequestsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = ('id', 'from_user', 'to_user')
