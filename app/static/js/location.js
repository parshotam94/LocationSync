if (navigator.geolocation) {
    navigator.geolocation.watchPosition((pos) => {
        const data = {
            user_id: USER_ID,
            group_id: GROUP_ID,
            lat: pos.coords.latitude,
            lng: pos.coords.longitude
        };
        
        // Emit to server
        socket.emit("send_location", data);
        
        // Optimistically update own map to feel instant
        updateMap(data);
        
    }, (err) => {
        console.error("Geolocation error:", err);
    }, {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 5000
    });
} else {
    alert("Geolocation is not supported by your browser.");
}