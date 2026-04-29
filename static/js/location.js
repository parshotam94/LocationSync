navigator.geolocation.watchPosition((pos)=>{
    socket.emit("send_location",{
        user_id:USER_ID,
        group_id:GROUP_ID,
        lat:pos.coords.latitude,
        lng:pos.coords.longitude
    });
});