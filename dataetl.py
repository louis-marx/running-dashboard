import os
import json
import urllib.request
import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st

def files_to_dataframe(folder):
    dir_list = os.listdir(folder)
    if ".DS_Store" in dir_list:
        dir_list.remove(".DS_Store")

    runs = []
    for file in dir_list:
        data = json.load(open(folder+"/"+file))
        run = [str(data['tags']['com.nike.name']),
                int(data['start_epoch_ms']),
                int(data['end_epoch_ms']),
                int(data['active_duration_ms']),
                str(data['tags']['com.nike.running.goaltype']),
                float(data['tags']['com.nike.temperature']),
                str(data['tags']['com.nike.weather']),
                int(data['tags']['rpe']),
                str(data['tags']['terrain'])]
            
        if 'com.nike.nrc.program.workout.title' in data['tags']:
            run.append(str(data['tags']['com.nike.nrc.program.workout.title']))
        else:
            run.append('')
        
        if 'com.nike.nrc.program.title' in data['tags']:
            run.append(str(data['tags']['com.nike.nrc.program.title']))
        else:
            run.append('')
        
        if 'com.nike.running.audioguidedrun.thumbnail' in data['tags']:
            urllib.request.urlretrieve(str(data['tags']['com.nike.running.audioguidedrun.thumbnail']), "thumbnails/" + os.path.splitext(file)[0] +".jpg")
        else:
            urllib.request.urlretrieve('https://picsum.photos/200', "thumbnails/" + os.path.splitext(file)[0] +".jpg")
        run.append(os.path.splitext(file)[0] +".jpg")

        summary = pd.DataFrame(data['summaries'])
        summary.sort_values("metric", inplace=True)
        summary = summary[summary.metric != "nikefuel"]["value"].tolist()
        runs.append(run+summary)

    runs = pd.DataFrame(runs, columns = ['name', 'start', 'end', 'duration', 'goaltype', 'temperature', 'weather', 'effort', 'terrain', 'program_type', 'program_name', 'thumbnail', 'ascent', 'calories', 'descent', 'distance', 'pace', 'speed', 'steps'])
    runs.start = pd.to_datetime(runs.start, unit='ms')
    runs.end = pd.to_datetime(runs.end, unit='ms')
    runs.duration = runs.duration / 60000

    runs['type'] = ''
    runs.loc[runs.goaltype.str.contains('speed'), 'type'] = 'speedrun'
    runs.loc[(runs.program_type.str.casefold() == 'long run') | runs.name.str.contains('Gratification'), 'type'] = 'longrun'
    runs.loc[runs.type == '', 'type'] = 'recoveryrun'

    runs['date'] = runs.start.dt.date
    runs['week'] = (runs.start.dt.isocalendar().week+13)%52
    runs['weekday'] = runs.start.dt.strftime('%A')
    runs['month'] = (runs.start.dt.month+15)%12
    runs['year'] = runs.start.dt.year
    runs['steps_per_minute'] = runs.steps / runs.duration
    runs['stride_length'] = 1000 * runs.distance / runs.steps

    return runs