#app allows you to choose period of rental time, and return a map with the most and less expensive rental payment for a car in US (airports)
#using Avis API & Google Maps API
#user puts a starting date and return date
#app send request with that date and city from the list (list of biggest cities)
#for every request you get: price of the cheapest offer and car model.
#every respond is present visually on the map - with the gradient icons green>orange>red presenting price
#the cheapest and the most expensive offers are presented by the biggest icons

import requests
import json
from requests.structures import CaseInsensitiveDict
import folium

# Creating a map (US)
map = folium.Map(location=[36.153980,-95.992775], zoom_start=4)

# Creating list of the biggest airports in US
iata_list = "https://raw.githubusercontent.com/jbrooksuk/JSON-Airports/master/airports.json"

il_r = requests.get(iata_list).json()

list_cities = []
for i in range(len(il_r)):
    if il_r[i]["iso"] == "US" and il_r[i]["size"] == "large":
        list_cities.append(il_r[i]["iata"])

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

# make acces to API with Access Token (Curl GET JSON in Python)
headers2 = CaseInsensitiveDict()
headers2["Accept"] = "application/json"
headers2["client_id"] = avis_api_id
headers2["authorization"] = auth_code


# pickup date and dropoff date - input by user
pick_up_date = "2021-01-11" #input("Podaj datę początkową wynajmu: ")
dropoff_date = "2021-01-15" #input("Podaj datę końcową wynajmu: ")
all_data_dict={}
x = -1
for i in range(len(list_cities)):
    try:
        iata_loc = list_cities[i]

        # getting response of location - full name of the airport
        url_loc = "https://stage.abgapiservices.com:443/cars/locations/v1?brand=Avis%2CBudget%2CPayless&country_code=US&keyword="+iata_loc

        s = requests.get(url_loc, headers=headers2)
        loc_name = s.json()["locations"][0]["name"]
        url = "https://stage.abgapiservices.com:443/cars/catalog/v1/vehicles/rates?brand=Avis&pickup_date="+pick_up_date+"T00%3A00%3A00&pickup_location="+iata_loc+"&dropoff_date="+dropoff_date+"T00%3A00%3A00&dropoff_location="+iata_loc+"&country_code=US&vehicle_class_code=A&rate_code=G3"

        r = requests.get(url, headers=headers2)
        price = r.json()["reservation"]["rate_totals"]["totals"]["reservation_total"]
        x+=1
        all_data_dict[x] = {"IATA": iata_loc, "name": loc_name, "price": float(price),
                            "lat": s.json()["locations"][0]["address"]["lat"],
                            "long": s.json()["locations"][0]["address"]["long"]
                            }
        print(x)
        print(loc_name)
        print("$" + str(price))

        folium.Marker(location=[all_data_dict[x]["lat"], all_data_dict[x]["long"]], popup=all_data_dict[x]["IATA"] + " " + all_data_dict[x]["name"], tooltip="$"+str(all_data_dict[x]["price"]),
                      icon=folium.Icon(color="blue", icon="glyphicon glyphicon-record")).add_to(map)


    except:
        pass



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

folium.Marker(location=[lat_max, long_max],popup=iata_max+" "+name_max, tooltip="$"+str(price_max), icon=folium.Icon(color="red", icon="glyphicon glyphicon-arrow-up")).add_to(map)
folium.Marker(location=[lat_min, long_min],popup=iata_min+" "+name_min, tooltip="$"+str(price_min), icon=folium.Icon(color="green", icon="glyphicon glyphicon-arrow-down")).add_to(map)

map.save("Mapa_testowa.html")
