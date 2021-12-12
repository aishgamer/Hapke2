import math

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
    return 1 + row['Bs0']* row['Bsg']

def add_shadow_hiding():
    global df
    df['shadow_hiding'] = df.apply(lambda r: calc_shadow_hiding(r), axis=1)

def calc_Bsg(row):
    return (1 + (1/row['hs']*row['tang2_rad']))**-1

def add_Bs():
    global df
    df['Bsg'] = df.apply(lambda r: calc_Bsg(r), axis=1)
    
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

def calc_coherent_backscatter(row):
    return 1 + row['Bc0']* row['Bc']
def add_coherent_backscatter():
    global df
    df['coherent_backscatter'] = df.apply(lambda r: calc_coherent_backscatter(r), axis=1)

def add_refl_mu():
    global df, surface_roughness
    if surface_roughness:
        df['mu_0'] = df['mod_mu_0e']
        df['mu'] = df['mod_mu_e']
    else:
        df['mu_0'] = df['cosi_rad']
        df['mu'] = df['cose_rad']

def calc_mu_ratio(row):
    v1 = row['mu_0'] / (row['mu_0']+row['mu'])
    
def add_mu_ratio():
    global df
    df['mu_ratio'] = df.apply(lambda r: calc_mu_ratio(r), axis=1)

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

def _Hu(self, scat_eff, u, r0=None):
    if self.hu_approx: 
        if r0 is None:
            r0 = self._r0(scat_eff)
          #Hapke 1993 equation 8.57
          #H(x) = {1/{1-[1-gamma]*x*[r0+(1-0.5*r0-r0*x)*ln((1+x)/x)]}}
          #Cj had return 1/(1 - u*scat_eff*(r0+np.log((1+u)/u)*(0.5 - r0*u)))
          #this is not the same!
        tmp_gamma = np.sqrt(1 - scat_eff)
        val = 1/(1-(1-tmp_gamma)*u*(r0 + (1 - 0.5*r0 - u*r0)*np.log((1 + u)/u)))
        return val
    else: 
        w0_table = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.925, 0.95, 0.975, 1.0])
        u_table = np.array([0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.0])
        # u = x, w0 = y, h = z (xsize,ysize) scipy.interpolate.RectBivariateSpline(x, y, z, bbox=[None, None, None, None], kx=3, ky=3, s=0)
        h_table = np.array([[1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                      [1.00783, 1.01608, 1.02484, 1.03422, 1.04439, 1.05544, 1.06780, 1.0820, 1.0903, 1.0999, 1.1053, 1.1117, 1.1196, 1.1368],
                      [1.01238, 1.02562, 1.03989, 1.05535, 1.07241, 1.09137, 1.11306, 1.1388, 1.1541, 1.1722, 1.1828, 1.1952, 1.2111, 1.2474],
                      [1.01584, 1.03295, 1.05155, 1.07196, 1.09474, 1.12045, 1.15036, 1.1886, 1.2086, 1.2349, 1.2506, 1.2693, 1.2936, 1.3508],
                      [1.01864, 1.03893, 1.06115, 1.08577, 1.11349, 1.14517, 1.18253, 1.2286, 1.2570, 1.2914, 1.3123, 1.3373, 1.3703, 1.4503],
                      [1.02099, 1.04396, 1.06930, 1.09758, 1.12968, 1.16674, 1.21095, 1.2663, 1.3009, 1.3433, 1.3692, 1.4008, 1.4427, 1.5473],
                      [1.02300, 1.04829, 1.07637, 1.10789, 1.14391, 1.18587, 1.23643, 1.3006, 1.3411, 1.3914, 1.4224, 1.4604, 1.5117, 1.6425],
                      [1.02475, 1.05209, 1.08259, 1.11700, 1.15659, 1.20304, 1.25951, 1.3320, 1.3783, 1.4363, 1.4724, 1.5170, 1.5778, 1.7364],
                      [1.02630, 1.05546, 1.08811, 1.12516, 1.16800, 1.21861, 1.28063, 1.3611, 1.4129, 1.4785, 1.5197, 1.5709, 1.6414, 1.8293],
                      [1.02768, 1.05847, 1.09308, 1.13251, 1.17833, 1.23280, 1.30003, 1.3881, 1.4453, 1.5183, 1.5646, 1.6224, 1.7027, 1.9213],
                      [1.02892, 1.06117, 1.09756, 1.13918, 1.18776, 1.24581, 1.31796, 1.4132, 1.4758, 1.5560, 1.6073, 1.6718, 1.7621, 2.0128],
                      [1.03004, 1.06363, 1.10164, 1.14528, 1.19640, 1.25781, 1.33459, 1.4368, 1.5044, 1.5918, 1.6480, 1.7191, 1.8195, 2.1037],
                      [1.03106, 1.06587, 1.10538, 1.15087, 1.20436, 1.26893, 1.35009, 1.4590, 1.5315, 1.6259, 1.6869, 1.7647, 1.8753, 2.1941],
                      [1.03199, 1.06793, 1.10881, 1.15602, 1.21173, 1.27925, 1.36457, 1.4798, 1.5571, 1.6583, 1.7242, 1.8086, 1.9295, 2.2842],
                      [1.03284, 1.06982, 1.11198, 1.16080, 1.21858, 1.28888, 1.37815, 1.4995, 1.5814, 1.6893, 1.7600, 1.8509, 1.9822, 2.3740],
                      [1.03363, 1.07157, 1.11491, 1.16523, 1.22495, 1.29788, 1.39090, 1.5182, 1.6045, 1.7190, 1.7943, 1.8918, 2.0334, 2.4635],
                      [1.03436, 1.07319, 1.11763, 1.16935, 1.23091, 1.30631, 1.40291, 1.5358, 1.6265, 1.7474, 1.8274, 1.9313, 2.0833, 2.5527],
                      [1.03504, 1.07469, 1.12017, 1.17320, 1.23648, 1.31424, 1.41425, 1.5526, 1.6475, 1.7746, 1.8592, 1.9695, 2.1320, 2.6417],
                      [1.03567, 1.07610, 1.12254, 1.17681, 1.24171, 1.32171, 1.42497, 1.5685, 1.6675, 1.8008, 1.8898, 2.0065, 2.1795, 2.7306],
                      [1.03626, 1.07741, 1.12476, 1.18019, 1.24664, 1.32875, 1.43512, 1.5837, 1.6867, 1.8259, 1.9194, 2.0423, 2.2258, 2.8193],
                      [1.03682, 1.07864, 1.12685, 1.18337, 1.25128, 1.33541, 1.44476, 1.5982, 1.7050, 1.8501, 1.9479, 2.0771, 2.2710, 2.9078]])
        fn = interpolate.RectBivariateSpline(u_table, w0_table, h_table, bbox=[None, None, None, None], kx=3, ky=3, s=0)
        if isinstance(u, float):
            u = np.array([u])
           
        val = fn(u, scat_eff, grid=False)
        #.flatten()[:, np.newaxis]     
        return val

def _Hu_Hu0(self, scat_eff, u, u0):
    r0 = self._r0(scat_eff)
    Hu = self._Hu(scat_eff, u=u, r0=r0)
    Hu0 = self._Hu(scat_eff, u=u0, r0=r0)
    return Hu, Hu0

def _r0(self, scat_eff):
    gamma = np.sqrt(1 - scat_eff)
    return (1-gamma) / (1+gamma)


def add_H_Fn():
    # H(mu_E/PoreK) * (H(mu0/poreK)) - 1

def main_hapke():
    ## Change W to SSA - Single Scattering Albedo
    t1 = df['W'] / (4* math.pi)
    t2 = df['mu_ratio']
    t3 = (df['phase'] * df['shadow_hiding']) + df['h_fn']
    t4 = df['coherent_backscatter']
    t5 = df['S']
    df['model_refl'] = t1 * t2 * t3 * t4 * t5

## Minimization is done on MSE::
# This is the objective function
# Sum (sqrt(refl_i)-modeL_ref_i)**2
