import base64, os
from io import BytesIO
from scipy.signal import savgol_filter
from flask import Flask, jsonify
import matplotlib.pyplot as plt, pandas as pd, numpy as np
from hapke2 import app
from hapke2.cerebrum import utils, datainsights as di, preprocess as pp

global wsdata, df, df_raw, crop_df, n_wave, down_wave,down_refl, n_refl, min_wave, max_wave, crop_wave, crop_refl

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

def begin_fig(size):
    fig = plt.figure(figsize=size)
    ax = fig.subplots()
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
    global wsdata, df, df_raw,crop_df,  n_wave,n_refl, min_wave, max_wave
    wsdata = []
    figOb, axOb = begin_fig([6,4])
    inp_file = os.path.join(app.instance_path, 'user_files', 'input_file.txt')
    dq_insights_file = os.path.join(app.instance_path, 'ref_files', 'dq_insights.csv')
    df = pd.read_csv(inp_file, header=None, delimiter = "\s", names=['wave','refl','i','e','g'])
    df_raw = df.copy(deep=True)

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

    df.plot('wave', 'refl','scatter', ax=axOb, figsize=(5,4), fontsize=7, xlabel='wave(nm)')
    pImage =  print_figure(figOb)

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
    dq_results.append({'dp':'Total Unique i,e,g combinations', 'rslt':dqp['all_angles_cnt']})
    dq_results.append({'dp':'Data Process Satus Reccommendation', 'rslt':dqp['process_status']})

    jres = {'min_wave':min_wave, 'max_wave':max_wave,'img':pImage, 'wsdata':wsdata,
            'dq_str':dqp['message'],'dq_results':dq_results}
    
    return jsonify(jres)

def preprocess(fdata):
    global wsdata, df, df_raw, crop_df, n_wave, down_wave,down_refl, n_refl, min_wave, max_wave, crop_wave, crop_refl
    figOb_pp, axOb_pp = begin_fig([5,4])
    crop_refl = n_refl
    down_wave = n_wave 
    crop_min = min_wave
    crop_max = max_wave
    df = pp.init_process(df)
    df = pp.add_macro_surface_roughness(df)

    if fdata['crop']=='on':
        crop_min_inp = fdata['pp_crop_min_input']
        crop_max_inp = fdata['pp_crop_max_input']
        crop_min = min_wave if crop_min_inp is None or crop_min_inp == '' else float(crop_min_inp)
        crop_max = max_wave if crop_max_inp is None or crop_max_inp == '' else float(crop_max_inp)
        i1, i2 = utils.find_nearest(n_wave, crop_min), utils.find_nearest(n_wave, crop_max)

        crop_wave = n_wave[i1:i2+1]
        crop_refl = n_refl[i1:i2+1]

        crop_df = pd.DataFrame({'wave':crop_wave,'refl':crop_refl})
        print(crop_df.shape)
        crop_df.plot('wave', 'refl','scatter', ax=axOb_pp, figsize=(5,4), fontsize=7, xlabel='wave(nm)')


    if fdata['dwnsmpl']=='on':
        dwnsmpl_pts_inp = fdata['pp_dwnsmpl_input']
        dwnsmpl_pts = crop_df.shape[0] if dwnsmpl_pts_inp is None or dwnsmpl_pts_inp == '' else dwnsmpl_pts_inp

        down_wave = np.linspace(crop_min, crop_max, dwnsmpl_pts)
        down_refl = np.interp(down_wave, crop_wave, crop_refl)

    pImage =  print_figure(figOb_pp)

    # Load Workspace
    wsdata.append({'var':'wave', 'value': n_wave.shape, 'min':min_wave, 'max':max_wave})
    wsdata.append({'var':'new_wave', 'value': down_wave.shape, 'min':crop_min, 'max':crop_max})
    wsdata.append({'var':'new_refl', 'value': crop_refl.shape, 'min':crop_refl.min(), 'max':crop_refl.max()})

    jres = {'img':pImage, 'wsdata':wsdata}
    print(jres)
    return jsonify(jres)
