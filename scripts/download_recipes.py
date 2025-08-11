"""
Script to download all cookbook recipes from rateslib documentation
"""

# List of all 29 cookbook recipes with their URLs
RECIPES = [
    # Interest Rate Curve Building
    ("01_single_currency_curve", "z_ptirds_curve.html", "Replicating the Single Currency Curve"),
    ("02_sofr_curve", "z_swpm.html", "Building a Conventional Par Tenor Based SOFR Curve"),
    ("03_dependency_chain", "z_dependencychain.html", "Solving Curves with a Dependency Chain"),
    ("04_handle_turns", "z_turns.html", "How to Handle Turns in Rateslib"),
    ("05_quantlib_comparison", "z_quantlib.html", "Comparing Curve Building with QuantLib"),
    ("06_zero_rates", "z_curve_from_zero_rates.html", "Constructing Curves from Zero Rates"),
    ("07_multicurve_framework", "z_multicurveframework.html", "Multicurve Framework Construction"),
    ("08_brazil_bus252", "z_bus252_convention.html", "Brazil's Bus252 Convention"),
    ("09_nelson_siegel", "z_basecurve.html", "Building Custom Curves (Nelson-Siegel)"),
    
    # Credit Curve Building
    ("10_pfizer_cds", "z_cdsw.html", "Replicating a Pfizer Default Curve & CDS"),
    
    # FX Volatility Surface Building
    ("11_fx_surface_interpolation", "z_fxvol_surface_construction.html", "Comparing Surface Interpolation"),
    ("12_fx_temporal", "z_fxvol_temporal.html", "FX Volatility Surface Temporal Interpolation"),
    ("13_eurusd_market", "z_eurusd_surface.html", "EURUSD market for IRS and FX volatility"),
    
    # Instrument Pricing
    ("14_bond_conventions", "z_bond_conventions.html", "Understanding Bond Conventions"),
    ("15_inflation_instruments", "z_index_bonds_and_fixings.html", "Inflation Instruments"),
    ("16_inflation_quantlib", "z_inflation_indexes.html", "Inflation Indexes (Quantlib comparison)"),
    ("17_ibor_stubs", "z_stubs.html", "Pricing IBOR Interpolated Stub Periods"),
    ("18_fixings", "z_fixings.html", "Working with Fixings"),
    ("19_historical_swaps", "z_historical_swap.html", "Valuing Historical Swaps"),
    ("20_amortization", "z_amortization.html", "Applying Amortization to Instruments"),
    ("21_cross_currency", "z_reverse_xcs.html", "Configuring Cross-Currency Swaps"),
    
    # Risk Sensitivity Analysis
    ("22_convexity_risk", "z_convexityrisk.html", "Building a Risk Framework with Convexity"),
    ("23_bond_basis", "z_bondbasis.html", "Exploring Bond Basis and Futures DV01"),
    ("24_bond_ctd", "z_bondctd.html", "Bond Future CTD Multi-Scenario Analysis"),
    ("25_exogenous_variables", "z_exogenous.html", "Exogenous Variables and Sensitivities"),
    ("26_sabr_beta", "z_exogenous_beta.html", "SABR's Beta as Exogenous Variable"),
    ("27_fixings_exposures", "z_fixings_exposures.html", "Fixings Exposures and Reset Ladders"),
    ("28_multicsa_curves", "z_multicsa.html", "MultiCsaCurves discontinuous derivatives"),
]

BASE_URL = "https://rateslib.com/py/en/latest/"

def get_recipe_urls():
    """Get all recipe URLs"""
    return [(name, BASE_URL + url, title) for name, url, title in RECIPES]

if __name__ == "__main__":
    for name, url, title in get_recipe_urls():
        print(f"{name}: {title}")
        print(f"  URL: {url}")