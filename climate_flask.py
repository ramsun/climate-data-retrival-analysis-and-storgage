'''
This file will use ORM to make queries to a sqlite database and post the results locally
using flask.

'''

# import dependencies
#SQL alchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import between

# flask dependencies
from flask import Flask, jsonify

# datetime dependencies
import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Home route
# All available routes are listed on the page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start]<br/>"
        f"/api/v1.0/[start]/[end]<br/>"
        f"NOTE: Enter [start] and [end] values as date strings in the %Y-%m-%d format"
    )

# Lists all the precipitation data from the database along with the associated dates
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_query = session.query(Measurement.date,Measurement.prcp).all()    
    
    prcp_dictionary_list = []
    for arow in prcp_query:
        prcp_dict = {}
        prcp_dict["date"] = arow.date
        prcp_dict["prcp"] = arow.prcp
        prcp_dictionary_list.append(prcp_dict)
    
    return jsonify(prcp_dictionary_list)

# Lists all weather stations within the dataset
@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(Station.station).all()    
    
    station_list = []
    for arow in station_query:
        station_list.append(arow.station)
    
    return jsonify(station_list)

# Lists the temperatures for the last year of data along with the associated 
@app.route("/api/v1.0/tobs")
def tobs():
    # query for the latest date in the database
    latest_date_max = session.query(func.max(Measurement.date)).scalar()
    # convert the latest date to a datetime object
    latest_date = dt.datetime.strptime(latest_date_max, '%Y-%m-%d').date()
    # use timedelta to find the date 1 year ago
    year_ago = latest_date - dt.timedelta(days=365)

    temperature_query = session.query(Measurement.date, Measurement.tobs).\
                        filter(between(Measurement.date, year_ago,latest_date))
    
    tobs_dictionary_list = []
    for arow in temperature_query:
        tobs_dict = {}
        tobs_dict["date"] = arow.date
        tobs_dict["tobs"] = arow.tobs
        tobs_dictionary_list.append(tobs_dict)
    
    return jsonify(tobs_dictionary_list)

# List the normals data for for a given start date through the max date in the database
@app.route("/api/v1.0/<start>")
def start_date_normals(start):
    # query for the latest date in the database
    latest_date_max = session.query(func.max(Measurement.date)).scalar()
    # convert the latest date to a datetime object
    latest_date = dt.datetime.strptime(latest_date_max, '%Y-%m-%d').date()
    
    tnormals_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date >= start)).\
        filter(Measurement.date <= latest_date).all()
    
    return jsonify(tnormals_query)

# List the normals data for for a given start date and end date given by the user
@app.route("/api/v1.0/<start>/<end>")
def start_to_end_date_normals(start, end):
    
    tnormals_start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    return jsonify(tnormals_start_query)

# Main
if __name__ == '__main__':
    # turn on debug mode
    app.run(debug=True)