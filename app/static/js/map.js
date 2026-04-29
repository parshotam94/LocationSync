// Initialize Map
var map = L.map('map').setView([28.6, 77.2], 10);

L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
}).addTo(map);

let markers = {};
let polylines = {};
let routeCoordinates = {};

// distinct colors for different users
const colors = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

function getColor(userId) {
    return colors[userId % colors.length];
}

function updateMap(data) {
    const userId = data.user_id;
    const latlng = [data.lat, data.lng];

    // Track coordinates
    if (!routeCoordinates[userId]) {
        routeCoordinates[userId] = [];
    }
    routeCoordinates[userId].push(latlng);

    // Update or create Marker
    if (!markers[userId]) {
        markers[userId] = L.marker(latlng).addTo(map);
        markers[userId].bindPopup(`User ${userId}`).openPopup();
    } else {
        markers[userId].setLatLng(latlng);
    }

    // Update or create Polyline
    if (!polylines[userId]) {
        polylines[userId] = L.polyline(routeCoordinates[userId], {
            color: getColor(userId),
            weight: 5,
            opacity: 0.7,
            smoothFactor: 1
        }).addTo(map);
    } else {
        polylines[userId].setLatLngs(routeCoordinates[userId]);
    }

    // Auto-pan map to the current user's location
    if (userId == USER_ID) {
        map.panTo(latlng);
    }
}

// Function to load history when joining
function loadHistory(history) {
    history.forEach(point => {
        updateMap({
            user_id: point.user_id,
            lat: point.latitude,
            lng: point.longitude
        });
    });
}