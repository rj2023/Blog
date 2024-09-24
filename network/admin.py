from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Post)
admin.site.register(PostInteraction)
admin.site.register(Comment)
admin.site.register(CommentLike)


# Register your models here.
