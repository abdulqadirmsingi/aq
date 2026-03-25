BEGIN;

INSERT INTO data_categories (id, slug, name, description, config, created_at, updated_at)
VALUES
  (
    gen_random_uuid(),
    'energy',
    'Energy',
    'Energy market prices, tariffs, and regulatory observations.',
    '{}'::jsonb,
    now(),
    now()
  ),
  (
    gen_random_uuid(),
    'money',
    'Money',
    'Exchange rates, inflation, and financial market observations.',
    '{}'::jsonb,
    now(),
    now()
  ),
  (
    gen_random_uuid(),
    'hr',
    'Human Resources',
    'Salary and employment market observations.',
    '{}'::jsonb,
    now(),
    now()
  ),
  (
    gen_random_uuid(),
    'medicine',
    'Medicine',
    'Medicine and drug price observations.',
    '{}'::jsonb,
    now(),
    now()
  ),
  (
    gen_random_uuid(),
    'living_cost',
    'Living Cost',
    'Land, rent, and cost-of-living observations.',
    '{}'::jsonb,
    now(),
    now()
  )
ON CONFLICT (slug) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  updated_at = now();

INSERT INTO sources (
  id,
  slug,
  name,
  source_type,
  description,
  url,
  reliability_score,
  is_active,
  metadata,
  created_at,
  updated_at
)
VALUES
  (
    gen_random_uuid(),
    'ewura',
    'EWURA',
    'government',
    'Energy and Water Utilities Regulatory Authority petroleum cap price bulletins.',
    'https://www.ewura.go.tz/pages/petroleum-product-pricing',
    0.950,
    true,
    '{"country":"Tanzania","domain":"energy"}'::jsonb,
    now(),
    now()
  )
ON CONFLICT (slug) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  url = EXCLUDED.url,
  reliability_score = EXCLUDED.reliability_score,
  is_active = EXCLUDED.is_active,
  metadata = EXCLUDED.metadata,
  updated_at = now();

WITH category_energy AS (
  SELECT id
  FROM data_categories
  WHERE slug = 'energy'
),
source_ewura AS (
  SELECT id
  FROM sources
  WHERE slug = 'ewura'
)
INSERT INTO metrics (
  id,
  slug,
  name,
  unit,
  description,
  category_id,
  canonical_source_id,
  value_type,
  default_frequency,
  is_location_required,
  validation_rules,
  dimensions_schema,
  created_at,
  updated_at
)
SELECT
  gen_random_uuid(),
  metric_seed.slug,
  metric_seed.name,
  'TZS/Litre',
  metric_seed.description,
  category_energy.id,
  source_ewura.id,
  'numeric',
  'monthly',
  true,
  '{"min":0,"max":100000}'::jsonb,
  '{"fuel_type":{"type":"string"},"document_url":{"type":"string"}}'::jsonb,
  now(),
  now()
FROM category_energy
CROSS JOIN source_ewura
CROSS JOIN (
  VALUES
    (
      'ewura_petrol_cap_price',
      'EWURA Petrol Cap Price',
      'Monthly EWURA retail cap price for petrol.'
    ),
    (
      'ewura_diesel_cap_price',
      'EWURA Diesel Cap Price',
      'Monthly EWURA retail cap price for diesel.'
    ),
    (
      'ewura_kerosene_cap_price',
      'EWURA Kerosene Cap Price',
      'Monthly EWURA retail cap price for kerosene.'
    )
) AS metric_seed(slug, name, description)
ON CONFLICT (slug) DO UPDATE SET
  name = EXCLUDED.name,
  unit = EXCLUDED.unit,
  description = EXCLUDED.description,
  category_id = EXCLUDED.category_id,
  canonical_source_id = EXCLUDED.canonical_source_id,
  value_type = EXCLUDED.value_type,
  default_frequency = EXCLUDED.default_frequency,
  is_location_required = EXCLUDED.is_location_required,
  validation_rules = EXCLUDED.validation_rules,
  dimensions_schema = EXCLUDED.dimensions_schema,
  updated_at = now();

WITH tz_country AS (
  INSERT INTO locations (
    id,
    name,
    code,
    level,
    parent_id,
    country_code,
    path,
    is_active,
    created_at,
    updated_at
  )
  VALUES (
    gen_random_uuid(),
    'Tanzania',
    'TZ',
    'country',
    NULL,
    'TZA',
    'TZ',
    true,
    now(),
    now()
  )
  ON CONFLICT (path) DO UPDATE SET
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    country_code = EXCLUDED.country_code,
    is_active = EXCLUDED.is_active,
    updated_at = now()
  RETURNING id
),
country_row AS (
  SELECT id FROM tz_country
  UNION ALL
  SELECT id FROM locations WHERE path = 'TZ'
),
region_seed AS (
  SELECT *
  FROM (
    VALUES
      ('Arusha', 'ARU', 'TZ/arusha', 'Arusha', 'ARU-CAP', 'TZ/arusha/arusha'),
      ('Dar es Salaam', 'DSM', 'TZ/dar-es-salaam', 'Dar es Salaam', 'DSM-CAP', 'TZ/dar-es-salaam/dar-es-salaam'),
      ('Dodoma', 'DOD', 'TZ/dodoma', 'Dodoma', 'DOD-CAP', 'TZ/dodoma/dodoma'),
      ('Geita', 'GET', 'TZ/geita', 'Geita', 'GET-CAP', 'TZ/geita/geita'),
      ('Iringa', 'IRI', 'TZ/iringa', 'Iringa', 'IRI-CAP', 'TZ/iringa/iringa'),
      ('Kagera', 'KAG', 'TZ/kagera', 'Bukoba', 'BUK-CAP', 'TZ/kagera/bukoba'),
      ('Katavi', 'KTV', 'TZ/katavi', 'Mpanda', 'MPD-CAP', 'TZ/katavi/mpanda'),
      ('Kigoma', 'KIG', 'TZ/kigoma', 'Kigoma', 'KIG-CAP', 'TZ/kigoma/kigoma'),
      ('Kilimanjaro', 'KIL', 'TZ/kilimanjaro', 'Moshi', 'MSH-CAP', 'TZ/kilimanjaro/moshi'),
      ('Lindi', 'LIN', 'TZ/lindi', 'Lindi', 'LIN-CAP', 'TZ/lindi/lindi'),
      ('Manyara', 'MNY', 'TZ/manyara', 'Babati', 'BBT-CAP', 'TZ/manyara/babati'),
      ('Mara', 'MAR', 'TZ/mara', 'Musoma', 'MUS-CAP', 'TZ/mara/musoma'),
      ('Mbeya', 'MBY', 'TZ/mbeya', 'Mbeya', 'MBY-CAP', 'TZ/mbeya/mbeya'),
      ('Mjini Magharibi', 'MJM', 'TZ/mjini-magharibi', 'Zanzibar City', 'ZNZ-CAP', 'TZ/mjini-magharibi/zanzibar-city'),
      ('Morogoro', 'MOR', 'TZ/morogoro', 'Morogoro', 'MOR-CAP', 'TZ/morogoro/morogoro'),
      ('Mtwara', 'MTW', 'TZ/mtwara', 'Mtwara', 'MTW-CAP', 'TZ/mtwara/mtwara'),
      ('Mwanza', 'MWZ', 'TZ/mwanza', 'Mwanza', 'MWZ-CAP', 'TZ/mwanza/mwanza'),
      ('Njombe', 'NJO', 'TZ/njombe', 'Njombe', 'NJO-CAP', 'TZ/njombe/njombe'),
      ('Pemba North', 'PNR', 'TZ/pemba-north', 'Wete', 'WET-CAP', 'TZ/pemba-north/wete'),
      ('Pemba South', 'PSR', 'TZ/pemba-south', 'Chake Chake', 'CCK-CAP', 'TZ/pemba-south/chake-chake'),
      ('Pwani', 'PWA', 'TZ/pwani', 'Kibaha', 'KIB-CAP', 'TZ/pwani/kibaha'),
      ('Rukwa', 'RKW', 'TZ/rukwa', 'Sumbawanga', 'SUM-CAP', 'TZ/rukwa/sumbawanga'),
      ('Ruvuma', 'RUV', 'TZ/ruvuma', 'Songea', 'SGA-CAP', 'TZ/ruvuma/songea'),
      ('Shinyanga', 'SHY', 'TZ/shinyanga', 'Shinyanga', 'SHY-CAP', 'TZ/shinyanga/shinyanga'),
      ('Simiyu', 'SIM', 'TZ/simiyu', 'Bariadi', 'BRD-CAP', 'TZ/simiyu/bariadi'),
      ('Singida', 'SIN', 'TZ/singida', 'Singida', 'SIN-CAP', 'TZ/singida/singida'),
      ('Songwe', 'SNG', 'TZ/songwe', 'Vwawa', 'VWA-CAP', 'TZ/songwe/vwawa'),
      ('Tabora', 'TAB', 'TZ/tabora', 'Tabora', 'TAB-CAP', 'TZ/tabora/tabora'),
      ('Tanga', 'TNG', 'TZ/tanga', 'Tanga', 'TNG-CAP', 'TZ/tanga/tanga'),
      ('Unguja North', 'UNG-N', 'TZ/unguja-north', 'Mkokotoni', 'MKK-CAP', 'TZ/unguja-north/mkokotoni'),
      ('Unguja South', 'UNG-S', 'TZ/unguja-south', 'Koani', 'KNI-CAP', 'TZ/unguja-south/koani')
  ) AS region_seed(region_name, region_code, region_path, capital_name, capital_code, capital_path)
),
region_upsert AS (
  INSERT INTO locations (
    id,
    name,
    code,
    level,
    parent_id,
    country_code,
    path,
    is_active,
    created_at,
    updated_at
  )
  SELECT
    gen_random_uuid(),
    region_seed.region_name,
    region_seed.region_code,
    'region',
    country_row.id,
    'TZA',
    region_seed.region_path,
    true,
    now(),
    now()
  FROM country_row
  CROSS JOIN region_seed
  ON CONFLICT (path) DO UPDATE SET
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    is_active = EXCLUDED.is_active,
    updated_at = now()
  RETURNING id, path
)
INSERT INTO locations (
  id,
  name,
  code,
  level,
  parent_id,
  country_code,
  path,
  is_active,
  created_at,
  updated_at
)
SELECT
  gen_random_uuid(),
  city_seed.capital_name,
  city_seed.capital_code,
  'city',
  parent_region.id,
  'TZA',
  city_seed.capital_path,
  true,
  now(),
  now()
FROM region_seed AS city_seed
JOIN locations AS parent_region
  ON parent_region.path = city_seed.region_path
ON CONFLICT (path) DO UPDATE SET
  name = EXCLUDED.name,
  code = EXCLUDED.code,
  is_active = EXCLUDED.is_active,
  updated_at = now();

COMMIT;
