import pandas as pd

def get_wave_char(df):
    wave_scenario = 0

    ws=df.wave.unique()
    if len(ws) == df.shape[0] and len(ws)>3: # len=4, w1,w2,w3,w4 ws=3
        wave_scenario = 3
        return wave_scenario,'Data at different wavelengths with *no* wavelength repeated'
    elif len(ws)==1: # len-4, w1,w1,w1,w1, ws=1
        wave_scenario = 1
        return wave_scenario,'Data at same wavelength'
    elif len(ws) < df.shape[0] and len(ws)>3: #len=4, w1,w2,w1,w2 ws=2
        wave_scenario = 2
        return wave_scenario,'Data at different wavelengths with wavelength repeated'
    else:
        return wave_scenario,'Unidentified wavelength characteristic' #ws=0 -- badddd data
    

def get_g_char(df):
    phase_angle_scenario = 0

    if len(df.g.unique()) == df.shape[0]: # len=4, w1,w2,w3,w4 ws=3
        phase_angle_scenario = 3
        return phase_angle_scenario,'Data at different phase angles with *no* phase angles repeated'
    elif len(df.g.unique())==1 and df.shape[0]>1: # len-4, w1,w1,w1,w1, ws=1
        phase_angle_scenario = 1
        return phase_angle_scenario,'Data at same Phase Angle'
    elif len(df.g.unique()) < df.shape[0]: #len=4, w1,w2,w1,w2 ws=2
        phase_angle_scenario = 2
        return phase_angle_scenario,'Data at different phase angles with phase angles repeated'
    else:
        return phase_angle_scenario,'Unidentified phase angle characteristic' #ws=0 -- badddd data
    
def get_i_char(df):
    inc_angle_scenario = 0

    if len(df.i.unique()) == df.shape[0]: # len=4, w1,w2,w3,w4 ws=3
        inc_angle_scenario = 3
        return inc_angle_scenario,'Data at different incident angles with *no* incident angles repeated'
    elif len(df.i.unique())==1 and df.shape[0]>1: # len-4, w1,w1,w1,w1, ws=1
        inc_angle_scenario = 1
        return inc_angle_scenario,'Data at same incident angle'
    elif len(df.i.unique()) < df.shape[0]: #len=4, w1,w2,w1,w2 ws=2
        inc_angle_scenario = 2
        return inc_angle_scenario,'Data at different incident angles with incident angles repeated'
    else:
        return inc_angle_scenario,'Unidentified incident angle characteristic' #ws=0 -- badddd data
    
def get_e_char(df):
    em_angle_scenario = 0
    if len(df.e.unique()) == df.shape[0]: # len=4, w1,w2,w3,w4 ws=3
        em_angle_scenario = 3
        return em_angle_scenario,'Data at different emission angles with *no* emission angles repeated'
    elif len(df.e.unique())==1 and df.shape[0]>1: # len-4, w1,w1,w1,w1, ws=1
        em_angle_scenario = 1
        return em_angle_scenario,'Data at same emission angle'
    elif len(df.e.unique()) < df.shape[0]: #len=4, w1,w2,w1,w2 ws=2
        em_angle_scenario = 2
        return em_angle_scenario,'Data at different emission angles with emission angles repeated'
    else:
        return em_angle_scenario,'Unidentified emission angle characteristic' #ws=0 -- badddd data

def get_opp_surge_char(df):
    opp_surge_scenario = 0 # not working
    g_s=df.g.unique()
    if len(g_s[g_s<15])>1 and len(g_s) > 1:
        opp_surge_scenario = 2
        return opp_surge_scenario,'Found unique data points in opposition surge at low phase angles:'
    elif len(g_s[g_s<15])==1 and len(g_s) > 2:
        opp_surge_scenario = 3
        return opp_surge_scenario,'Found unique data points in opposition surge at low phase angles, but only one'
    elif len(g_s[g_s<15]) < 1:
        opp_surge_scenario = 1
        return opp_surge_scenario,'You do not have sufficient data in opposition surge at low phase angle. (Min: 2 data points)'
    else:
        return opp_surge_scenario,'Unidentified opposition surge characteristics' #ws=0 -- badddd data

# Here is where the user gets to decide a few things
# 1 is data at same
# 2 is data at different with no repeats
# 3 is data at different with repeats
def get_data_quality(df):
    data_quality = 0

    wave_scenario, _wstr = get_wave_char(df)
    phase_angle_scenario, _pgstr = get_g_char(df)
    inc_angle_scenario, _istr = get_i_char(df)
    em_angle_scenario, _estr = get_e_char(df)
    opp_surge_scenario, _oppstr = get_opp_surge_char(df)

    dqp = ((wave_scenario, _wstr),(phase_angle_scenario, _pgstr),(inc_angle_scenario, _istr),
          (em_angle_scenario, _estr),(opp_surge_scenario, _oppstr))

    ks = df.key.unique()
    if len(ks) > 3 and wave_scenario == 2 and opp_surge_scenario == 2:
        data_quality = 2
        return dqp, data_quality, 'Data quality is great, you may proceed with all options'
    elif len(ks) > 3 and wave_scenario == 1 and opp_surge_scenario == 2:
        data_quality = 3
        return dqp, data_quality, 'Data quality is good, you may proceed with all options, but multiple wavelengths is advised for constraining macroscopic surface roughness'
    elif len(ks) > 3 and wave_scenario in [3,1] and opp_surge_scenario == 1:
        data_quality = 4
        return dqp, data_quality, 'Data quality is ok but lacking in points in opposition surge region, calculating shadow hiding is not advised'
    elif phase_angle_scenario == 1 and len(ks) > 3:
        data_quality = 1
        return dqp, data_quality, 'Data quality is ok but lacking in multiple phase angles data, calculating shadow hiding, marcoscopic surface roughness, phase function, and coherence is not advised'
    elif len(ks) < 3:
        data_quality = 5
        return dqp, data_quality, 'Data quality is bad, it is lacking in multiple phase angles, input angles, and emission angles calculating shadow hiding, marcoscopic surface roughness, and coherence is not advised'
    else:
        return dqp, data_quality, 'Data quality could not be analyzed. Please re-evaluate data set or proceed with caution'
