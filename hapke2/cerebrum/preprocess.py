import numpy as np
def init_process(df):
    df['i_rad'] = np.deg2rad(df.i)
    df['e_rad'] = np.deg2rad(df.e)
    df['g_rad'] = np.deg2rad(df.g)

    return df

def nanometer_conversion(df):
    if df.wave.mean() < 10:
        df.wave = df.wave * 1000
    return df

def add_macro_surface_roughness(df):
    #after converting to radians deg2rad(i,e,g)
    #calculate quantites for later
    #tangent of phase angle, g, divided by 2
    df['tang2_rad'] = np.tan(df.g_rad / 2)
    #cosine of phase angle, g
    df['cosg_rad'] = np.cos(df.g_rad)
    #cosine of input angle, i
    df['cosi_rad'] = np.cos(df.i_rad) # is mu_0 if no tbar
    #cosine of emission angle, e
    df['cose_rad'] = np.cos(df.e_rad) # is mu if no tbar
    #sine of input angle, i
    df['sini_rad'] = np.sin(df.i_rad)
    #sine of emission angle, e
    df['sine_rad'] = np.sin(df.e_rad)
    #cotangent of input angle, i
    df['coti_rad'] = 1 / np.tan(df.i_rad)
    #cotangent of emission angle, e
    df['cote_rad'] = 1 / np.tan(df.e_rad)
    #square of cotangent of input angle, i
    df['cot2i_rad'] = df.coti_rad ** 2
    #square of cotangent of emission angle, e 
    df['cot2e_rad'] = df.cote_rad ** 2
    #fi is the zimuthal angle - it is the angle between the projection 
    #onto the surface of input and emission rays, i and e
    #fi, i and e are related through the cosine of fi
    df['cosfi_rad'] = (df.cosg_rad - df.cosi_rad * df.cose_rad) / (df.sini_rad * df.sine_rad)
    #next, an array of length column i is created. Not sure if we want to 
    #I think we are just adding these to the original array of data
    #NEXT WE DEAL WITH SOME SPECIAL CASES WHERE FI IS IRREGULAR
    #if cosfi()<=0.99999

    return df