# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

recent_date = session.query(Measurement).order_by(desc(Measurement.date)).first()
#the result from the above query gives the following date: 2017-08-23

last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome(): 
    return(
        f"Welcome to my Module 10 API SQLite Connection & Landing Page!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precepitation-data                  list of precepitation data for the last 12 Months"
        f"/api/v1.0/sations                             list of all the stations in the database"
        f"/api/v1.0/tobs                                data for the most active station"
        f"/api/v1.0/datesearch/<startDate               provide a start date in URL"
        f"api/v1.0/datesearch/<startDate>/<endDate>     provide start and end date to retrive min, max temper"
    )

@app.route("/api/v1.0/precepitation-data")
def precepitation():
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_12_months).order_by(Measurement.date).all()

    precip_data = []
    for result in data:
        precip_dict = {result.date: result.prcp}
        precip_data.append(precip_dict)

    return jsonify(precip_data)

@app.route("/api/v1.0/sations")
def stations():
    results = session.query(Station.station).all()
    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    data = session.query(Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= last_12_months).all()
    active_station_data = list(np.ravel(data))

    return jsonify(active_station_data)


@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate).group_by(Measurement.date).all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate).filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate).group_by(Measurement.date).all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)