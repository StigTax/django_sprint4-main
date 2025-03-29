from django.contrib import admin

from .models import Category, Location, Post


class PostInLine(admin.StackedInline):
    model = Post
    extra = 0
    fields = ('title', 'is_published', 'pub_date', 'category')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = (PostInLine,)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'is_published',
        'created_at',
        'author',
        'location',
        'category',
    )
    list_editable = (
        'is_published',
        'category'
    )
    list_editable = ('is_published', 'category')
    search_fields = ('title', 'text')
    list_filter = ('category', 'pub_date', 'author')
    list_display_links = ('title',)
    date_hierarchy = 'pub_date'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
