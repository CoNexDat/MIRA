#!/usr/bin/env python
# coding: utf-8


from flask_wtf import FlaskForm as Form
from wtforms.widgets.html5 import NumberInput
from wtforms import TextField, SelectField, IntegerField, SubmitField
from wtforms.validators import (InputRequired, Email, NumberRange,
                                Length, Optional)


class IndexForm(Form):
    newMeasurement = SubmitField(label='Schedule new Measurement')


class ResultForm(Form):
    dates = SelectField(label='Change the selected date: ',
                        choices=[('0', '0')],
                        validators=[Optional()])
    dlScript = SelectField(label='Download Script: ',
                           choices=[('yes', 'Yes'), ('no', 'No')],
                           validators=[InputRequired()])
    dlMsmIds = SelectField(label='Measurement Ids: ',
                           choices=[('yes', 'Yes'), ('no', 'No')],
                           validators=[InputRequired()])
    dlLanet = SelectField(label='Lanet Network Graphs: ',
                          choices=[('yes', 'Yes'), ('no', 'No')],
                          validators=[InputRequired()])
    dlDegree = SelectField(label='Degree Distribution: ',
                           choices=[('yes', 'Yes'), ('no', 'No')],
                           validators=[InputRequired()])
    dlNeighbor = SelectField(label='Average Neighbor Degree: ',
                             choices=[('yes', 'Yes'), ('no', 'No')],
                             validators=[InputRequired()])
    dlCluster = SelectField(label='Clustering Coefficient: ',
                            choices=[('yes', 'Yes'), ('no', 'No')],
                            validators=[InputRequired()])
    dlHeatmaps = SelectField(label='Heatmaps: ',
                             choices=[('yes', 'Yes'), ('no', 'No')],
                             validators=[InputRequired()])
    dlAsns = SelectField(label='Autonomous system data: ',
                         choices=[('yes', 'Yes'), ('no', 'No')],
                         validators=[InputRequired()])
    dlProbes = SelectField(label='RIPE-Probe data: ',
                           choices=[('yes', 'Yes'), ('no', 'No')],
                           validators=[InputRequired()])
    dlEdges = SelectField(label='Autonomous system edgelst: ',
                          choices=[('yes', 'Yes'), ('no', 'No')],
                          validators=[InputRequired()])
    dlPaths = SelectField(label='Autonomous system paths: ',
                          choices=[('yes', 'Yes'), ('no', 'No')],
                          validators=[InputRequired()])
    changeDate = SubmitField(label='Select Date')
    download = SubmitField(label='Download')


class MeasurementForm(Form):
    numProbes = IntegerField(label='Sources: ', default=0,
                             validators=[InputRequired(), NumberRange(
                                 min=0, max=255)],
                             widget=NumberInput(min=0, max=255))
    numAsns = IntegerField(label='Targets: ', default=0,
                           validators=[InputRequired(), NumberRange(
                                 min=0)],
                           widget=NumberInput(min=0))
    repetition = IntegerField(label='Repetition of measurements: ',
                              default=1, validators=[
                                  InputRequired(), NumberRange(
                                      min=1, max=100)],
                              widget=NumberInput(min=1, max=100))
    concurrent = IntegerField(label='Concurrent measurements: ',
                              default=100, validators=[
                                  InputRequired(), NumberRange(
                                      min=1, max=2000)],
                              widget=NumberInput(min=1, max=2000))
    description = TextField(label='Description: ',
                            validators=[InputRequired(
                                message='Please enter a description')])
    protocol = SelectField(label='Protocol: ', choices=[('TCP', 'TCP'),
                                                        ('UDP', 'UDP'),
                                                        ('ICMP', 'ICMP')],
                           validators=[InputRequired()])
    packets = IntegerField(label='Packets: ', default=1,
                           validators=[InputRequired(), NumberRange(
                               min=1, max=16)],
                           widget=NumberInput(min=1, max=16))
    first_hop = IntegerField(label='First Hop: ', default=1,
                             validators=[InputRequired(), NumberRange(
                                 min=1, max=255)],
                             widget=NumberInput(min=1, max=255))
    max_hops = IntegerField(label='Max Hops: ', default=32,
                            validators=[InputRequired(), NumberRange(
                                min=1, max=255)],
                            widget=NumberInput(min=1, max=255))
    paris = IntegerField(label='Paris: ', default=1,
                         validators=[InputRequired(), NumberRange(
                             min=0, max=64)],
                         widget=NumberInput(min=0, max=64))
    bill_to = TextField(label='Billing address: ',
                        validators=[InputRequired(), Email(
                            message='Enter a valid email')])
    api_key = TextField(label='API-Key: ',
                        validators=[InputRequired(),
                                    Length(min=36, max=36,
                                           message='Enter a valid API-Key')])
    schedule = SelectField(label='Repeat every: ', choices=[('0', 'Never'),
                                                            ('7', 'Week'),
                                                            ('30', 'Month'),
                                                            ('365', 'Year')],
                           validators=[InputRequired()])
    startMeasurement = SubmitField(label='Schedule Measurements')
