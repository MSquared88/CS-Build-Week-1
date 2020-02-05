from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid

class Item(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class ItemInstance(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    data = models.TextField(default="{}")
    
    def __str__(self):
        return f"{str(self.item)} ({self.id})"

class Inventory(models.Model):
    items = models.ManyToManyField(ItemInstance)

class Enemy(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class EnemyInstance(models.Model):
    enemy = models.ForeignKey(Enemy, on_delete=models.CASCADE)
    attack = models.PositiveIntegerField(default=10)
    defense = models.PositiveIntegerField(default=10)
    hp = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{str(self.enemy)} ({self.id})"

class Room(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    n_to = models.ForeignKey("Room", on_delete=models.SET_NULL, blank=True, null=True, related_name="n_room")
    s_to = models.ForeignKey("Room", on_delete=models.SET_NULL, blank=True, null=True, related_name="s_room")
    e_to = models.ForeignKey("Room", on_delete=models.SET_NULL, blank=True, null=True, related_name="e_room")
    w_to = models.ForeignKey("Room", on_delete=models.SET_NULL, blank=True, null=True, related_name="w_room")
    inventory = models.OneToOneField(Inventory, on_delete=models.DO_NOTHING, blank=True, null=True)
    enemy = models.OneToOneField(EnemyInstance, on_delete=models.DO_NOTHING, blank=True, null=True)
    def connectRooms(self, destinationRoom, direction):
        destinationRoomID = destinationRoom.id
        try:
            destinationRoom = Room.objects.get(id=destinationRoomID)
        except Room.DoesNotExist:
            print("That room does not exist")
        else:
            if direction == "n":
                self.n_to = destinationRoomID
            elif direction == "s":
                self.s_to = destinationRoomID
            elif direction == "e":
                self.e_to = destinationRoomID
            elif direction == "w":
                self.w_to = destinationRoomID
            else:
                print("Invalid direction")
                return
            self.save()
    def playerNames(self, currentPlayerID):
        return [p.user.username for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]
    def playerUUIDs(self, currentPlayerID):
        return [p.uuid for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]
    def __str__(self):
        return f"{self.title} ({self.id})"

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currentRoom = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    inventory = models.OneToOneField(Inventory, on_delete=models.DO_NOTHING, null=True)
    hp = models.PositiveIntegerField(default=100)
    mp = models.PositiveIntegerField(default=100)
    def initialize(self):
        if self.currentRoom == 0:
            self.currentRoom = Room.objects.first().id
            self.save()
    def room(self):
        try:
            return Room.objects.get(id=self.currentRoom)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()





