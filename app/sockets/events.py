from flask_socketio import join_room, emit
from app.models.location_model import insert_location, get_locations_for_group
from flask import request

def register_socket_events(socketio):

    @socketio.on("join_group")
    def join(data):
        group_id = data["group_id"]
        join_room(group_id)
        # Send location history to the user who just joined
        history = get_locations_for_group(group_id)
        emit("location_history", history, to=request.sid)

    @socketio.on("send_location")
    def location(data):
        insert_location(data)
        emit("receive_location", data, room=data["group_id"])
        
    @socketio.on("ride_started")
    def handle_ride_started(data):
        emit("ride_started", data, room=data["group_id"])
        
    @socketio.on("ride_ended")
    def handle_ride_ended(data):
        emit("ride_ended", data, room=data["group_id"])