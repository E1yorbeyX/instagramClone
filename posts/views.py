from django.shortcuts import render
from rest_framework import generics, permissions
from shared.custom_pagination import CustomPagination
from posts.models import Post, PostLike, PostCommet, CommetLike
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from posts.serializers import PostSerializers, PostLikeSerializer, CommetSerializer, CommetLikeSerializer


class PostListView(generics.ListAPIView):
    serializer_class = PostSerializers
    permission_classes = [permissions.AllowAny, ]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()

class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializers
    permission_classes = [permissions.IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializers
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

        return Response(
            {
                "success":True,
                "status_code":status.HTTP_202_ACCEPTED,
                "message":"Ish tugatildi",
                "data": serializer.data
            }
        )  

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        
        return Response(
            {
                "success":True,
                "status_code":status.HTTP_204_NO_CONTENT,
                "message":"Ish tugatildi"
            }
        )


class CommetListAPIView(generics.ListAPIView):
    serializer_class = CommetSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        queryset = PostCommet.objects.filter(post__id=post_id)
        return queryset


class CommetCreateAPIView(generics.CreateAPIView):
    serializer_class = CommetSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    # def perform_create(self, serializer):
    #     post_id = self.kwargs['pk']
    #     post = Post.objects.get(id=post_id)
    #     serializer.save(author=self.request.user, post=post)
    
    def perform_create(self, serializer):
       serializer.save(author=self.request.user)
       

class PostLikeListView(generics.ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
       post_id = self.kwargs['pk']
       return PostLike.objects.filter(post_id=post_id)
   
class CommetRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = CommetSerializer
    permission_classes = [permissions.AllowAny, ]
    queryset = PostCommet.objects.all()

class CommetLikeListView(generics.ListAPIView):
    serializer_class = CommetLikeSerializer
    permission_classes = [permissions.AllowAny, ]
    
    def get_queryset(self):
        commet_id = self.kwargs['pk']
        return CommetLike.objects.filter(commet_id=commet_id)
    
class LikeListView(generics.ListAPIView):
    serializer_class = CommetLikeSerializer
    permission_classes = [permissions.AllowAny, ]
    queryset = CommetLike.objects.all()
    pagination_class = CustomPagination
    
class CommetLikeCreateView(generics.CreateAPIView):
    serializer_class = CommetLikeSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
class CommetLikeDestroyView(generics.DestroyAPIView):
    serializer_class = CommetLikeSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    queryset = PostCommet.objects.all()

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        commet_id = self.kwargs['pk']
        try:
            punlike = CommetLike.objects.get(author=user, commet_id=commet_id)
        except:
            return Response(
                {
                    "success":False,
                    "message":"Bu obect allaqachon o'chirilgan yoki yaratilmagan"
                }
            )                  
        punlike.delete()
        return Response(
            {
                "success":True
            }
        )

# class PostLikeView(APIView):
#     def post(self, request, pk):
#         try:
#             post_like = PostLike.objects.create(
#                 author=self.request.user,
#                 post_id=pk
#             )
#             serializer = PostLikeSerializer(post_like)
#             data = {
#                 "success":True,
#                 "message":"Successfully created post like",
#                 "data":serializer.data
#             }
#             return Response(
#                 data, 
#                 status=status.HTTP_201_CREATED
#             )
#         except Exception as e:
#             data = {
#                 "success":True,
#                 "message":f"{str(e)}"
#             }
#             return Response(data, status=status.HTTP_400_BAD_REQUEST)
#     def delete(self, request, pk):
#         try:
#             post_like = PostLike.objects.get(
#                 author=self.request.user,
#                 post_id = pk
#             )
#             post_like.delete()
#             data = {
#                 "success":True,
#                 "message":"Successfully post like deleted",
#             }
#             return Response(
#                 data,
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         except Exception as e:
#             data = {
#                 "success":False,
#                 "message":f"{str(e)}",
#             }
#             return Response(data, status=status.HTTP_400_BAD_REQUEST)


# class CommetLikeView(APIView):
#     def post(self, request, pk):
#         try:
#             commet_like = CommetLike.objects.create(
#                 author=self.request.user,
#                 commet_id=pk
#             )
#             serializer = CommetLikeSerializer(commet_like)
#             data = {
#                 "success":True,
#                 "message":"Successfully created commet like",
#                 "data":serializer.data
#             }
#             return Response(data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             data = {
#                 "success":False,
#                 "message":f"{str(e)}"
#             }
#             return Response(data, status=status.HTTP_400_BAD_REQUEST)
#     def delete(self, request, pk):
#         try:
#             commet_like = CommetLike.objects.get(
#                 author=self.request.user,
#                 commet_id=pk
#             )
#             commet_like.delete()
#             data = {
#                 "success":True,
#                 "message":"Successfully deleted commet like"
#             }
#             return Response(
#                 data,
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         except Exception as e:
#             data = {
#                 "success":False,
#                 "message":f"{str(e)}"
#             }
#             return Response(
#                 data,
#                 status=status.HTTP_400_BAD_REQUEST
#             )

class PostLikeView(APIView):
    def post(self, request, pk):
        try:
            postLike = PostLike.objects.get(
                author=self.request.user,
                post_id=pk
            )
            postLike.delete()
            data = {
                "success":True,
                "message":"Successfully deleted post like"
            }
            return Response(
                data,
                status=status.HTTP_204_NO_CONTENT
            )
        except PostLike.DoesNotExist:
            postLike = PostLike.objects.create(
                author=self.request.user,
                post_id=pk
            )
            serializer = PostLikeSerializer(postLike)
            data = {
                "success":True,
                "message":"Successfully created post like",
                "data":serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)

class CommetLikeView(APIView):
    def post(self, request, pk):
        try:
            commetLike = CommetLike.objects.get(
                author=self.request.user,
                commet_id=pk
            )
            commetLike.delete()
            data = {
                "success":True,
                "message":"Successfully deleted commet like"
            }
            return Response(
                data,
                status=status.HTTP_204_NO_CONTENT
            )
        except CommetLike.DoesNotExist:
            commetLike = CommetLike.objects.create(
                author=self.request.user,
                commet_id=pk
            )
            serializer = CommetLikeSerializer(commetLike)
            data = {
                "success":True,
                "message":"Successfully created commet like",
                "data":serializer.data
            }
            return Response(data, status=status.HTTP_201_CREATED)
