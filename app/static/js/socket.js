const socket = io();

// Join the group room
socket.emit("join_group", { group_id: GROUP_ID });

// Receive initial location history
socket.on("location_history", (history) => {
    console.log("Loaded history:", history);
    loadHistory(history);
});

// Receive live location updates
socket.on("receive_location", (data) => {
    updateMap(data);
});