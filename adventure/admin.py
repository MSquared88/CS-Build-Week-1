from django.contrib import admin
from .models import *

class RoomAdmin(admin.ModelAdmin):
    pass

class ItemAdmin(admin.ModelAdmin):
    pass

class ItemInstanceAdmin(admin.ModelAdmin):
    pass

class InventoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Room, RoomAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemInstance, ItemInstanceAdmin)
admin.site.register(Inventory, InventoryAdmin)