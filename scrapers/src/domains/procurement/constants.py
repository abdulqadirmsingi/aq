"""NeST PPRA procurement scraper constants."""

PROCUREMENT_CATEGORY_SLUG = "procurement"
PROCUREMENT_CATEGORY_NAME = "Public Procurement"
PROCUREMENT_CATEGORY_DESCRIPTION = (
    "Tanzania government procurement data from the National e-Procurement System "
    "(NeST), published by the Public Procurement Regulatory Authority (PPRA)."
)

NEST_SOURCE_SLUG = "nest_ppra"
NEST_SOURCE_NAME = "NeST PPRA Open Data"
NEST_SOURCE_DESCRIPTION = (
    "Open contracting data from Tanzania's National e-Procurement System, "
    "published under the Open Contracting Data Standard (OCDS) by PPRA."
)
NEST_SOURCE_URL = "https://data.nest.go.tz"

NEST_OCDS_PREFIX = "ocds-mv5oob"

DEFAULT_NEST_OCDS_API_URL = "https://nest.go.tz/gateway/nest-data-portal-api/api"
