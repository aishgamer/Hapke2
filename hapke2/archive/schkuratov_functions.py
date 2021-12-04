## Fresnel reflectances
## Appropriate for n=1.4 >> n=1.7

import math

alb_eq, phase_fn,n=0,0,1
app_alb = alb_eq * phase_fn
k, S, lamb_da = 0,0,0

# eq 7 -8
r_0 = (n-1)**2 / (n+1)**2
R_e = r_0 + 0.05
R_b = (0.28*n-0.20)*R_e
R_f = R_e - R_b
R_i = 1 - (1-R_e) / (n**2)
T_e = 1 - R_e
T_i = 1 - R_i

tau = (4*math.pi*k*S)/(lamb_da)

# eq 9a, 9b
r_num = ((1/2)*T_e*T_i*R_i*(math.exp(-2*tau)))
r_den = (1- (R_i * math.exp(-tau)))
r_b = R_b + ( r_num / r_den )
r_f = R_f + (T_e*T_i*(math.exp(-tau))) + (r_num/r_den)

#eq 10-12
# q = For a randomly packed medium, there is a mathematical theorem
# that the area fraction filled by particles in an intersecting plane
# (or a line) is equal to q.
q = 0
rho_b = q * r_b 
rho_f = q * r_f + (1 - q)

A_t1_num = 1 + (rho_b)**2 - (rho_f)**2
A_t1_den = 2 * (rho_b)
A = (A_t1_num/A_t1_den) - (((A_t1_num/A_t1_den)**2)-1)**(1/2)

# eq 14 - what is the range of j??


