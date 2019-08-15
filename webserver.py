#!/usr/bin/env python
# coding: utf-8


from werkzeug.datastructures import CallbackDict
from flask import (Flask, render_template, flash, redirect, url_for, request,
                   session, Response)
from flask.sessions import SessionInterface, SessionMixin
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from forms import IndexForm, MeasurementForm, ResultForm
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask_pymongo import PyMongo
from gridfs import GridFS
from threading import Thread
from bson.json_util import dumps
from datetime import datetime
import json
import zipfile
import io
import os
import shutil
import schedule_measurements


# App config
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/conexdat-db'
Bootstrap(app)

# Mongo config
mongo = PyMongo(app)
coll = mongo.db.dates
tracerouteColl = mongo.db.traceroutes
asnColl = mongo.db.asns
probeColl = mongo.db.probes
edgeColl = mongo.db.edges
fs = GridFS(mongo.db)
measurementDates = sorted([
    (str(item), datetime.strptime(str(item), '%Y%m%d').strftime("%d %b %Y"))
    for item in coll.distinct('date')], reverse=True)

# Nav config
nav = Nav()
topbar = Navbar('',
                View('Home', 'index'),
                View('Results', 'showResults', date=measurementDates[0][0]),
                View('Schedule new Measurements', 'getMeasurementInput'))
nav.register_element('top', topbar)


class ItsdangerousSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.modified = False


class ItsdangerousSessionInterface(SessionInterface):
    salt = 'cookie-session'
    session_class = ItsdangerousSession

    def get_serializer(self, app):
        if not app.secret_key:
            return None
        return URLSafeTimedSerializer(app.secret_key,
                                      salt=self.salt)

    def open_session(self, app, request):
        s = self.get_serializer(app)
        if s is None:
            return None
        val = request.cookies.get(app.session_cookie_name)
        if not val:
            return self.session_class()
        max_age = app.permanent_session_lifetime.total_seconds()
        try:
            data = s.loads(val, max_age=max_age)
            return self.session_class(data)
        except BadSignature:
            return self.session_class()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        expires = self.get_expiration_time(app, session)
        val = self.get_serializer(app).dumps(dict(session))
        response.set_cookie(app.session_cookie_name, val,
                            expires=expires, httponly=True,
                            domain=domain)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = IndexForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        return redirect(url_for('getMeasurementInput'))

    return render_template('index.html', form=form,
                           timelineData=measurementDates)


@app.route('/results/<date>', methods=['GET', 'POST'])
def showResults(date):
    form = ResultForm(request.form)
    form.dates.choices = [(k, v) for k, v in measurementDates]

    # define the names for the graphics of the selected date
    imageNames = {
        'lanet_v4': date + '_edgelist_v4.png',
        'lanet_v6': date + '_edgelist_v6.png',
        'degree_v4': date + '_degree_distribution_v4.png',
        'degree_v6': date + '_degree_distribution_v6.png',
        'avg_neighbor_v4': date + '_avg_neighbor_v4.png',
        'avg_neighbor_v6': date + '_avg_neighbor_v6.png',
        'cluster_v4': date + '_cluster_v4.png',
        'cluster_v6': date + '_cluster_v6.png',
        'heatmap_v4': date + '_heatmap_v4.png',
        'heatmap_v6': date + '_heatmap_v6.png'
    }

    try:
        form.dlScript.data = session['dlScript']
    except KeyError:
        print('no saved value for dlScript found')

    if form.validate_on_submit() and form.changeDate.data:
        print('here')
        return redirect(url_for('showResults', date=form.dates.data))

    elif form.validate_on_submit() and form.download.data:
        # create temporary dir for the .json-files
        os.makedirs('downloads/files/')

        # create .json-files to download depending on input
        if request.form['dlMsmIds'] == 'yes':
            getMeasurementIds(tracerouteColl, date)
        if request.form['dlLanet'] == 'yes':
            getDlImg(imageNames['lanet_v4'])
            getDlImg(imageNames['lanet_v6'])
        if request.form['dlDegree'] == 'yes':
            getDlImg(imageNames['degree_v4'])
            getDlImg(imageNames['degree_v6'])
        if request.form['dlNeighbor'] == 'yes':
            getDlImg(imageNames['avg_neighbor_v4'])
            getDlImg(imageNames['avg_neighbor_v6'])
        if request.form['dlCluster'] == 'yes':
            getDlImg(imageNames['cluster_v4'])
            getDlImg(imageNames['cluster_v6'])
        if request.form['dlHeatmaps'] == 'yes':
            getDlImg(imageNames['heatmap_v4'])
            getDlImg(imageNames['heatmap_v6'])
        if request.form['dlAsns'] == 'yes':
            getDlData(asnColl, date)
        if request.form['dlProbes'] == 'yes':
            getDlData(probeColl, date)
        if request.form['dlEdges'] == 'yes':
            getDlData(edgeColl, date)
        if request.form['dlPaths'] == 'yes':
            try:
                shutil.copy('paths/' + date + '_paths_v4.csv',
                            'downloads/files/')
            except Exception:
                print('No IPv4 Paths found')
            try:
                shutil.copy('paths/' + date + '_paths_v6.csv',
                            'downloads/files/')
            except Exception:
                print('No IPv6 Paths found')
        # write .json-files into zipfile and make it accesible for Respone()
        data = io.BytesIO()
        with zipfile.ZipFile(data, 'w') as z:
            for file in os.listdir('downloads/files/'):
                z.write('downloads/files/' + file)
            # add dlScript, if selected
            if request.form['dlScript'] == 'yes':
                for file in os.listdir('downloads/'):
                    z.write('downloads/' + file)
        data.seek(0)

        # delete the directory
        shutil.rmtree('downloads/files/')

        # save the dlScript value into the session
        session['dlScript'] = request.form['dlScript']

        # return the zip-File as a Download
        return Response(data, mimetype='application/zip',
                        headers={
                            'Content-Disposition':
                            'attachment;filename=%smeasurementData.zip' % date
                        })

    return render_template('results.html', form=form, **imageNames,
                           date=datetime.strptime(date, '%Y%m%d').strftime(
                               "%d %b %Y"))


@app.route('/scheduling', methods=['GET', 'POST'])
def getMeasurementInput():
    form = MeasurementForm(request.form)
    data = {}
    try:
        form.description.data = session['description']
    except KeyError:
        print('no description found')
    try:
        form.bill_to.data = session['bill_to']
    except KeyError:
        print('no billing address found')
    try:
        form.api_key.data = session['api_key']
    except KeyError:
        print('no api-key found')
    print(form.errors)

    if form.validate_on_submit():
        data = {
            'numProbes': request.form['numProbes'],
            'numAsns': request.form['numAsns'],
            'repetition': request.form['repetition'],
            'concurrent': request.form['concurrent'],
            'description': request.form['description'],
            'protocol': request.form['protocol'],
            'packets': request.form['packets'],
            'first_hop': request.form['first_hop'],
            'max_hops': request.form['max_hops'],
            'paris': request.form['paris'],
            'bill_to': request.form['bill_to'],
            'api_key': request.form['api_key']}
        schedule = request.form['schedule']

        session['description'] = request.form['description']
        session['bill_to'] = request.form['bill_to']
        session['api_key'] = request.form['api_key']

        Thread(target=schedule_measurements.main,
               args=(data, schedule)).start()
        flash('Your Measurement ' + data.get('description')
              + " was scheduled on the server."
              + 'It will take several hours until the results are available.')

        return redirect(url_for('index'))

    return render_template('scheduling.html', form=form)


@app.route('/images/<filename>')
def image(filename):
    gridout = fs.get_last_version(filename=filename).read()
    Response.content_type = 'image/jpeg'
    return gridout


# method that writes the data of a specific date from a passed collection
# to .json-files
def getDlData(coll, date):
    content = dumps(coll.find({'schedule_date': {'$in': [date]}}, {'_id': 0}))
    file = open('downloads/files/' + coll.full_name[12:] + '.json', 'w')
    file.write(content)


# method that gets the images of a specific date over GridFS
def getDlImg(imgName):
    try:
        img = fs.get_last_version(filename=imgName).read()
        file = open('downloads/files/' + imgName, 'wb')
        file.write(img)
    except Exception:
        print('No Image found for ' + imgName)


# method that writes the measurement ids of a specific date into json
def getMeasurementIds(coll, date):
    content = dumps(coll.find({'schedule_date': {'$in': [date]}},
                              {'_id': 0, 'msm_id': 1}))
    file = open('downloads/files/measurementIds.json', 'w')
    file.write(content)


# activate session interface
app.session_interface = ItsdangerousSessionInterface()
# activate the navbar
nav.init_app(app)


if __name__ == "__main__":
    app.run()
