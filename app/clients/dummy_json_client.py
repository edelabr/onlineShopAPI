import requests

def get_products():
    try:
        url = (
            f"https://dummyjson.com/products"
        )
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            json_data = response.json()
            hourly = json_data['hourly']
            return [
                {
                    "time": hourly['time'][i],
                    "temperature_2m": hourly['temperature_2m'][i],
                    "relative_humidity_2m": hourly['relative_humidity_2m'][i],
                    "rain": hourly['rain'][i]
                }
                for i in range(len(hourly['time']))
            ]
        else:
            print(f"Weather API response error: {response.status_code}")
    except Exception as e:
        print(f"Weather API error: {e}")
    return None
