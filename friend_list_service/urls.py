from django.urls import path
from friend_list_service import views

urlpatterns = [
    path('', views.api_root),
    path('register/', views.UserCreateView.as_view(), name='user-create'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/username/<username>/', views.UserDetailByUsernameView.as_view(), name='user-detail-by-username'),
    path('send_friend_request/', views.SendFriendRequestView.as_view(), name='send-friend-request'),
]
