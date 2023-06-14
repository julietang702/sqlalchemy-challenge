# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
app = Flask(__name__)

#connect to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

base = automap_base()
# reflect the tables
base.prepare(engine, reflect = True)
#Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station
#Create link from python to DB
session = Session(engine)

#home route
@app.route("/")
def home():
    return (
        "<div style='text-align: center;'>"
        "<h2>Welcome to the Hawaii Climate Analysis API</h2>"
        "<h3>Select from one of the available routes:</h3>"
        "<p>/api/v1.0/precipitation</p>"
        "<p>/api/v1.0/stations</p>"
        "<p>/api/v1.0/tobs</p>"
        "<p>/api/v1.0/start/end</p>"
        "</div>"
    )

@app.route("/api/v1.0/precipitation  ")
def precip():
    #calcualate the date one year from the last data in the data set
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #perform a query to retrieve the data and scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= previousYear).all()

    session.close()

    #dictonary with the date as the key and the precipitation scores
    precipitation = {date: prcp for date, prcp in results}

    #convert to json
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    #show a list of stations
    #retrieve names of the stations
    results = session.query(Station.station).all()
    session.close()
    
    stationList = list(np.ravel(results))

    # convert to a json and display
    return jsonify(stationList)

#/api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    #return previous year temps
    #calc the date one year from the last date in data set
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #perform a query to retrieve the temp from the most active
    results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= previousYear).all()
    session.close()

    TemperatureList = list(np.ravel(results))

    #return the list

    return jsonify(TemperatureList)

#start/end
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None,end=None):
    #select statement
    selection = [func,min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    if not end: 
        startDate = dt.datetime.strptime(start, "%m,%d,%Y")
        results= session.query(*selection).filter(Measurement.date >= startDate).all()
        session.close()
        temperatureList = list(np.ravel(results))

        #return temp
        return jsonify(temperatureList)

    else: 
        startDate = dt.datetime.strptime(start, "%m,%d,%Y")
        endDate = dt.datetime.strptime(start, "%m,%d,%Y")

        results= session.query(*selection)\
            .filter(Measurement.date >= startDate)\
            .filter(Measurement.date >= endDate).all()
        session.close()
        temperatureList = list(np.ravel(results))


        # app launcher
if __name__ == '__main__':
    app.run(debug=True)


