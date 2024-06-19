from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# GitHub username and updated PAT (Personal Access Token)
github_user = 'Sumbati10'
github_pat = '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'

# URLs of the GeoJSON data for different years
geojson_url_2021 = "https://raw.githubusercontent.com/Sumbati10/REMOTE_SENSING/main/2021_transformed.geojson"
geojson_url_2022 = "https://raw.githubusercontent.com/Sumbati10/REMOTE_SENSING/main/20222_transformed.geojson"
geojson_url_2023 = "https://raw.githubusercontent.com/Sumbati10/REMOTE_SENSING/main/22023_transformed.geojson"

# Function to fetch GeoJSON data using GitHub authentication
def fetch_geojson_with_auth(url):
    headers = {
        'Authorization': f'token {github_pat}',
        'Accept': 'application/vnd.github.v3.raw'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching GeoJSON: {response.status_code} {response.reason}")
        return None

# Fetch GeoJSON data for all years
geojson_data = {
    '2021': fetch_geojson_with_auth(geojson_url_2021),
    '2022': fetch_geojson_with_auth(geojson_url_2022),
    '2023': fetch_geojson_with_auth(geojson_url_2023)
}

@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML page with the map

@app.route('/update_map', methods=['POST'])
def update_map():
    selected_year = request.json['year']  # Get selected year from JSON POST data
    selected_month = request.json['month']  # Get selected month from JSON POST data
    
    if selected_year in geojson_data and geojson_data[selected_year] is not None:
        selected_geojson_data = geojson_data[selected_year]
        filtered_features = [feature for feature in selected_geojson_data['features'] if feature['properties']['month'] == int(selected_month)]
        
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
    else:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
