class DosesAndPaths:
    """
    Data-class
    """
    empty_field_file = None
    empty_scanner_field_file = None
    irrad_film_file = None
    calculation_doses = list()
    red_channel_blank = None
    p_opt = None
    doses = list()
    paths = list()
    sigma = 0
    z = list()
    basis_formatter = 0.17
    curve_object = None
    zero_from_db = None
    vmin = None
    vmax = None
    fit_func_type = None
    irrad_film_array = None
    irrad_film_array_original = None