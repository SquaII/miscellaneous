import json
import urllib2


latitude = raw_input("Enter latitude:")
longitude = raw_input("Enter longitude:")
language = raw_input("Enter language:")

gh_url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&language={2}&sensor=false"
req = urllib2.urlopen(gh_url.format(latitude, longitude, language))
json_data = req.read()
data = json.loads(json_data)

components = data['results'][0]['address_components']
for component in components:
    if 'administrative_area_level_1' in component['types']:
        print 'Region:', component['long_name']

    if 'locality' in component['types']:
        print 'City:', component['long_name']
