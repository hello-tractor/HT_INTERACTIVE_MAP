// Initialize the map
var map = L.map('map').setView([0.9036, 36.1477], 8); // Set initial view and zoom

// Define basemaps
var osm = L.tileLayer(
    'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }
).addTo(map);

var cyclOSM = L.tileLayer(
    'https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
    {
        maxZoom: 19,
        attribution: '<a href="https://github.com/cyclosm/cyclosm-cartocss-style/releases" title="CyclOSM - Open Bicycle render">CyclOSM</a> | Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }
);

// Create layer control for the basemaps
var baseMaps = {
    "OpenStreetMap": osm,
    "CyclOSM": cyclOSM
};

// Add basemap layers and overlay layers to the map
L.control.layers(baseMaps, null, { collapsed: false }).addTo(map);

// Function to update GeoJSON layer
function updateGeoJSON(selectedYear, selectedMonth) {
    // Fetch GeoJSON data based on selectedYear and selectedMonth
    var url = "{{ url_for('static', filename='kenya_wards_geojson.json') }}"; // Adjust URL as per Flask structure

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Style function for GeoJSON polygons
            function style(feature) {
                return {
                    fillColor: '#3388ff', // Default color for polygons
                    weight: 2,
                    opacity: 1,
                    color: 'white',
                    dashArray: '3',
                    fillOpacity: 0.7
                };
            }

            // Create GeoJSON layer with style
            L.geoJson(data, {
                style: style
            }).addTo(map);
        })
        .catch(error => {
            console.log(`Error fetching GeoJSON data: ${error}`);
        });
}

// Initial call to load GeoJSON data for default year and month
updateGeoJSON('2021', '1');

// Dropdown change event handlers
document.getElementById('yearDropdown').addEventListener('change', function () {
    var selectedYear = this.value;
    var selectedMonth = document.getElementById('monthDropdown').value;
    updateGeoJSON(selectedYear, selectedMonth);
});

document.getElementById('monthDropdown').addEventListener('change', function () {
    var selectedYear = document.getElementById('yearDropdown').value;
    var selectedMonth = this.value;
    updateGeoJSON(selectedYear, selectedMonth);
});

// Add zoom control to the map
L.control.zoom({ position: 'bottomright' }).addTo(map);
