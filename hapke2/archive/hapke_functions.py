def single_particle_phase(row):
    global phase_mixing
      if phase_mixing == 'legendre':
        # two-term legendre polynomial phase function P(g)
        return 1 + row['b'] * row['cosg_rad'] + row['c'] * (1.5*(row['cosg_rad']**2)-0.5)
      elif phase_mixing == 'dhg':
        # double Heyney-Greenstein phase function P(g)
        x0 = row['b'] * row['b']
        x1 = 2 * row['b']* row['cosg_rad']
        x2 = (1 + x1 + x0) ** 1.5
        x3 = (1 - x1 + x0) ** 1.5
        return (1-row['c']) * (1-x0) / x2 + row['c'] * (1-x0) / x3
      elif phase_mixing == 'constant':
        return 1
      else:
        raise ValueError('Invalid phase_fn: %r' % phase_fn)
        return 0

def add_phase():
    global df
    df['phase'] = df.apply(lambda r: single_particle_phase(r), axis=1)

def calc_mu_ratio(row):
    v1 = row['mu_0'] / (row['mu_0']+row['mu'])
    
def add_mu_ratio():
    global df
    df['mu_ratio'] = df.apply(lambda r: calc_mu_ratio(r), axis=1)

def add_refl_mu():
    global surface_roughness
    global df
    if surface_roughness:
        df['mu_0'] = df['mod_mu_0e']
        df['mu'] = df['mod_mu_e']
    else:
        df['mu_0'] = df['cosi_rad']
        df['mu'] = df['cose_rad']

def calc_coherent_backscatter(row):
    return 1 + row['Bc0']* row['Bc']
def add_coherent_backscatter():
    global df
    df['coherent_backscatter'] = df.apply(lambda r: calc_coherent_backscatter(r), axis=1)

    # You can only solve for Bc if you have phase angles less than 2 degress. 
def calc_Bc(row):
    mod_PoreK = 1.42 * row['PoreK']
    inv_hc = 1/hc 
    v1 = 1 / (1 + mod_PoreK)
    v2 = 1 / (1 + (inv_hc * row['tang2_rad']))**2
    v3_num = 1 - np.exp(-mod_PoreK*inv_hc*row['tang2_rad'])
    v3_den = inv_hc*row['tang2_rad']
    v3 = 1 + (v3_num/v3_den)
    return v1*v2*v3

def add_Bc():
    global df
    df['Bc'] = df.apply(lambda r: add_Bc(r), axis=1)
    
# hc = (lamda / 4 * math.pi * path)
# path = [PoreK*N*σ*QS(1−ξ)]−1
# path = (2/3)(D/(PoreK*ff*Qs(1-ξ)))
# ξ is the cosine asymmetry factor which is the average value of the cosine of the scattering angle
# θ weighted by the particle phase function,
# = −<cosg>
# A positive value of ξ implies that most of the light is scattered into the forward
# hemisphere, while a negative value of ξ means that the particle is predominantly
# backscattering


def calc_PoreK(row):
    var = 1.209 * (row['ff'])**(2/3)
    return -np.log(1 - var)/var

def add_PoreK():
    global df
    df['PoreK'] = df.apply(lambda r: calc_PoreK(r), axis=1)

def calc_shadow_hiding(row):
    return 1 + row['Bs0']* row['Bs']
def add_shadow_hiding():
    global df
    df['shadow_hiding'] = df.apply(lambda r: calc_shadow_hiding(r), axis=1)

def calc_Bs(row):
    return (1 + (1/row['hs']*row['tang2_rad']))**-1

def add_Bs():
    global df
    df['Bs'] = df.apply(lambda r: calc_Bs(r), axis=1)
    
# hs equations - From Domingue et all 2016
#However, it has been shown that for regoliths that are the product
#of comminution or grinding by meteorite impacts, the particle size
#distribution is best described by a power law (McKay et al., 1974;
#Bhattacharya et al., 1975). In this case, Hapke (2012a) shows that
#the relation between hs and / can be described by
# hs = (3 * (3**1/2)/8) * ((PoreK * ff)/np.log(D_min/D_mx)

# in any other surface
# hs = (3* PoreK * ff / 8)

def calc_S_ilesseqe(row):
    v1 = row['mod_mu_e']/row['eta_e']
    v2 = row['cosi_rad']/row['eta_i']
    v3_num =  row['xi_theta_bar']
    v3_den_1 = row['f_rad']
    # cosi_rad = mu_0
    v3_den_2 = row['f_rad']*row['xi_theta_bar']*(row['cosi_rad']/row['eta_i'])
    v3_den = 1 - v3_den_1 + v3_den_2
    v3 = v3_num/v3_den
    return v1*v2*v3

def calc_S_elessi(row):
    v1 = row['mod_mu_e']/row['eta_e']
    # cosi_rad = mu_0
    v2 = row['cosi_rad']/row['eta_i']
    v3_num =  row['xi_theta_bar']
    v3_den_1 = row['f_rad']
    # cose_rad = mu
    v3_den_2 = row['f_rad']*row['xi_theta_bar']*(row['cose_rad']/row['eta_e'])
    v3_den = 1 - v3_den_1 + v3_den_2
    v3 = v3_num/v3_den
    return v1*v2*v3

def calc_S(row):
    if row['i_rad'] <= row['e_rad']:
        return calc_S_ilesseqe(row)
    else:
        return calc_S_elessi(row)
    
def add_S():
    global df
    df['S'] = df.apply(lambda r: calc_S(r), axis=1)

def calc_mu_0e_elessi(row):
    #do we use i,e degree or i,e radians - Deborah  says radians
    # Theta_bar is inut guess to the program
    v1 = row['cosi_rad'] 
    v2 = row['sini_rad'] * np.tan(row['theta_bar_rad'])
    v3_num_1 = E2_x(row['i_rad'],row['theta_bar_rad'])
    v3_num_2 = row['sin2fi2_rad']*E2_x(row['e_rad'],row['theta_bar_rad'])
    v3_num = v3_num_1 - v3_num_2
    v3_den_1 = E1_x(row['i_rad'],row['theta_bar_rad'])
    v3_den_2 = (row['fi_rad']/math.pi) * E1_x(row['e_rad'],row['theta_bar_rad'])
    v3_den = 2 - v3_den_1 - v3_den_2
    v3 = v3_num/v3_den
    return row['xi_theta_bar'] * (v1 + (v2*v3))

def calc_mu_e_elessi(row):
    #do we use i,e degree or i,e radians - Deborah  says radians
    # Theta_bar is inut guess to the program
    v1 = row['cose_rad'] 
    v2 = row['sine_rad'] * np.tan(row['theta_bar_rad'])
    v3_num_1 = row['cosfi_rad']*E2_x(row['i_rad'],row['theta_bar_rad'])
    v3_num_2 = row['sin2fi2_rad']*E2_x(row['e_rad'],row['theta_bar_rad'])
    v3_num = v3_num_1 + v3_num_2
    v3_den_1 = E1_x(row['i_rad'],row['theta_bar_rad'])
    v3_den_2 = (row['fi_rad']/math.pi) * E1_x(row['e_rad'],row['theta_bar_rad'])
    v3_den = 2 - v3_den_1 - v3_den_2
    v3 = v3_num/v3_den
    return row['xi_theta_bar'] * (v1 + (v2*v3))

###########################################################################
##########################################################################
## i <= e
def calc_mu_0e_ilesseqe(row):
    #do we use i,e degree or i,e radians - Deborah  says radians
    # Theta_bar is inut guess to the program
    v1 = row['cosi_rad'] 
    v2 = row['sini_rad'] * np.tan(row['theta_bar_rad'])
    v3_num_1 = row['cosfi_rad']*E2_x(row['e_rad'],row['theta_bar_rad'])
    v3_num_2 = row['sin2fi2_rad']*E2_x(row['i_rad'],row['theta_bar_rad'])
    v3_num = v3_num_1 + v3_num_2
    v3_den_1 = E1_x(row['e_rad'],row['theta_bar_rad'])
    v3_den_2 = (row['fi_rad']/math.pi) * E1_x(row['i_rad'],row['theta_bar_rad'])
    v3_den = 2 - v3_den_1 - v3_den_2
    v3 = v3_num/v3_den
    return row['xi_theta_bar'] * (v1 + (v2*v3))

def calc_mu_e_ilesseqe(row):
    #do we use i,e degree or i,e radians - Deborah  says radians
    # Theta_bar is inut guess to the program
    v1 = row['cose_rad'] 
    v2 = row['sine_rad'] * np.tan(row['theta_bar_rad'])
    v3_num_1 = E2_x(row['e_rad'],row['theta_bar_rad'])
    v3_num_2 = row['sin2fi2_rad']*E2_x(row['i_rad'],row['theta_bar_rad'])
    v3_num = v3_num_1 - v3_num_2
    v3_den_1 = E1_x(row['e_rad'],row['theta_bar_rad'])
    v3_den_2 = (row['fi_rad']/math.pi) * E1_x(row['i_rad'],row['theta_bar_rad'])
    v3_den = 2 - v3_den_1 - v3_den_2
    v3 = v3_num/v3_den
    return row['xi_theta_bar'] * (v1 + (v2*v3))

def calc_mod_mu_0e(row):
    if row['i_rad'] <= row['e_rad']:
        return calc_mu_0e_ilesseqe(row)
    else:
        return calc_mu_0e_elessi(row)
    
def calc_mod_mu_e(row):
    if row['i_rad'] <= row['e_rad']:
        return calc_mu_e_ilesseqe(row)
    else:
        return calc_mu_e_elessi(row)
    
def add_modified_mu_():
    global df
    df['mod_mu_0e'] = df.apply(lambda r: calc_mod_mu_0e(r), axis=1)
    df['mod_mu_e'] = df.apply(lambda r: calc_mod_mu_e(r), axis=1)

def calc_xi_theta_bar(row):
    tan_sq_tbar = np.tan(row['theta_bar_rad'])**2
    denom = (1 + math.pi * tan_sq_tbar)**1/2
    return 1/denom

def add_xi_theta_bar():
    global df
    df['xi_theta_bar'] = df.apply(lambda r: calc_xi_theta_bar(r), axis=1)

def E1_x(x, tbar_rad):
    return np.exp((-2/math.pi)*(1/np.tan(tbar_rad))*(1/np.tan(x)))

def E2_x(x, tbar_rad):
    return np.exp((-1/math.pi)*(1/np.tan(tbar_rad))**2*(1/np.tan(x))**2)

def calc_eta(row, angle):
    t2_3 = E2_x(row[angle],row['theta_bar_rad'])/(2-E1_x(row[angle],row['theta_bar_rad']))
    t2_12 = np.sin(row[angle])*np.tan(row['theta_bar_rad'])
    t2 = t2_12*t2_3
    return row['xi_theta_bar']*(np.cos(row[angle])+t2)

def add_eta():
    global df
    df['eta_i'] = df.apply(lambda r: calc_eta(r, 'i_rad'), axis=1)
    df['eta_e'] = df.apply(lambda r: calc_eta(r, 'e_rad'), axis=1)

# calculating conditional fi

def calc_fi(row):
    cosfi_rad, fi_rad, sin2fi2_rad, tanfi2_rad, f_rad = None,None,None,None, None
    if row['cosfi_rad']<=-0.99999:
        print("Error: cosfi < -1 at i=",row.name,". Setting cosfi=-1.")
        cosfi_rad  = -1.0000
        fi_rad = math.pi
        sin2fi2_rad = 1.0
        f_rad = 0.0
    else:
        # normal range and greater than 0.9999
        if row['cosfi_rad'] >= 0.99999:
            print("Error: cosfi > 1 at i=",row.name,". Setting cosfi=1.")
            cosfi_rad = 1.000
        else:
            cosfi_rad = row['cosfi_rad']
            #what happens if try doesn't work
        try:
            fi_rad=np.arccos(cosfi_rad)
            sin2fi2_rad=(np.sin(fi_rad/2.0))**2
            tanfi2_rad=np.tan(fi_rad/2.0)
            f_rad = np.exp(-2.0*tanfi2_rad)
        except:
            return  cosfi_rad, fi_rad, sin2fi2_rad, tanfi2_rad, f_rad 
    return  cosfi_rad, fi_rad, sin2fi2_rad, tanfi2_rad, f_rad 
    
def add_fi_columns():
    global df
    df['fi_tuples'] =  df.apply(lambda r: calc_fi(r), axis=1)
    # cosfi_rad_logical contains the replaced values of cosfi_rad calculated durinng fi_calculations
    # within fi_calculations, the corrected cosfi_rad is used
    # post fi_calculations, cosfi_rad_logical must be used for corrected cosfi_rad
    df[['cosfi_rad_logical','fi_rad', 'sin2fi2_rad', 'tanfi2_rad', 'f_rad']] = pd.DataFrame(df['fi_tuples'].tolist(), index=df.index)
    df.drop(['fi_tuples'], axis=1, inplace=True)