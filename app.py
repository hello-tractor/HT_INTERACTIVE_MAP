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

# URLs of the landjob data
landjob_url_2024 = "https://raw.githubusercontent.com/Sumbati10/sorting_algorithms/main/output.geojson"

def fetch_landjob_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching landjob data: {response.status_code} {response.reason}")
        return None

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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/definition')
def definition():
    return render_template('definition.html')

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
                        <div data-name="County"><strong>County:</strong> {properties['County']}</div>
                        <div data-name="Subcounty"><strong>Subcounty:</strong> {properties['Subcounty']}</div>
                        <div data-name="Ward"><strong>Ward:</strong> {properties['wards']}</div>
                        <div data-name="Month"><strong>Month:</strong> {properties['month']}</div>
                        <div data-name="Year"><strong>Year:</strong> {properties['year']}</div>
                        <div data-name="Temp(mean)"><strong>Temp(mean):</strong> {properties['Temperature_mean']}</div>
                        <div data-name="NDVI-5"><strong>NDVI-5:</strong> {properties['NVDI 5 PERCENTILE']}</div>
                        <div data-name="NDVI-50"><strong>NDVI-50:</strong> {properties['NVDI 50 PERCENTILE']}</div>
                        <div data-name="NDVI-95"><strong>NDVI-95:</strong> {properties['NVDI 95 PERCENTILE']}</div>
                        <div data-name="NDVI-25"><strong>NDVI-25:</strong> {properties['NVDI 25 PERCENTILE']}</div>
                        <div data-name="NDVI (max)"><strong>NVDI (max):</strong> {properties['NVDI (max)']}</div>
                        <div data-name="NDVI (min)"><strong>NVDI (min):</strong> {properties['NVDI(min)']}</div>
                        <div data-name="NDVI (mean)"><strong>NVDI (mean):</strong> {properties['NVDI(MEAN)']}</div>
                        <div data-name="Rainfall"><strong>Rainfall:</strong> {properties['Rainfall-Precipitataion(mean)']}</div>
                        <div data-name="Landcover"><strong>Landcover:</strong> {properties['LANDCOVER(GFSAD)']}</div>
                        <div data-name="Worldcover (ESA)"><strong>Worldcover (ESA):</strong> {properties['WORLDCOVERCOVER(ESA)']}</div>
                        <div data-name="Agric-Occupation"><strong>Agric-Occupation:</strong> {properties['Agriculture_occupation']}</div>
                        <div data-name="Population"><strong>Population:</strong> {properties['Population']}</div>
                        <div data-name="Avg-Agri-Pop"><strong>Avg-Agri-Pop:</strong> {properties['Average Agriculturepopulation']}</div>
                    </div>
                """
            })
        
        return jsonify(data_to_send)
    
    else:
        return jsonify([])

@app.route('/search_wards', methods=['GET'])
def search_counties():
    query = request.args.get('query').lower()
    results = []

    for year, data in geojson_data.items():
        if data is not None:
            for feature in data['features']:
                if query in feature['properties']['wards'].lower():
                    results.append({
                        'latitude': feature['geometry']['coordinates'][1],
                        'longitude': feature['geometry']['coordinates'][0],
                        'wards': feature['properties']['wards']
                    })
    
    return jsonify(results)

@app.route('/fetch_landjob_data', methods=['POST'])
def fetch_landjob_data_route():
    landjob_data = fetch_landjob_data(landjob_url_2024)
    if landjob_data is None:
        return jsonify([])

    extracted_data = []
    for feature in landjob_data['features']:
        properties = feature['properties']
        extracted_data.append({
            'latitude': properties['geometry']['coordinates'][1],
            'longitude': properties['geometry']['coordinates'][0],
            'popup_content': f"""
                <div style='max-width: 300px;'>
                    <div><strong>User ID:</strong> {properties['user_id']}</div>
                    <div><strong>Location ID:</strong> {properties['location_id']}</div>
                    <!-- Add more fields as necessary -->
                </div>
            """
        })
    
    return jsonify(extracted_data)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

