#!/usr/bin/env python
# coding: utf-8


from crontab import CronTab
import json


def main(data, schedule):
    data_str = json.dumps(data)
    # create a new CronTab Job
    cron = CronTab(user=True)
    job = cron.new(command='main.py ' + '\'' + data_str + '\'',
                   comment=data.get('description'))
    job.setall('0 0 * * *')
    job.run()

    for result in cron.run_scheduler():
        print("This was printed to stdout by the process.")
