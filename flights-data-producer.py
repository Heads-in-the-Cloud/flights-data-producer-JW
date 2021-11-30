from faker import Faker
from collections import defaultdict
import random
import requests
import json
from xlrd import open_workbook


def formatting(jsonString):
    jsonString=jsonString.replace("[", "")
    jsonString=jsonString.replace("]","")
    return jsonString

def authHeader():
    token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJNb25pY2EtQnJhZGxleTI3NTAiLCJleHAiOjE2MzgyNTk5MjgsImlhdCI6MTYzODI0MTkyOH0.tIP4yBFTElHjSmFL6V9pRnfgneSMtYfmF9lPxTZZYZAHpTDdX5TR3im06fzyTaDB_DpltrV4-ayUF68zCy9yoQ"
    head = {'Authorization': 'Bearer ' + token}
    return head
def addType():
    type = defaultdict(list)
    max = random.randint(100,400)
    par = {'max_capacity':max}

    response = requests.post("http://localhost:9001/airplanetype", params=par, headers=authHeader())
    return response
def addAirplane():
    r = requests.get("http://localhost:9001/airplanetype", headers = authHeader())
    jsonType = r.json()
    typeIdList = []
    for x in range(len(jsonType)):
        typeIdList.append(jsonType[x]["id"])

    pickType = typeIdList[random.randint(0,len(typeIdList)-1)]
    aType = defaultdict(list)
    aType["id"].append(pickType)

    airplane = defaultdict(list)
    airplane["aType"].append(aType)
    airplaneJSON = json.dumps(airplane)
    airplaneJSON=formatting(airplaneJSON)
    finalinput = json.loads(airplaneJSON)
    response = requests.post("http://localhost:9001/airplane", json=finalinput, headers = authHeader())

#Should only be called once, adds every airport/ iata in the US to to airport table
def addAirports():
    airport = open_workbook('iataList.xls')
    for ap in airport.sheets():
        values = []
        for row in range(ap.nrows):
            indivAp = []
            for column in range(ap.ncols):
                val = (ap.cell(row,column).value)
                indivAp.append(val)
            values.append(indivAp)
    for ap in values:
        airport = defaultdict(list)
        airport["airportCode"].append(ap[0])
        airport["cityName"].append(ap[1])
        airportJSON = json.dumps(airport)
        airportJSON = formatting(airportJSON)
        finalinput = json.loads(airportJSON)
        response = requests.post("http://localhost:9001/airport", json=finalinput, headers = authHeader())

def addRoute():
    r = requests.get("http://localhost:9001/airport", headers = authHeader())
    jsonAirport = r.json()
    airportList = []
    for x in range(len(jsonAirport)):
        airportList.append(jsonAirport[x]["airportCode"])
    same = True
    while same:
        pickOrigin = airportList[random.randint(0,len(airportList)-1)]
        pickDest = airportList[random.randint(0,len(airportList)-1)]
        if(pickOrigin != pickDest):
            same = False
    origin = defaultdict(list)
    dest = defaultdict(list)
    origin["airportCode"].append(pickOrigin)
    dest["airportCode"].append(pickDest)
    route = defaultdict(list)
    route["originAirport"].append(origin)
    route["destinationAirport"].append(dest)
    routeJSON = json.dumps(route)
    routeJSON = formatting(routeJSON)
    finalinput = json.loads(routeJSON)
    response = requests.post("http://localhost:9001/route", json=finalinput, headers = authHeader())

def addFlight():
    faker = Faker()
    route = requests.get("http://localhost:9001/route", headers = authHeader())
    airplane = requests.get("http://localhost:9001/airplane", headers = authHeader())
    routeJSON = route.json()
    airplaneJSON = airplane.json()
    routeList = []
    for r in range (len(routeJSON)):
        info = []
        info.append(routeJSON[r]["id"])
        info.append(routeJSON[r]["originAirportId"])
        info.append(routeJSON[r]["destinationAirportId"])
        routeList.append(info)

    airplaneList = []
    for a in range(len(airplaneJSON)):
        info = []
        info.append(airplaneJSON[a]["id"])
        info.append(airplaneJSON[a]["aTypeId"])
        airplaneList.append(info)
    pickAirplane = airplaneList[random.randint(0,len(airplaneList)-1)]
    pickRoute = routeList[random.randint(0,len(routeList)-1)]
    
    seatPrice = random.randint(80,300)

    capReq = requests.get("http://localhost:9001/airplanetype/" + str(pickAirplane[1]), headers = authHeader())
    capReq = capReq.json()
    capacity = capReq["capacity"]
    reserved_seats = random.randint(0,capacity)

    #only prints dates in the past-- would change if needed to be realistic, but for the purposes of adding data this is ok for now
    datetime = faker.date_time()

    flight = defaultdict(list)
    routeFormat = defaultdict(list)
    airplaneFormat = defaultdict(list)

    routeFormat["id"].append(pickRoute[0])
    routeFormat["originAirportId"].append(pickRoute[1])
    routeFormat["destinationAirportId"].append(pickRoute[2])
    airplaneFormat["id"].append(pickAirplane[0])
    airplaneFormat["aTypeId"].append(pickAirplane[1])
    flight["departure_time"].append(str(datetime))
    flight["reserved_seats"].append(reserved_seats)
    flight["seat_price"].append(seatPrice)
    flight["route"].append(routeFormat)
    flight["airplane"].append(airplaneFormat)

    flightJSON = json.dumps(flight)
    flightJSON = formatting(flightJSON)
    finalinput = json.loads(flightJSON)
    response = requests.post("http://localhost:9001/flight", json=finalinput, headers = authHeader())
addAirports()
for x in range (10):
    addType()
for x in range (10):
    addAirplane()
for x in range (10):
    addRoute()
for x in range (10):
    addFlight()