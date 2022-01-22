import pandas as pd
from fractions import Fraction

N_UNIQUE_POINTS = 3
OPP_SURGE_CUT_OFF_DEG = 15
OPP_SURGE_POINTS = 2

def get_data_quality(df, lkp_file):

    # There are six different scenarios to consider
    # Wave Scenario, Phase Angle, Incident Angle, Emmission Angle options: same, diff_no_reps, diff_reps
    # All Angles Count: Total count of different i,e,g combinations - determined by n
    # Opp_surge_scenario: surge_cnt_not_met, surge_cnt_met (when #g < 15 degrees is more than 2 points)
    wave_scenario, all_angles_cnt, incident_angle_scenario, emmission_angle_scenario, phase_angle_scenario, opp_surge_scenario= None, None, None, None, None, None 

    # Count of variable, and flag if its repeated
    wave_unique = df.wave.unique()
    w_cnt, w_is_rep = len(wave_unique), len(wave_unique)<df.shape[0]

    # Checking nature of wavelength in the data points.
    # w_cnt == 1 - all datapoints have the same wavelength (A phase curve at a single wavelength)
    # w_cnt > 1 and w_is_rep != 1 - all data points have different wavelengths (Full spectrum at a single phase angle)
    # w_cnt > 1 and w_is_rep == 1 - data points have more than 1 group of wavelengths. (Spectra at multiple phase angles)
    if w_cnt == 1:
        wave_scenario = 'same'
    elif w_cnt > 1 and w_is_rep != 1:
        wave_scenario = 'diff_no_reps'
    elif w_cnt > 1 and w_is_rep == 1: 
        wave_scenario = 'diff_reps'
    else:
        wave_scenario = None

    i_unique = df.i.unique()
    i_cnt, i_is_rep = len(i_unique), len(i_unique)<df.shape[0]

    # Checking nature of Incident Angle in the data points.
    # i_cnt == 1 - all datapoints have the same Incidence angle (But Emission angle can change)
    # i_cnt > 1 and i_is_rep ! - all data points have different Incidence angles 
    # i_cnt > 1 and i_is_rep == 1 - data points have more than 1 group of Incidence angles. 
    if i_cnt == 1:
        incident_angle_scenario = 'same'
    elif i_cnt > 1 and i_is_rep != 1:
        incident_angle_scenario = 'diff_no_reps'
    elif i_cnt > 1 and i_is_rep == 1: 
        incident_angle_scenario = 'diff_reps'
    else:
        incident_angle_scenario = None

    e_unique = df.e.unique()
    e_cnt, e_is_rep = len(e_unique), len(e_unique)<df.shape[0]

    # Checking nature of Incident Angle in the data points.
    # e_cnt == 1 - all datapoints have the same Emission angle (But Incidence angle can change)
    # e_cnt > 1 and e_is_rep ! - all data points have different Emission angles 
    # e_cnt > 1 and e_is_rep == 1 - data points have more than 1 group of Emission angles.
    if e_cnt == 1:
        emmission_angle_scenario = 'same'
    elif e_cnt > 1 and e_is_rep != 1:
        emmission_angle_scenario = 'diff_no_reps'
    elif e_cnt > 1 and e_is_rep == 1: 
        emmission_angle_scenario = 'diff_reps'
    else:
        emmission_angle_scenario = None

    g_unique = df.g.unique()
    g_cnt, g_is_rep = len(g_unique), len(g_unique)<df.shape[0]

    # Checking nature of Phase Angle in the data points.
    # g_cnt == 1 - all datapoints have the same Phase angle (But Incidence and Emission angle can change)
    # g_cnt > 1 and g_is_rep ! - all data points have different Phase angles (But Incidence and Emission can be the same)
    # g_cnt > 1 and g_is_rep == 1 - data points have more than 1 group of Phase angles
    if g_cnt == 1:
        phase_angle_scenario = 'same'
    elif g_cnt > 1 and g_is_rep != 1:
        phase_angle_scenario = 'diff_no_reps'
    elif g_cnt > 1 and g_is_rep == 1: 
        phase_angle_scenario = 'diff_reps'
    else:
        phase_angle_scenario = None

    # All Angles Count
    # Identifies unique sets of i/e/g combinations
    # This lets us determine how complete our phase angle coverage is 
    # To see if we have enough information to solve for phase dependent quantities
    # - Phase function requires g spans the entire range
    # - SHOE requires points at low phase angles (< 15 degrees)
    # - CBOE requires points at very low phase angles (< 2 degrees)
    # - Surface Roughness - Multiple wavelengths are advised to calculate surface roughness
    ks = df.key.unique()
    all_angles_cnt = 'more_than_n' if len(ks) > N_UNIQUE_POINTS else 'less_than_n'

    # Checking to ensure, data points are available to calculate shadow hiding
    g_in_opp_surge_region = g_unique[g_unique < OPP_SURGE_CUT_OFF_DEG]
    opp_surge_cnt = len(g_in_opp_surge_region)
    opp_surge_scenario = 'surge_cnt_not_met' if opp_surge_cnt < OPP_SURGE_POINTS else 'surge_cnt_met'

    # We check two regions, to ensure we can constrain the shadow hiding curve
    # atleast 1 in 0-10/10-15 range
    g_cnt_bs_rng_1 = len(g_unique[g_unique < 10])
    g_cnt_bs_rng_2 = len(g_unique[(g_unique >= 10) & (g_unique < 15)])
    ext_bs_scenario = 'Sufficient Data for Shadow Hiding' if g_cnt_bs_rng_1 >=1 and g_cnt_bs_rng_2 >= 1 else 'Insufficient Data points for Shadow Hiding'

    # We check to ensure data points are available to calculate - Coherent Backscatter
    # atleast 2 less then 2
    g_cnt_bc_rng_1 = len(g_unique[g_unique < 2])
    ext_coh_ratio_scenario = 'Sufficient Data for Coherence Ratio' if g_cnt_bc_rng_1 >=1 else 'Insufficient Data points for Coherence Ratio'

    # How well will our phase angle be constrained 
    # >27% of data blocks split through entire phase range is ideal
    ## Find Phase Angle Extended Scenario
    ## Display it as Phase Angle Coverage: More than 27% filled, or not filled
    ## Ask Eli How to Display
    is_g_suff = True 
    wave_pass_dict = {}
    # This grabs a wavelength block - if there is more than 1 block of wavelength
    # Dataset: w1,w1,w1,w2,w2,w2,w3,w3,w4,w4
    # wave_unique: w1,w2,w3,w4 || df_t collects each wavelength block temporarily
    # df_t (dataframe_temp): [w1,w1,w1] | 2nd iter: [w2,w2,w2]........
    # It checks for unique phase angle in each wavelength
    for w in wave_unique:
        df_t = df[df.wave==w]
        g_ = df_t.g.unique()
        bkt_list = []
        # Split the dataset in buckets of range 10 degrees
        # 180 degrees - in ranges of 10 is 18 buckets
        # 27% filled of 18 is rounded to 5
        for gg in g_:
            bkt_list.append(gg//10)
        bkt_set = set(bkt_list)
        wave_pass = len(bkt_set)>=5 
        wave_pass_dict[w] = (wave_pass,bkt_set)
        is_g_suff = is_g_suff & wave_pass

    # Now cut by ieg - check for minimum of 10 points and also all cuts must have same points
    # This decides smoothening and downsample

    # Load the Data Quality Insights File
    # After calculating the different flags for input data as above
    # They are looked up the DQ Insights file loaded below
    # For each possible, valid combination of input data flags, the file returns a processing status
    # The processing status determines the valid input values that are enabled on the Front-End Webpage
    lkp = pd.read_csv(lkp_file)
    scene = lkp[(lkp.wave_scenario==wave_scenario) & (lkp.all_angles_cnt==all_angles_cnt) & (lkp.incident_angle_scenario==incident_angle_scenario) & (lkp.emmission_angle_scenario==emmission_angle_scenario) & (lkp.phase_angle_scenario==phase_angle_scenario) & (lkp.opp_surge_scenario==opp_surge_scenario)]
    dq_msg = scene.data_insights.values[0]
    dstat = scene.process_status.values[0]

    # Dictionary Keys will be used in Display on the Webpage
    di_pkg = {'wave_count':w_cnt, 'wave_scenario':wave_scenario,'i_count':i_cnt, 'incident_angle_scenario':incident_angle_scenario, 'e_count':e_cnt, 'emmission_angle_scenario':emmission_angle_scenario, 'g_count':g_cnt, 'phase_angle_scenario':phase_angle_scenario, 'all_angles_cnt':all_angles_cnt, 'opp_surge_count':opp_surge_cnt, 'opp_surge_scenario':opp_surge_scenario, 'message':dq_msg, 'process_status':dstat, 'ext_coh_ratio_scenario':ext_coh_ratio_scenario, 'ext_bs_scenario':ext_bs_scenario,'g_covg':is_g_suff,'scene':scene}

    return di_pkg