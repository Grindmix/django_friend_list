from friend_list_service.serializers import UserModelSerializer

def accept_friend_request(friend_request_object):
    serializer = UserModelSerializer
    user_one = friend_request_object.from_user
    user_two = friend_request_object.to_user
    user_one.friend_list.add(user_two)
    user_one.save()
    user_list = []
    user_list.append(serializer(user_one))
    user_list.append(serializer(user_two))
    friend_request_object.delete()
    return user_list