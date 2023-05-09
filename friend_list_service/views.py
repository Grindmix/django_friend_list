from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.fields import CharField
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, GenericAPIView
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter

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


class UserFriendlistOnlyView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserFriendListSerializer


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
    

class AllFriendRequstsListView(ListAPIView):
    queryset = Requests.objects.all()
    serializer_class = RequestsHyperlinkSerializer


class FriendRequestDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Requests.objects.all()
    serializer_class = RequestsModelSerializer


class AcceptOrRejectFriendRequestView(GenericAPIView):
    queryset = Requests.objects.all()
    serializer_class = AcceptOrRejectSerializer

    VALID = ['accept', 'reject']

    def post(self, request, *args, **kwargs):
        friend_request_object = self.get_object()
        if 'action' not in request.data or not isinstance(request.data['action'], str):
            return Response({'message': 'Request body must contain action field'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.data['action'].lower() in self.VALID:
            return Response({'message': '"action" must be: accept or reject'}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data['action'].lower() == 'accept':
            user_list = accept_friend_request(friend_request_object)
            return Response({'message': f'{user_list[0].data["username"]} and {user_list[1].data["username"]} are now friends!'})
        
        friend_request_object.delete()
        return Response({"message": "Friend request has been rejected and deleted"})
    

class DeleteFriendFromFriendlistView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UUIDFieldRequestSerializer

    @extend_schema(request=UUIDFieldRequestSerializer)
    def put(self, request, pk, *args, **kwargs):
        if 'user_id' not in request.data or not isinstance(request.data['user_id'], str):
            return Response({'message': 'Request body must contain user_id field'},status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object()
        try:
            friend_to_delete = self.queryset.get(pk=request.data['user_id'])
            if user.friend_list.filter(pk=friend_to_delete.id).exists():
                user.friend_list.remove(friend_to_delete)
                return Response({'message': f'{pk} and {friend_to_delete.id} no longer friends :('}, status=status.HTTP_200_OK)
            else:
                return Response({'message': f'{pk} and {friend_to_delete.id} not even friends right now.'}, status=status.HTTP_409_CONFLICT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserFriendRequestsView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = RequestsHyperlinkSerializer

    VALID = ['incoming_requests', 'outcoming_requests']

    @extend_schema(parameters=[OpenApiParameter('filter', required=False, enum=VALID)])
    def get(self, request, *args, **kwargs):
        user_object = self.get_object()
        query_param_filter = request.query_params.get('filter')
        serializer_context = {'request': request,}
        if query_param_filter not in self.VALID and query_param_filter != None:
            return Response({"message": f"filter query parameter not valid (your is: {query_param_filter})"}, status=status.HTTP_400_BAD_REQUEST)
        
        if query_param_filter == None:
            filter_result = user_object.incoming_requests.all() | user_object.outcoming_requests.all()

        elif query_param_filter == self.VALID[0]:
            filter_result = user_object.incoming_requests.all()

        elif query_param_filter == self.VALID[1]:
            filter_result = user_object.outcoming_requests.all()

        serializer = self.serializer_class(filter_result, many=True, context=serializer_context)
        if serializer.data == []:
            if query_param_filter == None:
                query_param_filter = 'any friend requests'
            return Response({"message": f"This user doesn't have {query_param_filter}."})
        return Response(data=serializer.data)
