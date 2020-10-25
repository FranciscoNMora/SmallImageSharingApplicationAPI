from django.contrib import admin, messages

# Register your models here.
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Q
from django import forms

from PostsApp.models import Profile, Post, LikeException


class ProfileFollowingForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['following']

    def __init__(self, *args, **kwargs):
        super(ProfileFollowingForm, self).__init__(*args, **kwargs)
        self.fields['following'].queryset = User.objects.exclude(Q(is_staff=True) |
                                                                 Q(pk=self.instance.user_id))


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ['following']
    form = ProfileFollowingForm


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = True
    inlines = (ProfileInline,)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('username',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('post_ref', 'author', 'caption', 'created',)
    list_filter = ('author',)
    readonly_fields = ('post_ref', 'created',)
    ordering = ('-created',)

    def save_model(self, request, obj: Post, form, change: bool):
        liked = form.cleaned_data['liked']
        author = form.cleaned_data['author']
        if author in liked:
            form.cleaned_data['liked'] = liked.exclude(id=author.id)
            messages.set_level(request, messages.ERROR)
            messages.error(request, "Author of the post can not be in 'Liked' list")
        super().save_model(request, obj, form, change)

