# This file contains a list of standard bondmath functions that are needed for various calculations
# Basic package needs for all functions:

import math
import numpy as np
from numba import njit, float64

MAX_LOG_RATE = 1e3
BASE_TOL = 1e-12



# Cash flow calculation functions------------------------------------------------------------------
@njit(nogil=True, cache=False)
def annuity(rate, remterm):
    return np.divide(rate, (1 - np.power((1 + rate), (-remterm))))

@njit(nogil=True, cache=False)
def beg_balance_factor(periodic_rate, full_term, current_period):
    return np.divide(np.power((1+periodic_rate), full_term)-np.power((1+periodic_rate), current_period-1),
                     (np.power((1+periodic_rate), full_term)-1))

@njit(nogil=True, cache=False)
def end_balance_factor(periodic_rate, full_term, current_period):
    return np.divide(np.power((1+periodic_rate), full_term)-np.power((1+periodic_rate), current_period),
                     (np.power((1+periodic_rate), full_term)-1))


# CPR and SMM Functions
@njit(float64(float64), nogil=True, cache=False)
def cpr2smm(cpr):
    smm_=  1. - np.power(1.-cpr/100., 1/12.)
    return smm_

@njit(float64(float64), nogil=True, cache=False)
def smm2cpr(smm):
    cpr_ = 100*(1. - np.power(1-smm , 12))
    return cpr_

# Interest Rate Conversion Formulas:
def intEffectiveAnnualRate(stated_rate,compound_type):
    if compound_type == 'simple':
        return stated_rate
    else:
        COMPOUND_DICT = {'daily':365, 'weekly':52, 'monthly':12, 'quarterly':4, 'semiannual':2, 'annual':1}
        return np.float_power((1 + np.divide(stated_rate, COMPOUND_DICT[compound_type])), COMPOUND_DICT[compound_type]) -1

def regZRate(cash_disbursed, up_front_fees, back_end_fees, stated_rate, compound_type, months):
    mofrac = (months % 12) / 12
    yrfrac = months // 12
    effrate = intEffectiveAnnualRate(stated_rate, compound_type)
    if compound_type == 'simple':
        intfrac = (1 + effrate / 12 * months)
    else:
        intfrac = (1 + effrate) ** yrfrac + (1 if mofrac > 0 else 0 + (effrate / 12 * mofrac))
    moic = ((cash_disbursed + up_front_fees) * intfrac + back_end_fees) / cash_disbursed
    rate_guess = (moic - 1) * (12 / months)
    moic_guess = ((1 + mofrac * rate_guess) * (1+rate_guess) ** yrfrac)
    while abs(moic - moic_guess)>0.0001:
        rate_up = rate_guess + (0.1 / 100)
        moic_up = (1 + mofrac * rate_up) * (1 + rate_up) ** yrfrac
        rate_guess = rate_guess + (0.1/100) * ((moic-moic_guess)/(moic_up-moic_guess))
        moic_guess = (1 + mofrac * rate_guess) * (1 + rate_guess) ** yrfrac
    return '%.6f' % rate_guess


# IRR Solution Searches---------------------------------------------------------------------------
#TODO: rewrite IRR functions so variables are clearer
#TODO: numba compile IRR functions (need to know numba array declaration method)

# BEGIN: Binary Search Method IRR
def irrBinary(stream, tol=BASE_TOL):
    rate_lo, rate_hi = -MAX_LOG_RATE, +MAX_LOG_RATE
    sgn = np.sign(stream[0]) # f(x) is decreasing
    for steps in range(100):
        rate = (rate_lo + rate_hi)/2
        r = np.arange(len(stream))
        # Factor exp(m) out because it doesn't affect the sign
        m = max(-rate * r)
        f = np.exp(-rate * r - m)
        t = np.dot(f, stream)
        if abs(t) < tol * math.exp(-m):
            break
        if t * sgn > 0:
            rate_hi = rate
        else:
            rate_lo = rate
    rate = (rate_lo + rate_hi) / 2
    return math.exp(rate) - 1
# END: Binary Search from LDCMA Utilities


# BEGIN: Newton's Method IRR
def irrNewton(stream, tol=BASE_TOL):
    rate = 0.0
    for steps in range(50):
        r = np.arange(len(stream))
        # Factor exp(m) out of the numerator & denominator for numerical stability
        m = max(-rate * r)
        f = np.exp(-rate * r - m)
        t = np.dot(f, stream)
        if abs(t) < tol * math.exp(-m):
            break
        u = np.dot(f * r, stream)
        # Clip the update to avoid jumping into some numerically unstable place
        rate = rate + np.clip(t / u, -1.0, 1.0)
    return math.exp(rate) - 1
# END: Newton's Method from LDCMA Utilities