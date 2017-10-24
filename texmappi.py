import json
import os
import webbrowser
import folium

from folium.plugins import MarkerCluster
from requests import get

# get weather station data
txmeso_url = 'https://www.texmesonet.org/api/CurrentData'
mesowest_url = 'http://api.mesowest.net/v2/stations/metadata?&state=tx&county=Travis&token=demotoken'
mesowest_data = get(mesowest_url).json()
txmeso_data = get(txmeso_url).json()

lons = []
lats = []
wsnames = []
airtemp = []

lons = [station['longitude'] for station in txmeso_data]
lats = [station['latitude'] for station in txmeso_data]
wsnames = [station['name'] for station in txmeso_data]
airtemp = [station['airTemp'] for station in txmeso_data]


# initialize the map
m = folium.Map(location=[30.334694,-97.781949],zoom_start=6, control_scale=True, tiles=None)

# add additional base maps
folium.TileLayer('https://{s}.tile.thunderforest.com/pioneer/{z}/{x}/{y}.png?apikey=47c1ac00fc2d4af9b0b9a6a4a5545341', name='Pioneer', attr='Thunderforest').add_to(m)
folium.TileLayer('https://{s}.tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png?apikey=47c1ac00fc2d4af9b0b9a6a4a5545341', name='Spinal Map', attr='Thunderforest').add_to(m)
folium.TileLayer('Stamen Toner', name='Stamen Toner').add_to(m)
folium.TileLayer('Stamen Watercolor', name='Stamen Watercolor').add_to(m)

# more basemaps
# folium.TileLayer('cartodbpositron', name='Positron', attr='Carto').add_to(m)
# folium.TileLayer('Stamen Terrain', name='Stamen Terrain').add_to(m)
# folium.TileLayer('Stamen Toner', name='Stamen Toner').add_to(m)
# folium.TileLayer('https://{s}.tile.thunderforest.com/transport-dark/{z}/{x}/{y}.png?apikey=47c1ac00fc2d4af9b0b9a6a4a5545341', name='Transport Dark', attr='Thunderforest').add_to(m)
# folium.TileLayer('https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=47c1ac00fc2d4af9b0b9a6a4a5545341', name='Outdoors', attr='Thunderforest').add_to(m)
# folium.TileLayer('https://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=47c1ac00fc2d4af9b0b9a6a4a5545341', name='Landscape', attr='Thunderforest').add_to(m)
# folium.TileLayer('https://{s}.tile.thunderforest.com/neighbourhood/{z}/{x}/{y}.png?apikey=47c1ac00fc2d4af9b0b9a6a4a5545341', name='neighbourhood', attr='Thunderforest').add_to(m)
# folium.TileLayer('https://{s}.tile.thunderforest.com/transport/{z}/{x}/{y}.png?apikey=47c1ac00fc2d4af9b0b9a6a4a5545341', name='Transport', attr='Thunderforest').add_to(m)

# geojson features from geoserver pi
counties_group =folium.FeatureGroup(name='Counties').add_to(m)
txdot_counties_detailed = get('http://10.10.11.66:8080/geoserver/tnris/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=tnris:txdot_2015_county_detailed_tx&maxFeatures=254&outputFormat=application%2Fjson').json()
for feature in txdot_counties_detailed['features']:
    county_name = feature['properties']['CNTY_NM']
    popup = folium.Popup(county_name + ' County')
    gj = folium.GeoJson(
            feature,
            style_function = lambda feature: {'fillColor': '#F8F9F9', 'fillOpacity': 0, 'color': '#545454', 'weight': 1, 'bubblingMouseEvents': False})
    gj.add_child(popup)
    gj.add_to(counties_group)

# state park geojson features
# folium.GeoJson(
#     state_parks,
#     name='State Parks',
#     style_function = lambda feature: {'fillColor': '#00ffffff','color': '#545454', 'weight': 1.5,'dashArray': '5, 5'},
#     highlight_function = lambda feature: {'fillColor': '#848484','color': 'green', 'weight': 3,'dashArray': '5, 5'}).add_child(folium.Popup('jason is the coolest')).add_to(m)

# wms layers from geoserver pi
folium.WmsTileLayer(url='http://10.10.11.66:8080/geoserver/tnris/wms',
                    name='State Parks',
                    layers='tnris:TPWD State Parks',
                    transparent=True,
                    fmt='image/png',
                    attr='TPWD').add_to(m)

folium.WmsTileLayer(url='http://10.10.11.66:8080/geoserver/tnris/wms',
                    name='Wildlife Management Areas',
                    layers='tnris:Wildlife Management Areas',
                    transparent=True,
                    fmt='image/png',
                    attr='TPWD').add_to(m)

# mesowest stations for travis county
mesowest_url = 'http://api.mesowest.net/v2/stations/metadata?&state=tx&county=Travis&token=demotoken'
mesowest_data = get(mesowest_url).json()

marker_cluster = MarkerCluster(name='Travis County Mesowest Stations').add_to(m)

for station in mesowest_data['STATION']:
    if station['STATUS'] == 'ACTIVE':
        tooltip = station['NAME'] + ', Elevation: ' + station['ELEVATION'] + 'ft'
        folium.Marker([float(station['LATITUDE']),
                       float(station['LONGITUDE'])],
                       popup=tooltip,
                       icon=folium.Icon(icon = 'cloud')).add_to(marker_cluster)

# off leash park locations from the city of austin
off_leash_data = os.path.join(os.getcwd(), 'off-leash-areas.geojson')
f = open(off_leash_data).read()
data = json.loads(f)
for feature in data['features']:
    print(feature['geometry']['type'])
    print(feature['geometry']['coordinates'])


folium.LayerControl().add_to(m)


# save the map as html and open in the browser
CWD = os.getcwd()
m.save('texmappi.html')
webbrowser.open_new('file://' + CWD + '/' + 'texmappi.html')
