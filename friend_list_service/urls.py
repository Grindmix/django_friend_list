from django.urls import path
from friend_list_service import views

urlpatterns = [
    path('', views.api_root),
    path('register/', views.UserCreateView.as_view(), name='user-create'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/username/<username>/', views.UserDetailByUsernameView.as_view(), name='user-detail-by-username'),
    path('send_friend_request/', views.SendFriendRequestView.as_view(), name='send-friend-request'),
    path('request_detail/<pk>/', views.FriendRequestDetailView.as_view(), name='requests-detail'),
    path('accept_or_reject_request/<pk>/', views.AcceptOrRejectFriendRequestView.as_view(), name='accept-or-reject-friend-request'),
    path('list_friend_requests/all/', views.AllFriendRequstsListView.as_view(), name='list-requests'),
    path('list_friend_requests/user/<pk>/', views.UserFriendRequestsView.as_view(), name='list-user-friend-requests'),
    path('delete_friend/<pk>/', views.DeleteFriendFromFriendlistView.as_view(), name='delete-friend'),
]
