import os
import json
import requests
import pytz
from datetime import datetime , timedelta
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

def getDate():
    return (datetime.now().date() ).strftime("%Y%m%d")

def formatLocation(lat,long):
    return "{}:{}:EPSG:4326".format(long,lat)
    

def formatDate(date):
    # Sample date string
    date_string = date

    # Parse the date string into a datetime object
    dt_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")

    # Define Sydney timezone (UTC+10) or in can use timedelta(hours=10 and add it to the dt_object)
    sydney_timezone = pytz.timezone('Australia/Sydney')

    # Convert UTC datetime object to Sydney time
    dt_sydney = dt_object.replace(tzinfo=pytz.utc).astimezone(sydney_timezone)

    # Format the datetime object into the desired format
    formatted_date = dt_sydney.strftime('%Y-%m-%d %I:%M:%S %p')
    return formatted_date


def formatTimeTaken(sec):
    hoursTaken = sec // 3600
    remaining_seconds = sec % 3600
    minutesTaken = remaining_seconds // 60
    secondsTaken = remaining_seconds % 60 
    return "{} hours {} minutes {} seconds".format(hoursTaken,minutesTaken,secondsTaken)

def fromatResponse(response):
    # startingPoint = response.journeys[journey].origin.name
    journeys = [] 
    for journey in range(len(response['journeys'])):
        routes=[]
        totalTimeForTrip=0
        for i in range(len(response['journeys'][journey]['legs'])):
            # departureTime = response['journeys'][journey]['legs'][i]['origin']['departureTimeBaseTimetable']
            plannedDepartureTime = response['journeys'][journey]['legs'][i]['origin']['departureTimePlanned']
            realTimeDepartureTime = response['journeys'][journey]['legs'][i]['origin']['departureTimePlanned']
            # arrivalTime = response['journeys'][journey]['legs'][i]['destination']['arrivalTimeBaseTimetable']
            plannedArrivalTime = response['journeys'][journey]['legs'][i]['destination']['arrivalTimePlanned']
            realTimeArrivalTime = response['journeys'][journey]['legs'][i]['destination']['arrivalTimeEstimated']
            timeTaken=response['journeys'][journey]['legs'][i]['duration']
            totalTimeForTrip = response['journeys'][journey]['legs'][i]['duration'] + totalTimeForTrip
            coords = { 
                        "from" : response['journeys'][journey]['legs'][i]['origin']['name'],
                        # "departure Time": formatDate(departureTime),
                        "planned Departure Time" : formatDate(plannedDepartureTime),
                        "realtime Departure Time" : formatDate(realTimeDepartureTime),
                        "to": response['journeys'][journey]['legs'][i]['destination']["name"],
                        "timeTaken" : formatTimeTaken(timeTaken),
                        # "arrival Time": formatDate(arrivalTime),
                        "planned arrival Time" : formatDate(plannedArrivalTime),
                        "realtime arrival Time" : formatDate(realTimeArrivalTime),
                        
                        
                    }
            if 'disassembledName' in response['journeys'][journey]['legs'][i]['transportation'] :
                coords['on'] = response['journeys'][journey]['legs'][i]['transportation']['disassembledName']
            else :
                coords['on'] = response['journeys'][journey]['legs'][i]['transportation']['product']['name']
        
            routes.append(coords)
        
    
        journeys.append(routes)
        journeys[journey][0]['info']= {"totalOnTrasnportDuration": formatTimeTaken(totalTimeForTrip),}

        

       

    return json.dumps(journeys,indent=4)

def create_html_table(data):
    data = json.loads(data)
    html=""
    for i , leg in enumerate(data):
     
        html += f"<h1>journey no: {i + 1}<h1>"
        html += "<table border='1'><tr></th><th> From </th><th> To </th><th> Realtime Departure </th><th> Departure </th><th> Duration </th><th> Arrival </th><th> Realtime Arrival </th><th> On </th><th> Journey Duration </th></tr>"
        for step in leg:
            html += "<tr>"
            html += f"<td> {step['from']} </td>"
            html += f"<td> {step['to']} </td>"
            html += f"<td> {step.get('planned Departure Time', '')} </td>"
            html += f"<td> {step.get('realtime Departure Time', '')} </td>"
            html += f"<td> {step['timeTaken']} </td>"
            html += f"<td> {step.get('planned arrival Time', '')} </td>"
            html += f"<td> {step.get('realtime arrival Time', '')} </td>"
            html += f"<td> {step['on']} </td>"
            if 'info' in step and 'totalOnTrasnportDuration' in step['info']:
                html += f"<td> {step['info']['totalOnTrasnportDuration']} </td>"
            else:
                html += "<td></td>"
            html += "</tr>"
        html += "</tr>"
        html += "</table>"

    return html






    
def get_route():
    # Specify parameters for the trip request
    arrivalDate = getDate()
    params = {
    "type_origin": "coord",
    "name_origin": "151.1545913816247:-33.914322087809346:EPSG:4326",
    "name_destination": formatLocation(-33.96602210082954, 151.04066738332494),
    "type_destination":'coord',
    "depArrMacro" : "arr",
    "itdDate" : arrivalDate,
    "itdTime" : "0900",
    "outputFormat" : "rapidJSON",
    "coordOutputFormat" : "EPSG:4326",
    }
    headers ={
    "Authorization": TRANSPORT_NSW_API,
    }
    try:
        response  = requests.get("https://api.transport.nsw.gov.au/v1/tp/trip",params=params,headers=headers)
        data = response.json()
        return fromatResponse(data)
    except Exception as e:
        print(e)
        return "error"
    
def sendEmail(message):
    message = Mail(
    from_email='nembangd0@gmail.com',
    to_emails='diwashnembang0@gmail.com',
    subject='Your route to work',
    html_content='<pre>{}</pre>'.format(message))
    try:
        sg = SendGridAPIClient(SEND_GRID_API)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e.message)

def run():
    journeys = get_route()
    if(journeys == "error"): return 
    tabel = create_html_table(journeys)
    # print(tabel)
    sendEmail(tabel)



TRANSPORT_NSW_API = os.getenv('TRANSPORT_NSW_API')
SEND_GRID_API = os.getenv('SEND_GRID_API')
origin = "-33.914322087809346,151.1545913816247"
destination = "-33.96602210082954,151.04061373929883"



if __name__ == "__main__" : 
    run()