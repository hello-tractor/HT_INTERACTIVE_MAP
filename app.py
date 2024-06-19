from flask import Flask, render_template, jsonify, request
import folium
from folium import LayerControl
import requests

app = Flask(__name__)

# Function to fetch GeoJSON data using requests
def fetch_geojson(url):
    response = requests.get(url)
    geojson_data = response.json()
    return geojson_data

# URL of the GeoJSON data
geojson_url = "https://raw.githubusercontent.com/Sumbati10/REMOTE_SENSING/main/2021_transformed.geojson"

# Fetch GeoJSON data
geojson_data = fetch_geojson(geojson_url)

@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML page with the map

@app.route('/update_map', methods=['POST'])
def update_map():
    selected_month = request.json['month']  # Get selected month from JSON POST data
    
    # Filter GeoJSON data based on selected month
    filtered_features = [feature for feature in geojson_data['features'] if feature['properties']['month'] == int(selected_month)]
    
    # Prepare data to send back as JSON
    data_to_send = []
    for feature in filtered_features:
        properties = feature['properties']
        data_to_send.append({
            'latitude': properties['latitude'],
            'longitude': properties['longitude'],
            'popup_content': f"""
                <div style='max-width: 300px;'>
                    <strong>County:</strong> {properties['County']}<br>
                    <strong>Subcounty:</strong> {properties['Subcounty']}<br>
                    <strong>Ward:</strong> {properties['wards']}<br>
                    <strong>Month:</strong> {properties['month']}<br>
                    <strong>Year:</strong> {properties['year']}<br>
                    <strong>Temp(mean):</strong> {properties['Temperature_mean']}<br>
                    <strong>NDVI-5:</strong> {properties['NVDI 5 PERCENTILE']}<br>
                    <strong>NDVI-50:</strong> {properties['NVDI 50 PERCENTILE']}<br>
                    <strong>NDVI-95:</strong> {properties['NVDI 95 PERCENTILE']}<br>
                    <strong>NDVI-25:</strong> {properties['NVDI 25 PERCENTILE']}<br>
                    <strong>NVDI (max):</strong> {properties['NVDI (max)']}<br>
                    <strong>NVDI (min):</strong> {properties['NVDI(min)']}<br>
                    <strong>NVDI (mean):</strong> {properties['NVDI(MEAN)']}<br>
                    <strong>Rainfall:</strong> {properties['Rainfall-Precipitataion(mean)']}<br>
                    <strong>Landcover:</strong> {properties['LANDCOVER(GFSAD)']}<br>
                    <strong>Worldcover (ESA):</strong> {properties['WORLDCOVERCOVER(ESA)']}<br>
                    <strong>Agric-Occupation:</strong> {properties['Agriculture_occupation']}<br>
                    <strong>Population:</strong> {properties['Population']}<br>
                    <strong>Avg-Agri-Pop:</strong> {properties['Average Agriculturepopulation']}<br>
                </div>
            """
        })

    return jsonify(data_to_send)

if __name__ == '__main__':
    app.run(debug=True)
