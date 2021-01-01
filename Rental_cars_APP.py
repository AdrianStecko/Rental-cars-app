"""
App allows you to choose period of rental time and class of the car, and return a map with the most and less expensive rental rates (only US airports)
Use Avis API & folium
User enter a starting date and a returning date as well as a class of the car
App send request with that data and city from the dictionary (list_cities)
For every request you get a price
Every respond is present visually on the map - with the red mark for the most expensive offer and green one for cheapest offer
The rest of offers are presented with blue marks
"""

import requests
import json
from requests.structures import CaseInsensitiveDict
import folium

# Creating a map (US)
map = folium.Map(location=[36.153980,-95.992775], zoom_start=4)

# Opening file with airports data
iata_list = open("airports.json")
il_r = json.load(iata_list)

# Creating dictionary of IATA codes
list_cities = {}
for i in range(len(il_r)):
    if il_r[i]["iso"] == "US" and il_r[i]["size"] == "large":
        list_cities[il_r[i]["iata"]] = {"lat": il_r[i]["lat"], "long": il_r[i]["lon"], "name": il_r[i]["name"]}
    else:
        pass

# Reading Avis API client_id and client_secret
avis_api_id_file = open("Avis_API_id.txt", "r")
avis_api_id = avis_api_id_file.read()
avis_api_id_file.close()
avis_api_cs_file = open("Avis_API_client_secret.txt", "r")
avis_api_cs = avis_api_cs_file.read()
avis_api_cs_file.close()

# Obtaining Access Token
headers = CaseInsensitiveDict()
headers["client_id"] = avis_api_id
headers["client_secret"] = avis_api_cs
url_acces = "https://stage.abgapiservices.com/oauth/token/v1"
g = requests.get(url_acces, headers=headers)
access_token = g.json()["access_token"]
auth_code = "Bearer"+" "+str(access_token)

# Make acces to API with Access Token (Curl GET JSON in Python)
headers2 = CaseInsensitiveDict()
headers2["Accept"] = "application/json"
headers2["client_id"] = avis_api_id
headers2["authorization"] = auth_code


# Pick up date, drop off date and car class - input by user
pick_up_date = input("Enter a pick up date in format YYYY-MM-DD: ")
dropoff_date = input("Enter a drop off date in format YYYY-MM-DD: ")
car_class = input("Enter a class of the car (A,B,C,D,E,S,P,G,H,L,K,W,V,F,Z): ")

# Creating empty dict for entire data
all_data_dict={}

x = -1

for iata_loc in list_cities:
    try:
        # Getting response of a car rate code
        url_ava = "https://stage.abgapiservices.com:443/cars/catalog/v1/vehicles?brand=Avis&pickup_date="+pick_up_date+"T12%3A00%3A00&pickup_location="+iata_loc+"&dropoff_date="+dropoff_date+"T12%3A00%3A00&dropoff_location="+iata_loc+"&country_code=US"
        s = requests.get(url_ava, headers=headers2)
        rate_code_list = s.json()["vehicles"]
        for i in range(len(rate_code_list)):
            if s.json()["vehicles"][i]["category"]["vehicle_class_code"] == car_class:
                rate_code = s.json()["vehicles"][i]["rate_totals"]["rate"]["rate_code"]

        # Getting response of a full price
        url_rate = "https://stage.abgapiservices.com:443/cars/catalog/v1/vehicles/rates?brand=Avis&pickup_date="+pick_up_date+"T12%3A00%3A00&pickup_location="+iata_loc+"&dropoff_date="+dropoff_date+"T12%3A00%3A00&dropoff_location="+iata_loc+"&country_code=US&vehicle_class_code="+car_class+"&rate_code="+rate_code

        r = requests.get(url_rate, headers=headers2)
        price = r.json()["reservation"]["rate_totals"]["totals"]["reservation_total"]
        x+=1

        all_data_dict[x] = {"IATA": iata_loc, "name": list_cities[iata_loc]["name"], "price": float(price),
                            "lat": list_cities[iata_loc]["lat"],
                            "long": list_cities[iata_loc]["long"]
                            }

        # Creating marks for every location
        folium.Marker(location = [all_data_dict[x]["lat"], all_data_dict[x]["long"]], popup = all_data_dict[x]["IATA"] + " " + all_data_dict[x]["name"], tooltip = "$"+str(all_data_dict[x]["price"]),
                      icon = folium.Icon(color = "blue", icon = "glyphicon glyphicon-record")).add_to(map)

    except:
        pass

# sorting for max and min rates
price_max = 0
for k,v in all_data_dict.items():
    if price_max < float(v['price']):
        price_max = float(v['price'])
        iata_max = all_data_dict[k]["IATA"]
        name_max = all_data_dict[k]["name"]
        lat_max = all_data_dict[k]["lat"]
        long_max = all_data_dict[k]["long"]

price_min = float("inf")
for l,j in all_data_dict.items():
    if price_min > float(j['price']):
        price_min = float(j['price'])
        iata_min = all_data_dict[l]["IATA"]
        name_min = all_data_dict[l]["name"]
        lat_min = all_data_dict[l]["lat"]
        long_min = all_data_dict[l]["long"]

print("Najwyższa cena obowiązuje w: "+str(iata_max)+" "+str(name_max)+" $"+str(price_max))
print(lat_max)
print(long_max)

print("Najniższa cena obowiązuje w: "+str(iata_min)+" "+str(name_min)+" $"+str(price_min))
print(lat_min)
print(long_min)

# creating marks for max and min rates
folium.Marker(location=[lat_max, long_max],popup=iata_max+" "+name_max, tooltip="$"+str(price_max), icon=folium.Icon(color="red", icon="glyphicon glyphicon-arrow-up")).add_to(map)
folium.Marker(location=[lat_min, long_min],popup=iata_min+" "+name_min, tooltip="$"+str(price_min), icon=folium.Icon(color="green", icon="glyphicon glyphicon-arrow-down")).add_to(map)

map.save("Test_map.html")
