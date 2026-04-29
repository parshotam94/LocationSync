const socket = io();

socket.emit("join_group",{group_id:GROUP_ID});

socket.on("receive_location",(data)=>{
    updateMarker(data);
});