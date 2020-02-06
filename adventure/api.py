from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
from rest_framework import status
from django.forms.models import model_to_dict
import json
import random

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

def update(request):
    player = request.user.player
    room = player.currentRoom

    return {"title": room.title, "description": room.description}

@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.currentRoom
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name': player.user.username, 'title': room.title, 'description': room.description, 'players': players}, safe=True)


# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs = {"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.currentRoom
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to and room.n_to.id
    elif direction == "s":
        nextRoomID = room.s_to and room.s_to.id
    elif direction == "e":
        nextRoomID = room.e_to and room.e_to.id
    elif direction == "w":
        nextRoomID = room.w_to and room.w_to.id
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom = nextRoom
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name': player.user.username, 'title': nextRoom.title, 'description': nextRoom.description, 'players': players, 'error_msg': ""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name': player.user.username, 'title': room.title, 'description': room.description, 'players': players, 'error_msg': "You cannot move that way."}, safe=True)

@api_view(["POST"])
def attack(request):
    player = request.user.player
    enemy = player.currentRoom.enemy
    player_hp = player.hp # Their HP will get reset if they die.

    if enemy:
        player_should_hit = random.random() > 0.2
        enemy_should_hit = random.random() > 0.2

        if player_should_hit:
            enemy.hp -= random.randint(1, 5)
        
        if enemy_should_hit:
            player.hp -= random.randint(1, enemy.attack)

            if player.hp <= 0:
                player_hp = player.hp
                player.hp = 100
                player.currentRoom = Room.objects.first()

            player.save()
        
        if enemy.hp <= 0:
            enemy.delete()
        else:
            enemy.save()
        
        if player_hp <= 0:
            return JsonResponse({"revival_room": model_to_dict(player.currentRoom)})

        return JsonResponse({
            "player": {
                "hp": player_hp if player_hp > 0 else 0
            },
            "enemy": {
                "hp": enemy.hp if enemy.hp > 0 else 0
            }
        })

    return JsonResponse({"error": "There is no enemy in this room."})
@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error': "Not yet implemented"}, safe=True, status=500)


@csrf_exempt
@api_view(["GET"])
def rooms(request):
    data = list(Room.objects.all().values())
    return JsonResponse(data, safe=False)
