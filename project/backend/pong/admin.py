from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
	list_display = ('id', 'is_full', 'max_players', 'created_at')
	filter_horizontal = ('players',)
