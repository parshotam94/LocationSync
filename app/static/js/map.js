// Initialize Map
var map = L.map('map').setView([28.6, 77.2], 10);

L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
}).addTo(map);

let markers = {};
let polylines = {};
let routeCoordinates = {};
let userNames = {};
let activeParticipants = new Set();

// Ride State
let rideActive = false;
let currentRideId = null;
let rideStartTime = null;
let rideDistanceKm = 0;
let lastRidePoint = null;

// Destination Marker
if (DEST_LAT && DEST_LNG) {
    const destIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    L.marker([DEST_LAT, DEST_LNG], {icon: destIcon}).addTo(map).bindTooltip("Destination", {permanent: true, direction: 'top', offset: [0, -20]});
}

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
    if (rideActive) activeParticipants.add(userId);

    // Track coordinates
    if (!routeCoordinates[userId]) {
        routeCoordinates[userId] = [];
    }
    
    // Only track route history if ride is active or it's historical data
    if (rideActive || data.is_historical) {
        routeCoordinates[userId].push(latlng);
        
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
    }

    // Update or create Marker
    if (!markers[userId]) {
        markers[userId] = L.marker(latlng).addTo(map);
        markers[userId].bindTooltip(userName, {permanent: true, direction: 'top', offset: [0, -20]}).openTooltip();
    } else {
        markers[userId].setLatLng(latlng);
    }

    // Active Ride Metrics Calculation (For Current User Only)
    if (userId == USER_ID && rideActive) {
        if (lastRidePoint) {
            const distMeters = map.distance(lastRidePoint, latlng);
            rideDistanceKm += (distMeters / 1000);
            document.getElementById('stat-dist').innerText = rideDistanceKm.toFixed(2);
            
            const hoursElapsed = (new Date() - rideStartTime) / (1000 * 60 * 60);
            if (hoursElapsed > 0) {
                const speed = rideDistanceKm / hoursElapsed;
                document.getElementById('stat-speed').innerText = speed.toFixed(1);
            }
        }
        lastRidePoint = latlng;
    }

    // Auto-pan map to the current user's location
    if (userId == USER_ID && !data.is_historical) {
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
            lng: point.longitude,
            is_historical: true
        });
    });
}

// ----------------------------------------------------
// Ride Controls & ETA
// ----------------------------------------------------

// Handle incoming socket events for rides
socket.on("ride_started", (data) => {
    rideActive = true;
    currentRideId = data.ride_id;
    rideStartTime = new Date();
    rideDistanceKm = 0;
    
    // clear map lines
    for (let uid in polylines) {
        map.removeLayer(polylines[uid]);
    }
    polylines = {};
    routeCoordinates = {};
    if (markers[USER_ID]) {
        lastRidePoint = markers[USER_ID].getLatLng();
    }
    
    document.getElementById('active-ride-stats').style.display = 'block';
    
    if (IS_OWNER) {
        document.getElementById('start-ride-btn').style.display = 'none';
        document.getElementById('ride-name').style.display = 'none';
        document.getElementById('end-ride-btn').style.display = 'inline-block';
    }
});

socket.on("ride_ended", () => {
    rideActive = false;
    document.getElementById('active-ride-stats').style.display = 'none';
    if (IS_OWNER) {
        document.getElementById('start-ride-btn').style.display = 'inline-block';
        document.getElementById('ride-name').style.display = 'inline-block';
        document.getElementById('end-ride-btn').style.display = 'none';
    }
    alert("Ride has ended!");
});

if (IS_OWNER) {
    document.getElementById('start-ride-btn').addEventListener('click', () => {
        const rideName = document.getElementById('ride-name').value || "New Ride";
        fetch('/api/start_ride', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ group_id: GROUP_ID, name: rideName })
        }).then(r => r.json()).then(res => {
            if (res.success) {
                socket.emit("ride_started", { group_id: GROUP_ID, ride_id: res.ride_id });
            }
        });
    });

    document.getElementById('end-ride-btn').addEventListener('click', () => {
        const durationMins = (new Date() - rideStartTime) / (1000 * 60);
        const avgSpeed = durationMins > 0 ? (rideDistanceKm / (durationMins/60)) : 0;
        
        fetch('/api/end_ride', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                ride_id: currentRideId,
                total_distance: rideDistanceKm,
                duration_minutes: durationMins,
                avg_speed: avgSpeed,
                participant_ids: Array.from(activeParticipants)
            })
        }).then(r => r.json()).then(res => {
            if (res.success) {
                socket.emit("ride_ended", { group_id: GROUP_ID });
            }
        });
    });
}

// AI ETA Polling
if (DEST_LAT && DEST_LNG) {
    setInterval(() => {
        if (!markers[USER_ID]) return;
        
        const currentLatLng = markers[USER_ID].getLatLng();
        const destLatLng = L.latLng(DEST_LAT, DEST_LNG);
        const distKm = currentLatLng.distanceTo(destLatLng) / 1000;
        
        // estimate speed (use ride speed if available, else assume 40km/h default)
        let speed = 40;
        if (rideActive && rideDistanceKm > 0) {
            const hoursElapsed = (new Date() - rideStartTime) / (1000 * 60 * 60);
            speed = rideDistanceKm / hoursElapsed;
        }

        fetch('/api/eta', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ distance_km: distKm.toFixed(2), speed_kmh: speed.toFixed(1) })
        }).then(r => r.json()).then(res => {
            document.getElementById('eta-display').innerText = res.eta;
        });
    }, 30000); // query gemini every 30 seconds
}