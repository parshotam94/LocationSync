// Initialize Map
var map = L.map('map').setView([28.6, 77.2], 10);

L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
}).addTo(map);

let markers = {};
let polylines = {};
let routeCoordinates = {};
let userNames = {};

// distinct colors for different users
const colors = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

function getColor(userId) {
    return colors[userId % colors.length];
}

function updateMap(data) {
    const userId = data.user_id;
    const userName = data.user_name || `User ${userId}`;
    const latlng = [data.lat, data.lng];

    userNames[userId] = userName;

    // Track coordinates
    if (!routeCoordinates[userId]) {
        routeCoordinates[userId] = [];
    }
    routeCoordinates[userId].push(latlng);

    // Update or create Marker
    if (!markers[userId]) {
        markers[userId] = L.marker(latlng).addTo(map);
        markers[userId].bindTooltip(userName, {permanent: true, direction: 'top', offset: [0, -20]}).openTooltip();
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

    updateDistances();
}

function updateDistances() {
    const distancesContainer = document.getElementById('distances-list');
    if (!distancesContainer) return;
    
    distancesContainer.innerHTML = '';
    
    if (!markers[USER_ID]) {
        distancesContainer.innerHTML = '<div>Waiting for your location...</div>';
        return;
    }
    
    const myLatLng = markers[USER_ID].getLatLng();
    let hasOthers = false;

    for (let uid in markers) {
        if (uid != USER_ID) {
            hasOthers = true;
            const theirLatLng = markers[uid].getLatLng();
            const distanceMeters = myLatLng.distanceTo(theirLatLng);
            let distanceStr = '';
            if (distanceMeters > 1000) {
                distanceStr = (distanceMeters / 1000).toFixed(2) + ' km';
            } else {
                distanceStr = Math.round(distanceMeters) + ' m';
            }
            
            const name = userNames[uid] || `User ${uid}`;
            const div = document.createElement('div');
            div.style.marginBottom = '5px';
            div.innerHTML = `<span style="color: ${getColor(uid)}; font-weight: bold;">${name}</span>: ${distanceStr}`;
            distancesContainer.appendChild(div);
        }
    }
    
    if (!hasOthers) {
        distancesContainer.innerHTML = '<div>No other members active.</div>';
    }
}

// Function to load history when joining
function loadHistory(history) {
    history.forEach(point => {
        updateMap({
            user_id: point.user_id,
            user_name: point.user_name,
            lat: point.latitude,
            lng: point.longitude
        });
    });
}