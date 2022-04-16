import base64, os
from io import BytesIO
from scipy.signal import savgol_filter
from flask import Flask, jsonify
import matplotlib.pyplot as plt, pandas as pd, numpy as np
from matplotlib import cm
import json
import plotly
import plotly.express as px
from hapke2 import app
from hapke2.cerebrum import utils, datainsights as di, preprocess as pp

global wsdata, df, df_raw, n_wave,n_refl, min_wave, max_wave, dqp
dq_insights_file = os.path.join(app.instance_path, 'ref_files', 'dq_insights.csv')

wsdata = []
def hello():
    # Generate the figure **without using pyplot**.
    # fig = Figure() -- had canvas error
    fig = plt.figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return jsonify(f"<img src='data:image/png;base64,{data}'/>")

def begin_fig(size, dim=2):
    if dim==2:
        fig = plt.figure(figsize=size)
        ax = fig.subplots()
    else:
        fig, ax = plt.subplots(figsize=size,subplot_kw={"projection": "3d"})
    return fig, ax

def print_figure(fig):
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


###############################################################################################
## BEGIN PROCESSING HERE
###############################################################################################

def read_input():
    global wsdata, df, df_raw, n_wave, n_refl, min_wave, max_wave, dqp
    wsdata = []
    
    inp_file = os.path.join(app.instance_path, 'user_files', 'input_file.txt')
    df = pd.read_csv(inp_file, header=None, delimiter = "\s", names=['wave','refl','i','e','g'])
    df_raw = df.copy(deep=True)

    df, dqp, n_wave, n_refl, i_array, e_array, g_array, min_wave, max_wave = check_dq(df, dq_insights_file)

    # Matplotlib -- version (2d,3d works)
    # figOb, axOb = begin_fig([6,4],3)
    # df.plot('wave', 'refl','scatter', ax=axOb, figsize=(5,4), fontsize=7, xlabel='wave(nm)')
    # pImage =  print_figure(figOb)

    # Try 3d plot
    # axOb.scatter(df.wave.values, df.refl.values, df.g.values, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    # axOb.set_xlabel('wave')
    # axOb.set_ylabel('refl')
    # axOb.set_zlabel('phase angle')
    # pImage =  print_figure(figOb)

    # Load Workspace
    wsdata.append({'var':'wave', 'value': n_wave.shape[0], 'min':round(min_wave,2), 'max':round(max_wave,2)})
    wsdata.append({'var':'refl', 'value': n_refl.shape[0], 'min':round(n_refl.min(),2), 'max':round(n_refl.max(),2)})
    wsdata.append({'var':'i_unique', 'value': int(dqp['i_count']), 'min':int(round(i_array.min(),2)), 'max':int(round(i_array.max(),2))})
    wsdata.append({'var':'e_unique', 'value': int(dqp['e_count']), 'min':int(round(e_array.min(),2)), 'max':int(round(e_array.max(),2))})
    wsdata.append({'var':'g_unique', 'value': int(dqp['g_count']), 'min':int(round(g_array.min(),2)), 'max':int(round(g_array.max(),2))})

    dq_results = []
    dq_results.append({'dp':'Data Quality on Wave(nm) - wave', 'rslt':dqp['wave_scenario']})
    dq_results.append({'dp':'Data Quality on Incident Angle(deg) - i', 'rslt':dqp['incident_angle_scenario']})
    dq_results.append({'dp':'Data Quality on Emission Angle(deg) - e', 'rslt':dqp['emmission_angle_scenario']})
    dq_results.append({'dp':'Data Quality on Phase Angle(deg) - g', 'rslt':dqp['phase_angle_scenario']})
    dq_results.append({'dp':'Data Quality on Opp. Surge', 'rslt':dqp['opp_surge_scenario']})
    dq_results.append({'dp':'Data Quality on Shadow Hiding - Bs', 'rslt':dqp['ext_bs_scenario']})
    dq_results.append({'dp':'Data Quality on Coherence Ratio - Bc', 'rslt':dqp['ext_coh_ratio_scenario']})
    dq_results.append({'dp':'Data Quality on Phase Angle Coverage (Need more than 27 percent filled)', 'rslt':dqp['g_covg']})
    dq_results.append({'dp':'Preprocess: Can crop?', 'rslt':dqp['scene'].pp_crop.values[0]})
    dq_results.append({'dp':'Total Unique i,e,g combinations', 'rslt':dqp['all_angles_cnt']})
    dq_results.append({'dp':'Data Process Satus Reccommendation', 'rslt':dqp['process_status']})

    plot_data = {'wave': df.wave.values.tolist(), 'refl': df.refl.values.tolist(), 'g': df.g.values.tolist()}
    jres = {'min_wave':min_wave, 'max_wave':max_wave, 'wsdata':wsdata,
            'dq_str':dqp['message'],'dq_results':dq_results, 'plot_data':plot_data}
    
    ret_rslt = jsonify(jres)
    return ret_rslt


def check_dq(df, dq_insights_file):
    #Add hash
    df = utils.add_hash(df, 'key')

    # DQ Validation:
    dqp = di.get_data_quality(df,dq_insights_file)

    n_wave = df.wave.to_numpy()
    n_refl = df.refl.to_numpy()
    i_array = df.i.to_numpy()
    e_array = df.e.to_numpy()
    g_array = df.g.to_numpy()
    min_wave, max_wave = n_wave.min(), n_wave.max()

    return df, dqp, n_wave, n_refl, i_array, e_array, g_array, min_wave, max_wave

def preprocess(fdata):
    global wsdata, df, df_raw, n_wave, n_refl, min_wave, max_wave, dqp
    figOb_pp, axOb_pp = begin_fig([5,4])
    crop_min = min_wave
    crop_max = max_wave
    df = pp.init_process(df)
    df = pp.add_macro_surface_roughness(df)
    df_raw = df.copy(deep=True)

    if fdata['crop']=='on' and dqp['scene'].pp_crop.values[0]=='yes':
        crop_min_inp = fdata['pp_crop_min_input']
        crop_max_inp = fdata['pp_crop_max_input']
        crop_min = min_wave if crop_min_inp is None or crop_min_inp == '' else float(crop_min_inp)
        crop_max = max_wave if crop_max_inp is None or crop_max_inp == '' else float(crop_max_inp)
        i1, i2 = utils.find_nearest(n_wave, crop_min), utils.find_nearest(n_wave, crop_max)

        # Copy to new n_wave - leave original as is....
        # For wave with no repeats - all the repeats are taken
        n_wave_pp = n_wave[i1:i2+1]
        min_wave, max_wave = n_wave_pp.min(), n_wave_pp.max()
        df = df[(df.wave>=min_wave)&(df.wave<=max_wave)]
    else:
        n_wave_pp = n_wave 

    df, dqp, n_wave, n_refl, i_array, e_array, g_array, min_wave, max_wave = check_dq(df, dq_insights_file)

    df.plot('wave', 'refl','scatter', ax=axOb_pp, figsize=(5,4), fontsize=7, xlabel='wave(nm)')
    pImage =  print_figure(figOb_pp)

    #######################
    # ieg not the same - sets of data in reflectance vs wavelength at each i/e/g
    # each set is downsampled the same way

    # Load Workspace
    wsdata.append({'var':'wave', 'value': n_wave.shape[0], 'min':round(min_wave,2), 'max':round(max_wave,2)})
    wsdata.append({'var':'refl', 'value': n_refl.shape[0], 'min':round(n_refl.min(),2), 'max':round(n_refl.max(),2)})
    wsdata.append({'var':'i_unique', 'value': int(dqp['i_count']), 'min':int(round(i_array.min(),2)), 'max':int(round(i_array.max(),2))})
    wsdata.append({'var':'e_unique', 'value': int(dqp['e_count']), 'min':int(round(e_array.min(),2)), 'max':int(round(e_array.max(),2))})
    wsdata.append({'var':'g_unique', 'value': int(dqp['g_count']), 'min':int(round(g_array.min(),2)), 'max':int(round(g_array.max(),2))})

    dq_results = []
    dq_results.append({'dp':'Data Quality on Wave(nm) - wave', 'rslt':dqp['wave_scenario']})
    dq_results.append({'dp':'Data Quality on Incident Angle(deg) - i', 'rslt':dqp['incident_angle_scenario']})
    dq_results.append({'dp':'Data Quality on Emission Angle(deg) - e', 'rslt':dqp['emmission_angle_scenario']})
    dq_results.append({'dp':'Data Quality on Phase Angle(deg) - g', 'rslt':dqp['phase_angle_scenario']})
    dq_results.append({'dp':'Data Quality on Opp. Surge', 'rslt':dqp['opp_surge_scenario']})
    dq_results.append({'dp':'Data Quality on Shadow Hiding - Bs', 'rslt':dqp['ext_bs_scenario']})
    dq_results.append({'dp':'Data Quality on Coherence Ratio - Bc', 'rslt':dqp['ext_coh_ratio_scenario']})
    dq_results.append({'dp':'Data Quality on Phase Angle Coverage (Need more than 27 percent filled)', 'rslt':dqp['g_covg']})
    dq_results.append({'dp':'Preprocess: Can crop?', 'rslt':dqp['scene'].pp_crop.values[0]})
    dq_results.append({'dp':'Total Unique i,e,g combinations', 'rslt':dqp['all_angles_cnt']})
    dq_results.append({'dp':'Data Process Satus Reccommendation', 'rslt':dqp['process_status']})

    jres = {'img':pImage, 'wsdata':wsdata, 'dq_str':dqp['message'],'dq_results':dq_results, 'guess_permission':dqp['process_status']}
    
    return jsonify(jres)

