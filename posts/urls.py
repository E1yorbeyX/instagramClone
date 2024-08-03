from django.urls import path
from posts.views import PostListView, PostCreateView, PostRetrieveUpdateDestroyAPIView, CommetListAPIView, CommetCreateAPIView, \
    PostLikeListView, CommetRetrieveAPIView, CommetLikeListView, LikeListView, CommetLikeCreateView, CommetLikeDestroyView, PostLikeView, CommetLikeView


urlpatterns = [
    path('', PostListView.as_view(), name='posts_list'),
    path('post_create/', PostCreateView.as_view(), name='post_create'),
    path('post_rud/<uuid:pk>/', PostRetrieveUpdateDestroyAPIView.as_view(), name='post_rud'),
    path('<uuid:pk>/commets/', CommetListAPIView.as_view(), name='commets'),
    path('commets/create/', CommetCreateAPIView.as_view(), name='commet_create'),
    path('<uuid:pk>/likes/', PostLikeListView.as_view(), name='post_likes'),
    path('commet/<uuid:pk>/likes/', CommetLikeListView.as_view(), name='commet_likes'),
    path('commet/<uuid:pk>/', CommetRetrieveAPIView.as_view(), name='commet_detial'),
    path('likes/', LikeListView.as_view(), name='commets_likes'),
    path('to/<uuid:pk>/like/', CommetLikeCreateView.as_view(), name='to_like'),
    path('from/<uuid:pk>/delete/like/', CommetLikeDestroyView.as_view(), name='delete_like'),
    path('<uuid:pk>/post/like', PostLikeView.as_view(), name='post_like'),
    path('<uuid:pk>/commet/like', CommetLikeView.as_view(), name='commet_like')
]