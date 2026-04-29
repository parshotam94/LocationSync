var map = L.map('map').setView([28.6,77.2],6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

let markers = {};

function updateMarker(data){
    if(!markers[data.user_id]){
        markers[data.user_id] = L.marker([data.lat,data.lng]).addTo(map);
    } else {
        markers[data.user_id].setLatLng([data.lat,data.lng]);
    }
}