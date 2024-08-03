from rest_framework import serializers
from posts.models import Post, PostCommet, PostLike, CommetLike
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'image')

class PostSerializers(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    post_likes_counts = serializers.SerializerMethodField('get_post_likes_counts')
    post_commit_counts = serializers.SerializerMethodField('get_post_commit_counts')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Post
        fields = (
            'id',
            'author', 
            'image', 
            'caption', 
            'created_at', 
            'me_liked',
            'post_likes_counts',
            'post_commit_counts'
        )
        extra_kwargs = {'image':{'required':False}}
        
    def get_post_likes_counts(self, obj):
        return obj.postlike.count()
    
    def get_post_commit_counts(self, obj):
        return obj.postcommit.count()

    def get_me_liked(self, obj):
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            try:
                like = PostLike.objects.get(post=obj, author=request.user)
                return  True
            except PostLike.DoesNotExist:
                return False
        return False

class CommetSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField('get_replies')
    me_liked = serializers.SerializerMethodField('get_me_liked')
    commet_likes = serializers.SerializerMethodField('get_commet_likes_count')

    class Meta:
        model = PostCommet
        fields = (
            'id',
            'author',
            'post',
            'commet',
            'parent',
            'replies',
            'me_liked',
            'commet_likes'
        )
    
    def get_replies(self, obj):
        if obj.child.exists():
            serializer = self.__class__(obj.child.all(), many=True, context=self.context)
            return serializer.data
        else:
            return None
        
    def get_me_liked(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return obj.commitlike.filter(author=user).exists()
        else:
            return False
    
    def get_commet_likes_count(self, obj):
        return obj.commitlike.count()


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ['id', 'author', 'post']


class CommetLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = CommetLike
        fields = ['id', 'author', 'commet']