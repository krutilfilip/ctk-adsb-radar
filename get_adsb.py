import requests

def get_nearest_planes(lat, lon, radius_nm):
    api_url = f"https://api.adsb.lol/v2/point/{lat}/{lon}/{radius_nm}"

    try:
        response = requests.get(api_url, timeout=2.0)
        plane_list = response.json()['ac']
        return plane_list
    except Exception as e:
        return []

def get_plane_route(callsign):
    api_url = f"https://api.adsbdb.com/v0/callsign/{callsign}"

    try:
        response = requests.get(api_url, timeout=2.0).json()
        airline_json = response['response']['flightroute']['airline']
        origin_json = response['response']['flightroute']['origin']
        destination_json = response['response']['flightroute']['destination']

        airline_name = airline_json['callsign']

        origin_city = origin_json['municipality']
        origin_airport_code = origin_json['iata_code']
        origin_airport = origin_json['name']
        origin_country = origin_json['country_name']

        destination_city = destination_json['municipality']
        destination_airport_code = destination_json['iata_code']
        destination_airport = destination_json['name']
        destination_country = destination_json['country_name']

        route = {
            'airline_name': airline_name,
            'origin_city': origin_city,
            'origin_airport_code': origin_airport_code,
            'origin_airport': origin_airport,
            'origin_country': origin_country,
            'destination_city': destination_city,
            'destination_airport_code': destination_airport_code,
            'destination_airport': destination_airport,
            'destination_country': destination_country
        }
        return route
    except Exception as e:
        print(e)
        return "NO DATA"