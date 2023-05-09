from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.fields import CharField
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from drf_spectacular.utils import extend_schema, inline_serializer

from friend_list_service.serializers import *

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
