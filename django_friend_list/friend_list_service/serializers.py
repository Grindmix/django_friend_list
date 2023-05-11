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


class UserFriendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'friend_list')


class RequestsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = ('id', 'from_user', 'to_user')


class RequestsHyperlinkSerializer(serializers.HyperlinkedModelSerializer):
    accept_or_reject = serializers.HyperlinkedIdentityField(view_name='accept-or-reject-friend-request', read_only=True)

    class Meta:
        model = Requests
        fields = ('url', 'id', 'from_user', 'to_user', 'accept_or_reject')


class AcceptOrRejectSerializer(serializers.Serializer):
    
    choices = {'accept': 'accept', 'reject': 'reject'}
    action = serializers.ChoiceField(choices=choices)


class UUIDFieldRequestSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()