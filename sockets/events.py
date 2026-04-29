from flask_socketio import join_room,emit
from app.models.location_model import upsert_location

def register_socket_events(socketio):

    @socketio.on("join_group")
    def join(data):
        join_room(data["group_id"])

    @socketio.on("send_location")
    def location(data):
        upsert_location(data)
        emit("receive_location",data,room=data["group_id"])