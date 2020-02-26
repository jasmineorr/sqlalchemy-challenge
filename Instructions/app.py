import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, render_template

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

#Routes

@app.route('/')
def index():
    return render_template('climate_index.html')

#precipitation for the last 12 months
@app.route('/api/v1.0/precipitation')
def precip():
    #find the most recent date in the database
    date = session.query(func.max(Measurement.date)).scalar()

    #subtract a year from it
    year = dt.timedelta(days=365)
    year_ago =  date - year

    #select only the date and precip values
    yr_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_ago).all()

    #convert the query results to a dict using date as the key and prcp as the value
    precipitation_dict = {}
    for rain in yr_prcp:
        precipitation_dict[str(rain.date)] = rain.prcp
    
    #return the json representation of the dict
    return jsonify(precipitation_dict)

#list of stations
@app.route('/api/v1.0/stations')
def stations():
    #get a list of all the stations
    stns_list = session.query(Station.station).all()

    #convert list of tuples into normal list
    stns_rav = list(np.ravel(stns_list))

    #return json representation of the list
    return jsonify(stns_rav)

#temperature observations for the last 12 months
@app.route('/api/v1.0/tobs')
def temp_obs():
    #find the most recent date in the db
    most_recent = session.query(func.max(Measurement.date)).scalar()

    #subtract a year from it
    year = dt.timedelta(days=365)
    year_ago =  most_recent - year

    #find the tobs for the last year
    yr_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > year_ago ).all()

    #convert list of tuples into normal list
    yr_tobs_rav = list(np.ravel(yr_tobs))

    #return json representation of the list
    return jsonify(yr_tobs_rav)

#find the temp min, max, and avg for a date range
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature(start=None, end=None):
    #when given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive'''
    if end != None:
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(msmt.date >= start).filter(Measurement.date <= end).all()
    #when given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    else:
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    #convert list of tuples into normal list
    temps_rav = list(np.ravel(temps))

    #return json representation of the list
    return jsonify(temps_rav)

if __name__ == '__main__':
    app.run(debug=False)

