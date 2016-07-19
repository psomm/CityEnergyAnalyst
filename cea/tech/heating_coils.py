# -*- coding: utf-8 -*-
"""
=========================================
Heating and cooling coils of Air handling units
=========================================

"""
from __future__ import division
import scipy.optimize as sopt
from scipy import log, exp

def calc_heating_coil(Qhsf, Qhsf_0, Ta_sup_hs, Ta_re_hs, Ths_sup_0, Ths_re_0, ma_sup_hs, ma_sup_0,Ta_sup_0, Ta_re_0, Cpa):

    tasup = Ta_sup_hs + 273
    tare = Ta_re_hs + 273
    tsh0 = Ths_sup_0 + 273
    trh0 = Ths_re_0 + 273
    mCw0 = Qhsf_0 / (tsh0 - trh0)

    # log mean temperature at nominal conditions
    TD10 = Ta_sup_0 - trh0
    TD20 = Ta_re_0 - tsh0
    LMRT0 = (TD10 - TD20) / log(TD20 / TD10)
    UA0 = Qhsf_0 / LMRT0

    if Qhsf > 0 and ma_sup_hs > 0:
        AUa = UA0 * (ma_sup_hs / ma_sup_0) ** 0.77
        NTUc = AUa / (ma_sup_hs * Cpa * 1000)
        ec = 1 - exp(-NTUc)
        tc = (tare - tasup + tasup * ec) / ec  # contact temperature of coil

        # minimum
        LMRT = (tsh0 - trh0) / log((tsh0 - tc) / (trh0 - tc))
        k1 = 1 / mCw0

        def fh(x):
            Eq = mCw0 * k2 - Qhsf_0 * (k2 / (log((x + k2 - tc) / (x - tc)) * LMRT))
            return Eq

        k2 = Qhsf * k1
        result = sopt.newton(fh, trh0, maxiter=100, tol=0.01) - 273
        trh = result.real
        tsh = trh + k2
        mcphs = Qhsf / (tsh - trh) / 1000
    else:
        tsh = trh = mcphs = 0
    return tsh, trh, mcphs

def calc_cooling_coil(Qcsf, Qcsf_0, Ta_sup_cs, Ta_re_cs, Tcs_sup_0, Tcs_re_0, ma_sup_cs, ma_sup_0, Ta_sup_0, Ta_re_0,Cpa):
    # Initialize temperatures
    tasup = Ta_sup_cs + 273
    tare = Ta_re_cs + 273
    tsc0 = Tcs_sup_0 + 273
    trc0 = Tcs_re_0 + 273
    mCw0 = Qcsf_0 / (tsc0 - trc0)

    # log mean temperature at nominal conditions
    TD10 = Ta_sup_0 - trc0
    TD20 = Ta_re_0 - tsc0
    LMRT0 = (TD20 - TD10) / log(TD20 / TD10)
    UA0 = Qcsf_0 / LMRT0

    if Qcsf < 0 and ma_sup_cs > 0:
        AUa = UA0 * (ma_sup_cs / ma_sup_0) ** 0.77
        NTUc = AUa / (ma_sup_cs * Cpa * 1000)
        ec = 1 - exp(-NTUc)
        tc = (tare - tasup + tasup * ec) / ec  # contact temperature of coil

        def fh(x):
            TD1 = tc - (k2 + x)
            TD2 = tc - x
            LMRT = (TD2 - TD1) / log(TD2 / TD1)
            Eq = mCw0 * k2 - Qcsf_0 * (LMRT / LMRT0)
            return Eq

        k2 = -Qcsf / mCw0
        result = sopt.newton(fh, trc0, maxiter=100, tol=0.01) - 273
        tsc = result.real
        trc = tsc + k2

        # Control system check - close to optimal flow
        min_AT = 5  # Its equal to 10% of the mass flowrate
        tsc_min = 7  # to consider coolest source possible
        trc_max = 17
        tsc_max = 12
        AT = tsc - trc
        if AT < min_AT:
            if tsc < tsc_min:
                tsc = tsc_min
                trc = tsc_min + min_AT
            if tsc > tsc_max:
                tsc = tsc_max
                trc = tsc_max + min_AT
            else:
                trc = tsc + min_AT
        elif tsc > tsc_max or trc > trc_max or tsc < tsc_min:
            trc = trc_max
            tsc = tsc_max

        mcpcs = Qcsf / (tsc - trc) / 1000
    else:
        tsc = trc = mcpcs = 0
    return tsc, trc, mcpcs
