from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.fields import CharField
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from drf_spectacular.utils import extend_schema, inline_serializer

from friend_list_service.serializers import *
from friend_list_service.utils import accept_friend_request


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'user-list': reverse('user-list', request=request, format=format),
        'user-create': reverse('user-create', request=request, format=format),
    })

class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserHyperlinkSerializer


class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserHyperlinkSerializer


class UserDetailByUsernameView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserHyperlinkSerializer
    lookup_field = 'username'


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserHyperlinkSerializer

    @extend_schema(request=inline_serializer('username', {'username': CharField()}))
    def post(self, request, *args, **kwargs):
        username = request.data['username']
        try:
            User.objects.get(username=username)
            return Response({"message": "This username was taken!"}, status=status.HTTP_409_CONFLICT)
        except User.DoesNotExist:
            return self.create(request, *args, **kwargs)
        

class SendFriendRequestView(CreateAPIView):
    queryset = Requests.objects.all()
    serializer_class = RequestsModelSerializer

    def post(self, request, *args, **kwargs):
        if not 'from_user' in request.data or not 'to_user' in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.data['from_user'] == request.data['to_user']:
            return Response({'message': 'User fields are same'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            User.objects.get(pk=request.data['from_user'])
            User.objects.get(pk=request.data['to_user'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # find_similar_request = self.queryset.filter(from_user)

            if User.objects.get(pk=request.data['from_user']).outcoming_requests.filter(to_user=request.data['to_user']).exists():
                return Response({"message": "You already sent this request"}, status.HTTP_409_CONFLICT)
            
            if User.objects.get(pk=request.data['from_user']).incoming_requests.filter(from_user=request.data['to_user']).exists():
                friend_request_object = User.objects.get(pk=request.data['from_user']).incoming_requests.filter(from_user=request.data['to_user']).first()
                accept_friend_request(friend_request_object)
                return Response({"message": f"The same request already existed and was successfully accepted."})
            
            if User.objects.filter(pk=request.data['from_user'], friend_list__id=request.data['to_user']):
                return Response({"message": f"{request.data['from_user']} and {request.data['to_user']} already friends"}, status=status.HTTP_409_CONFLICT)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)