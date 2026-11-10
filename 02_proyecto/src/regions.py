REGIONES = {
    "Sudamérica": [
        "Bolivia (Plurinational State of)", "Brazil", "Colombia", "Ecuador",
        "Guyana", "Paraguay", "Peru", "Venezuela",
    ],
    "Centroamérica y Caribe": [
        "Costa Rica", "Cuba", "Dominican Republic", "El Salvador", "Guatemala", "Haiti",
        "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Trinidad & Tobago",
    ],
    "África": [
        "Angola", "Burundi", "Cameroon", "Central African Republic", "Congo", "Côte d'Ivoire",
        "Democratic Republic of Congo", "Equatorial Guinea", "Ethiopia", "Gabon", "Ghana",
        "Guinea", "Kenya", "Liberia", "Madagascar", "Malawi", "Nigeria", "Rwanda",
        "Sierra Leone", "Tanzania", "Togo", "Uganda", "Zambia", "Zimbabwe",
    ],
    "Asia y Oceanía": [
        "India", "Indonesia", "Lao People's Democratic Republic", "Nepal", "Papua New Guinea",
        "Philippines", "Sri Lanka", "Thailand", "Timor-Leste", "Viet Nam", "Yemen",
    ],
}

PAIS_REGION = {pais: region for region, paises in REGIONES.items() for pais in paises}


def add_region(df, col="country"):
    return df.assign(region=df[col].map(PAIS_REGION).fillna("Sin región"))