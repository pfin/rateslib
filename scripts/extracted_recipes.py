"""
Rateslib Cookbook Recipes 13-17, 19-24, 26-28
===============================================

This file contains Python code extracted from the rateslib cookbook recipes.
Due to network connectivity issues during extraction, some recipes may be incomplete.

Recipes successfully extracted:
- Recipe 13: A EURUSD market for IRS, cross-currency and FX volatility
- Recipe 14: Understanding and Customising FixedRateBond Conventions  
- Recipe 15: Using Curves with an Index and Inflation Instruments
- Recipe 16: Inflation Indexes and Curves 2 (Quantlib comparison)

Note: Remaining recipes (17, 19-24, 26-28) could not be extracted due to network issues.
"""

from rateslib import *
import numpy as np
from pandas import DataFrame, Series

# =============================================================================
# Recipe 13: A EURUSD market for IRS, cross-currency and FX volatility
# =============================================================================

def recipe_13_eurusd_market():
    """A EURUSD market for IRS, cross-currency and FX volatility"""
    
    # Input market data from May 28, 2024
    fxr = FXRates({"eurusd": 1.0867}, settlement=dt(2024, 5, 30))

    mkt_data = DataFrame(
        data=[['1w', 3.9035,5.3267,3.33,],
              ['2w', 3.9046,5.3257,6.37,],
              ['3w',3.8271,5.3232,9.83,],
              ['1m',3.7817,5.3191,13.78,],
              ['2m',3.7204,5.3232,30.04,],
              ['3m',3.667,5.3185,45.85,-2.5],
              ['4m',3.6252,5.3307,61.95,],
              ['5m',3.587,5.3098,78.1,],
              ['6m',3.5803,5.3109,94.25,-3.125],
              ['7m',3.5626,5.301,110.82,],
              ['8m',3.531,5.2768,130.45,],
              ['9m',3.5089,5.2614,145.6,-7.25],
              ['10m',3.4842,5.2412,162.05,],
              ['11m',3.4563,5.2144,178,],
              ['1y',3.4336,5.1936,None,-6.75],
              ['15m',3.3412,5.0729,None,-6.75],
              ['18m',3.2606,4.9694,None,-6.75],
              ['21m',3.1897,4.8797,None,-7.75],
              ['2y',3.1283,4.8022,None,-7.875],
              ['3y',2.9254,4.535,None,-9],
              ['4y',2.81,4.364,None,-10.125],
              ['5y',2.7252,4.256,None,-11.125],
              ['6y',2.6773,4.192,None,-12.125],
              ['7y',2.6541,4.151,None,-13],
              ['8y',2.6431,4.122,None,-13.625],
              ['9y',2.6466,4.103,None,-14.25],
              ['10y',2.6562,4.091,None,-14.875],
              ['12y',2.6835,4.084,None,-16.125],
              ['15y',2.7197,4.08,None,-17],
              ['20y',2.6849,4.04,None,-16],
              ['25y',2.6032,3.946,None,-12.75],
              ['30y',2.5217,3.847,None,-9.5]],
        columns=["tenor", "estr", "sofr", "fx_swap", "xccy"],
    )

    # Create curves
    eur = Curve(
        nodes={
            dt(2024, 5, 28): 1.0,
            **{add_tenor(dt(2024, 5, 30), _, "F", "tgt"): 1.0 for _ in mkt_data["tenor"]}
        },
        calendar="tgt",
        interpolation="log_linear",
        convention="act360",
        id="estr",
    )
    usd = Curve(
        nodes={
            dt(2024, 5, 28): 1.0,
            **{add_tenor(dt(2024, 5, 30), _, "F", "nyc"): 1.0 for _ in mkt_data["tenor"]}
        },
        calendar="nyc",
        interpolation="log_linear",
        convention="act360",
        id="sofr",
    )
    eurusd = Curve(
        nodes={
            dt(2024, 5, 28): 1.0,
            **{add_tenor(dt(2024, 5, 30), _, "F", "tgt"): 1.0 for _ in mkt_data["tenor"]}
        },
        interpolation="log_linear",
        convention="act360",
        id="eurusd",
    )

    # FX Forwards mapping
    fxf = FXForwards(
        fx_rates=fxr,
        fx_curves={"eureur": eur, "eurusd": eurusd, "usdusd": usd}
    )

    # Create instruments for solving curves
    estr_swaps = [IRS(dt(2024, 5, 30), _, spec="eur_irs", curves="estr") for _ in mkt_data["tenor"]]
    estr_rates = mkt_data["estr"].tolist()
    labels = mkt_data["tenor"].to_list()
    sofr_swaps = [IRS(dt(2024, 5, 30), _, spec="usd_irs", curves="sofr") for _ in mkt_data["tenor"]]
    sofr_rates = mkt_data["sofr"].tolist()

    # Solve EUR and USD curves
    eur_solver = Solver(
        curves=[eur],
        instruments=estr_swaps,
        s=estr_rates,
        fx=fxf,
        instrument_labels=labels,
        id="eur",
    )
    usd_solver = Solver(
        curves=[usd],
        instruments=sofr_swaps,
        s=sofr_rates,
        fx=fxf,
        instrument_labels=labels,
        id="usd",
    )

    # Cross currency curve instruments
    fxswaps = [FXSwap(dt(2024, 5, 30), _, pair="eurusd", curves=[None, "eurusd", None, "sofr"]) for _ in mkt_data["tenor"][0:14]]
    fxswap_rates = mkt_data["fx_swap"][0:14].tolist()
    xcs = [XCS(dt(2024, 5, 30), _, spec="eurusd_xcs", curves=["estr", "eurusd", "sofr", "sofr"]) for _ in mkt_data["tenor"][14:]]
    xcs_rates = mkt_data["xccy"][14:].tolist()

    # Solve FX curve
    fx_solver = Solver(
        pre_solvers=[eur_solver, usd_solver],
        curves=[eurusd],
        instruments=fxswaps + xcs,
        s=fxswap_rates + xcs_rates,
        fx=fxf,
        instrument_labels=labels,
        id="eurusd_xccy",
    )

    # FX Vol Surface data
    vol_data = DataFrame(
        data=[
            ['1w',4.535,-0.047,0.07,-0.097,0.252],
            ['2w',5.168,-0.082,0.077,-0.165,0.24],
            ['3w',5.127,-0.175,0.07,-0.26,0.233],
            ['1m',5.195,-0.2,0.07,-0.295,0.235],
            ['2m',5.237,-0.28,0.087,-0.535,0.295],
            ['3m',5.257,-0.363,0.1,-0.705,0.35],
            ['4m',5.598,-0.47,0.123,-0.915,0.422],
            ['5m',5.776,-0.528,0.133,-1.032,0.463],
            ['6m',5.92,-0.565,0.14,-1.11,0.49],
            ['9m',6.01,-0.713,0.182,-1.405,0.645],
            ['1y',6.155,-0.808,0.23,-1.585,0.795],
            ['18m',6.408,-0.812,0.248,-1.588,0.868],
            ['2y',6.525,-0.808,0.257,-1.58,0.9],
            ['3y',6.718,-0.733,0.265,-1.45,0.89],
            ['4y',7.025,-0.665,0.265,-1.31,0.885],
            ['5y',7.26,-0.62,0.26,-1.225,0.89],
            ['6y',7.508,-0.516,0.27,-0.989,0.94],
            ['7y',7.68,-0.442,0.278,-0.815,0.975],
            ['10y',8.115,-0.267,0.288,-0.51,1.035],
            ['15y',8.652,-0.325,0.362,-0.4,1.195],
            ['20y',8.651,-0.078,0.343,-0.303,1.186],
            ['25y',8.65,-0.029,0.342,-0.218,1.178],
            ['30y',8.65,0.014,0.341,-0.142,1.171],
        ],
        columns=["tenor", "atm", "25drr", "25dbf", "10drr", "10dbf"]
    )
    vol_data["expiry"] = [add_tenor(dt(2024, 5, 28), _, "MF", "tgt") for _ in vol_data["tenor"]]

    # Define FX Vol Surface
    surface = FXDeltaVolSurface(
        eval_date=dt(2024, 5, 28),
        expiries=vol_data["expiry"],
        delta_indexes=[0.1, 0.25, 0.5, 0.75, 0.9],
        node_values=np.ones((23, 5))*5.0,
        delta_type="forward",
        id="eurusd_vol"
    )

    # FX instrument arguments
    fx_args = dict(
        pair="eurusd",
        curves=[None, "eurusd", None, "sofr"],
        calendar="tgt",
        delivery_lag=2,
        payment_lag=2,
        eval_date=dt(2024, 5, 28),
        modifier="MF",
        premium_ccy="usd",
        vol="eurusd_vol",
    )

    # Create instruments for surface calibration (1Y or less)
    instruments_le_1y, rates_le_1y, labels_le_1y = [], [], []
    for row in range(11):
        instruments_le_1y.extend([
            FXStraddle(strike="atm_delta", expiry=vol_data["expiry"][row], delta_type="spot", **fx_args),
            FXRiskReversal(strike=("-25d", "25d"), expiry=vol_data["expiry"][row], delta_type="spot", **fx_args),
            FXBrokerFly(strike=(("-25d", "25d"), "atm_delta"), expiry=vol_data["expiry"][row], delta_type="spot", **fx_args),
            FXRiskReversal(strike=("-10d", "10d"), expiry=vol_data["expiry"][row], delta_type="spot", **fx_args),
            FXBrokerFly(strike=(("-10d", "10d"), "atm_delta"), expiry=vol_data["expiry"][row], delta_type="spot", **fx_args),
        ])
        rates_le_1y.extend([vol_data["atm"][row], vol_data["25drr"][row], vol_data["25dbf"][row], vol_data["10drr"][row], vol_data["10dbf"][row]])
        labels_le_1y.extend([f"atm_{row}", f"25drr_{row}", f"25dbf_{row}", f"10drr_{row}", f"10dbf_{row}"])

    # Create instruments for surface calibration (>1Y)
    instruments_gt_1y, rates_gt_1y, labels_gt_1y = [], [], []
    for row in range(11, 23):
        instruments_gt_1y.extend([
            FXStraddle(strike="atm_delta", expiry=vol_data["expiry"][row], delta_type="forward", **fx_args),
            FXRiskReversal(strike=("-25d", "25d"), expiry=vol_data["expiry"][row], delta_type="forward", **fx_args),
            FXBrokerFly(strike=(("-25d", "25d"), "atm_delta"), expiry=vol_data["expiry"][row], delta_type="forward", **fx_args),
            FXRiskReversal(strike=("-10d", "10d"), expiry=vol_data["expiry"][row], delta_type="forward", **fx_args),
            FXBrokerFly(strike=(("-10d", "10d"), "atm_delta"), expiry=vol_data["expiry"][row], delta_type="forward", **fx_args),
        ])
        rates_gt_1y.extend([vol_data["atm"][row], vol_data["25drr"][row], vol_data["25dbf"][row], vol_data["10drr"][row], vol_data["10dbf"][row]])
        labels_gt_1y.extend([f"atm_{row}", f"25drr_{row}", f"25dbf_{row}", f"10drr_{row}", f"10dbf_{row}"])

    # Solve surface
    surface_solver = Solver(
        surfaces=[surface],
        instruments=instruments_le_1y+instruments_gt_1y,
        s=rates_le_1y+rates_gt_1y,
        instrument_labels=labels_le_1y+labels_gt_1y,
        fx=fxf,
        pre_solvers=[fx_solver],
        id="eurusd_vol"
    )

    # Alternative SABR Surface
    sabr_surface = FXSabrSurface(
        eval_date=dt(2024, 5, 28),
        expiries=list(vol_data["expiry"]),
        node_values=[[0.05, 1.0, 0.01, 0.10]] * 23,  # alpha, beta, rho, nu
        pair="eurusd",
        delivery_lag=2,
        calendar="tgt|fed",
        id="eurusd_vol",
    )

    return {
        'mkt_data': mkt_data,
        'vol_data': vol_data,
        'curves': {'eur': eur, 'usd': usd, 'eurusd': eurusd},
        'fxf': fxf,
        'solvers': {'eur': eur_solver, 'usd': usd_solver, 'fx': fx_solver, 'surface': surface_solver},
        'surfaces': {'delta': surface, 'sabr': sabr_surface}
    }


# =============================================================================
# Recipe 14: Understanding and Customising FixedRateBond Conventions
# =============================================================================

def recipe_14_bond_conventions():
    """Understanding and Customising FixedRateBond Conventions"""
    
    # Example bond without calendar adjustments
    bond = FixedRateBond(dt(2000, 2, 17), "2y", fixed_rate=4.0, frequency="S", calendar="all", convention="actacticma")
    
    # Better configuration with proper calendar
    bond = FixedRateBond(dt(2000, 2, 17), "2y", fixed_rate=4.0, frequency="S", calendar="nyc", modifier="none", convention="actacticma")
    
    # Thai Government Bond custom implementation example
    def _v1_thb_gb(obj, ytm, f, settlement, acc_idx, v2, accrual, period_idx):
        """The exponent to the regular discount factor is derived from ACT365F"""
        r_u = (obj.leg1.schedule.uschedule[acc_idx + 1] - settlement).days
        return v2 ** (r_u * f / 365)

    def _v3_thb_gb(obj, ytm, f, settlement, acc_idx, v2, accrual, period_idx):
        """The exponent to the regular discount function is derived from ACT365F"""
        r_u = (obj.leg1.schedule.uschedule[-1] - obj.leg1.schedule.uschedule[-2]).days
        return v2 ** (r_u * f / 365)

    # Custom calc mode for Thai bonds
    from rateslib.instruments import BondCalcMode
    
    thb_gb = BondCalcMode(
        settle_accrual="linear_days",
        ytm_accrual="linear_days",
        v1=_v1_thb_gb,
        v2="regular",
        v3=_v3_thb_gb,
        c1="full_coupon",
        ci="full_coupon",
        cn="cashflow",
    )

    # Thai bond with custom calc mode
    thai_bond = FixedRateBond(
        effective=dt(1991, 1, 15),
        termination=dt(1996, 4, 30),
        stub="shortback",
        fixed_rate=11.25,
        frequency="S",
        roll=15,
        convention="act365f",
        modifier="none",
        currency="thb",
        calendar="bus",
        calc_mode=thb_gb
    )

    return {
        'bond': bond,
        'thai_bond': thai_bond,
        'thb_gb': thb_gb,
        'custom_functions': {'_v1_thb_gb': _v1_thb_gb, '_v3_thb_gb': _v3_thb_gb}
    }


# =============================================================================
# Recipe 15: Using Curves with an Index and Inflation Instruments
# =============================================================================

def recipe_15_index_curves():
    """Using Curves with an Index and Inflation Instruments"""
    
    today = dt(2025, 5, 12)

    # Create RPI series (real published UK RPI prints)
    RPI_series = DataFrame([
        [dt(2024, 2, 1), 381.0],
        [dt(2024, 3, 1), 383.0],
        [dt(2024, 4, 1), 385.0],
        [dt(2024, 5, 1), 386.4],
        [dt(2024, 6, 1), 387.3],
        [dt(2024, 7, 1), 387.5],
        [dt(2024, 8, 1), 389.9],
        [dt(2024, 9, 1), 388.6],
        [dt(2024, 10, 1), 390.7],
        [dt(2024, 11, 1), 390.9],
        [dt(2024, 12, 1), 392.1],
        [dt(2025, 1, 1), 391.7],
        [dt(2025, 2, 1), 394.0],
        [dt(2025, 3, 1), 395.3]
    ], columns=["month", "rate"]).set_index("month")["rate"]

    # Index Fixed Rate Bond
    ukti = IndexFixedRateBond(
        effective=dt(2024, 5, 27),
        termination=dt(2025, 5, 27),
        fixed_rate=2.0,
        notional=-10e6,
        index_base=RPI_series,
        index_method="daily",
        index_lag=3,
        index_fixings=RPI_series,
        spec="uk_gb"
    )

    # Discount curve
    disc_curve = Curve({today: 1.0, dt(2029, 1, 1): 0.95})

    # Index curve for forecast
    index_curve = Curve(
        nodes={
            dt(2025, 3, 1): 1.0,
            dt(2025, 4, 1): 1.0,
            dt(2025, 5, 1): 1.0,
            dt(2025, 6, 1): 1.0,
            dt(2025, 7, 1): 1.0,
        },
        index_lag=0,
        index_base=395.3,
        id="ic",
    )

    # Solver for index curve
    solver = Solver(
        curves=[index_curve],
        instruments=[
            Value(effective=dt(2025, 4, 1), metric="index_value", curves="ic"),
            Value(effective=dt(2025, 5, 1), metric="index_value", curves="ic"),
            Value(effective=dt(2025, 6, 1), metric="index_value", curves="ic"),
            Value(effective=dt(2025, 7, 1), metric="index_value", curves="ic"),
        ],
        s=[396, 397.1, 398, 398.8],
        instrument_labels=["Apr", "May", "Jun", "Jul"],
    )

    # Bond with mixed fixings and forecast
    ukti_mixed = IndexFixedRateBond(
        effective=dt(2024, 9, 16),
        termination=dt(2025, 9, 16),
        fixed_rate=3.0,
        notional=-15e6,
        index_base=RPI_series,
        index_method="daily",
        index_lag=3,
        index_fixings=RPI_series,
        spec="uk_gb",
        curves=[index_curve, disc_curve]
    )

    # Index Fixed Leg example
    ifl = IndexFixedLeg(
        effective=dt(2024, 12, 1),
        termination="8m",
        frequency="M",
        fixed_rate=1.0,
        notional=-15e6,
        convention="30360",
        index_base=RPI_series,
        index_fixings=RPI_series,
        index_lag=2,
        index_method="monthly",
        currency="gbp"
    )

    return {
        'RPI_series': RPI_series,
        'ukti': ukti,
        'ukti_mixed': ukti_mixed,
        'ifl': ifl,
        'curves': {'disc': disc_curve, 'index': index_curve},
        'solver': solver
    }


# =============================================================================
# Recipe 16: Inflation Indexes and Curves 2 (Quantlib comparison)
# =============================================================================

def recipe_16_inflation_comparison():
    """Inflation Indexes and Curves 2 (Quantlib comparison)"""
    
    # Historical inflation fixings (indexed to 1st of month)
    inflation_fixings = [
        (dt(2022, 1, 1), 110.70),
        (dt(2022, 2, 1), 111.74),
        (dt(2022, 3, 1), 114.46),
        (dt(2022, 4, 1), 115.11),
        (dt(2022, 5, 1), 116.07),
        (dt(2022, 6, 1), 117.01),
        (dt(2022, 7, 1), 117.14),
        (dt(2022, 8, 1), 117.85),
        (dt(2022, 9, 1), 119.26),
        (dt(2022, 10, 1), 121.03),
        (dt(2022, 11, 1), 120.95),
        (dt(2022, 12, 1), 120.52),
        (dt(2023, 1, 1), 120.27),
        (dt(2023, 2, 1), 121.24),
        (dt(2023, 3, 1), 122.34),
        (dt(2023, 4, 1), 123.12),
        (dt(2023, 5, 1), 123.15),
        (dt(2023, 6, 1), 123.47),
        (dt(2023, 7, 1), 123.36),
        (dt(2023, 8, 1), 124.03),
        (dt(2023, 9, 1), 124.43),
        (dt(2023, 10, 1), 124.54),
        (dt(2023, 11, 1), 123.85),
        (dt(2023, 12, 1), 124.05),
        (dt(2024, 1, 1), 123.60),
        (dt(2024, 2, 1), 124.37),
        (dt(2024, 3, 1), 125.31),
        (dt(2024, 4, 1), 126.05),
    ]
    dates, values = zip(*inflation_fixings)
    fixings = Series(values, dates)

    # Nominal discount curve (3% continuously compounded)
    nominal_curve = Curve(
        nodes={dt(2024, 5, 11): 1.0, dt(2074, 5, 18): 1.0},
        interpolation="log_linear",
        convention="Act365F",
        id="discount"
    )
    solver1 = Solver(
        curves=[nominal_curve],
        instruments=[Value(dt(2074, 5, 11), metric="cc_zero_rate", curves="discount")],
        s=[3.0],
        id="rates",
        instrument_labels=["nominal"],
    )

    # Inflation curve calibrated with ZCIS rates
    inflation_curve = Curve(
        nodes={
            dt(2024, 4, 1): 1.0,  # last known inflation print
            dt(2025, 5, 11): 1.0,  # 1y
            dt(2026, 5, 11): 1.0,  # 2y
            dt(2027, 5, 11): 1.0,  # 3y
            dt(2028, 5, 11): 1.0,  # 4y
            dt(2029, 5, 11): 1.0,  # 5y
            dt(2031, 5, 11): 1.0,  # 7y
            dt(2034, 5, 11): 1.0,  # 10y
            dt(2036, 5, 11): 1.0,  # 12y
            dt(2039, 5, 11): 1.0,  # 15y
            dt(2044, 5, 11): 1.0,  # 20y
            dt(2049, 5, 11): 1.0,  # 25y
            dt(2054, 5, 11): 1.0,  # 30y
            dt(2064, 5, 11): 1.0,  # 40y
            dt(2074, 5, 11): 1.0,  # 50y
        },
        interpolation="log_linear",
        convention="Act365F",
        index_base=126.05,
        index_lag=0,
        id="inflation"
    )

    # ZCIS instruments for calibration
    zcis_instruments = [
        ZCIS(dt(2024, 5, 11), "1y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "2y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "3y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "4y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "5y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "7y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "10y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "12y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "15y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "20y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "25y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "30y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "40y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
        ZCIS(dt(2024, 5, 11), "50y", spec="eur_zcis", curves=["inflation", "discount"], leg2_index_fixings=fixings),
    ]
    
    zcis_rates = [2.93, 2.95, 2.965, 2.98, 3.0, 3.06, 3.175, 3.243, 3.293, 3.338, 3.348, 3.348, 3.308, 3.228]
    
    solver = Solver(
        pre_solvers=[solver1],
        curves=[inflation_curve],
        instruments=zcis_instruments,
        s=zcis_rates,
        instrument_labels=["1y", "2y", "3y", "4y", "5y", "7y", "10y", "12y", "15", "20y", "25y", "30y", "40y", "50y"],
        id="zcis",
    )

    # Seasonality curve for composite inflation curve
    seasonality = Curve(
        nodes={
            dt(2024, 4, 1): 1.0,
            dt(2025, 3, 1): 1.0,
            dt(2025, 4, 1): 1.0,
            dt(2025, 5, 1): 1.0,
            dt(2025, 6, 1): 1.0,
            dt(2025, 7, 1): 1.0,
            dt(2074, 5, 11): 1.0
        },
        convention="Act365F",
        id="season"
    )
    
    solver_s2 = Solver(
        curves=[seasonality],
        instruments=[
            Value(dt(2024, 4, 1), curves="season", metric="o/n_rate"),
            Value(dt(2025, 3, 1), curves="season", metric="o/n_rate"),
            Value(dt(2025, 4, 1), curves="season", metric="o/n_rate"),
            Value(dt(2025, 5, 1), curves="season", metric="o/n_rate"),
            Value(dt(2025, 6, 1), curves="season", metric="o/n_rate"),
            Value(dt(2025, 7, 1), curves="season", metric="o/n_rate"),
        ],
        s=[0.0, -0.3, 0.3, -0.4, 0.4, 0.0],
        instrument_labels=["s0", "s1", "s2", "s3", "s4", "s5"],
        id="seasonality",
    )

    # Composite curve with seasonality
    adjusted_inflation = CompositeCurve(curves=[inflation_curve, seasonality], id="adj_inflation")

    # Example ZCIS for risk analysis
    zcis = ZCIS(dt(2024, 3, 11), "4y", spec="eur_zcis", curves=["adj_inflation", "discount"], fixed_rate=3.0, leg2_index_fixings=fixings)

    return {
        'fixings': fixings,
        'curves': {'nominal': nominal_curve, 'inflation': inflation_curve, 'seasonality': seasonality, 'adjusted': adjusted_inflation},
        'instruments': {'zcis_list': zcis_instruments, 'zcis_example': zcis},
        'solvers': {'nominal': solver1, 'inflation': solver, 'seasonality': solver_s2}
    }


# =============================================================================
# Main execution and example usage
# =============================================================================

if __name__ == "__main__":
    print("Rateslib Cookbook Recipes Extracted")
    print("=" * 40)
    
    # You can run individual recipes like this:
    # result_13 = recipe_13_eurusd_market()
    # result_14 = recipe_14_bond_conventions() 
    # result_15 = recipe_15_index_curves()
    # result_16 = recipe_16_inflation_comparison()
    
    print("Available recipe functions:")
    print("- recipe_13_eurusd_market()")
    print("- recipe_14_bond_conventions()")
    print("- recipe_15_index_curves()")
    print("- recipe_16_inflation_comparison()")
    print("\nNote: Recipes 17, 19-24, 26-28 could not be extracted due to network connectivity issues.")