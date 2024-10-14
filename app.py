from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# Correct URLs of the GeoJSON data for different years from S3 bucket
geojson_url_2021 = "https://ht-interactive-map.s3.us-west-2.amazonaws.com/kenya/cleaned-up-data-silver-layer/KENYA/2021_transformed.geojson"
geojson_url_2022 = "https://ht-interactive-map.s3.us-west-2.amazonaws.com/kenya/cleaned-up-data-silver-layer/KENYA/20222_transformed.geojson"
geojson_url_2023 = "https://ht-interactive-map.s3.us-west-2.amazonaws.com/kenya/cleaned-up-data-silver-layer/KENYA/22023_transformed.geojson"


# Function to fetch GeoJSON data
def fetch_geojson(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching GeoJSON: {response.status_code} {response.reason}")
        return None

# Fetch GeoJSON data for all years
geojson_data = {
    '2021': fetch_geojson(geojson_url_2021),
    '2022': fetch_geojson(geojson_url_2022),
    '2023': fetch_geojson(geojson_url_2023)
}

# Direct URL to fetch the GeoJSON data
geojson_url = "https://ht-interactive-map.s3.us-west-2.amazonaws.com/kenya/cleaned-up-data-silver-layer/Kenya_soil_data_converted12.geojson"

# Add this function to fetch GeoJSON data
def fetch_soil_geojson(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching soil GeoJSON: {response.status_code} {response.reason}")
        return None

# Fetch GeoJSON data for soil
soil_geojson_data = fetch_geojson(geojson_url)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/definition')
def definition():
    return render_template('definition.html')

@app.route('/')
def index():
    return render_template('index.html')  

@app.route('/update_map', methods=['POST'])
def update_map():
    selected_year = request.json.get('year', None)  
    selected_month = request.json.get('month', None)  
    
    if selected_year in geojson_data and geojson_data[selected_year] is not None:
        selected_geojson_data = geojson_data[selected_year]
        filtered_features = [
            feature for feature in selected_geojson_data['features'] 
            if str(feature.get('properties', {}).get('month')) == selected_month
        ]
        
        data_to_send = []
        for feature in filtered_features:
            properties = feature.get('properties', {})
            data_to_send.append({
                'latitude': properties.get('latitude'),
                'longitude': properties.get('longitude'),
                'popup_content': f"""
                    <div style='max-width: 300px;'>
                        <div data-name="County"><strong>County:</strong> {properties.get('County')}</div>
                        <div data-name="Subcounty"><strong>Subcounty:</strong> {properties.get('Subcounty')}</div>
                        <div data-name="Ward"><strong>Ward:</strong> {properties.get('wards')}</div>
                        <div data-name="Month"><strong>Month:</strong> {properties.get('month')}</div>
                        <div data-name="Year"><strong>Year:</strong> {properties.get('year')}</div>
                        <div data-name="Temp(mean)"><strong>Temp(mean):</strong> {properties.get('Temperature_mean')}</div>
                        <div data-name="NDVI-5"><strong>NDVI-5:</strong> {properties.get('NVDI 5 PERCENTILE')}</div>
                        <div data-name="NDVI-50"><strong>NDVI-50:</strong> {properties.get('NVDI 50 PERCENTILE')}</div>
                        <div data-name="NDVI-95"><strong>NDVI-95:</strong> {properties.get('NVDI 95 PERCENTILE')}</div>
                        <div data-name="NDVI-25"><strong>NDVI-25:</strong> {properties.get('NVDI 25 PERCENTILE')}</div>
                        <div data-name="NDVI (max)"><strong>NVDI (max):</strong> {properties.get('NVDI (max)')}</div>
                        <div data-name="NDVI (min)"><strong>NVDI (min):</strong> {properties.get('NVDI(min)')}</div>
                        <div data-name="NDVI (mean)"><strong>NVDI (mean):</strong> {properties.get('NVDI(MEAN)')}</div>
                        <div data-name="Rainfall"><strong>Rainfall:</strong> {properties.get('Rainfall-Precipitataion(mean)')}</div>
                        <div data-name="Landcover"><strong>Landcover:</strong> {properties.get('LANDCOVER(GFSAD)')}</div>
                        <div data-name="Worldcover (ESA)"><strong>Worldcover (ESA):</strong> {properties.get('WORLDCOVERCOVER(ESA)')}</div>
                        <div data-name="Agric-Occupation"><strong>Agric-Occupation:</strong> {properties.get('Agriculture_occupation')}</div>
                        <div data-name="Population"><strong>Population:</strong> {properties.get('Population')}</div>
                        <div data-name="Avg-Agri-Pop"><strong>Avg-Agri-Pop:</strong> {properties.get('Average Agriculturepopulation')}</div>
                    </div>
                """
            })
        
        return jsonify(data_to_send)
    
    else:
        return jsonify([])

@app.route('/search_wards', methods=['GET'])
def search_counties():
    query = request.args.get('query', '').lower()
    results = []

    for year, data in geojson_data.items():
        if data is not None:
            for feature in data['features']:
                if query in str(feature.get('properties', {}).get('wards', '')).lower():
                    results.append({
                        'latitude': feature.get('geometry', {}).get('coordinates', [])[1],
                        'longitude': feature.get('geometry', {}).get('coordinates', [])[0],
                        'wards': feature.get('properties', {}).get('wards')
                    })
    
    return jsonify(results)

# Add this route to serve the soil GeoJSON data
@app.route('/soil_data')
def get_soil_data():
    return jsonify(soil_geojson_data)

if __name__ == '__main__':
    app.run(debug=True)
