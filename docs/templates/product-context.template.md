# PsyCrawl Product Context

_This file stores reusable context for skill analyses._
_Edit directly or let skills update it automatically._

## Business
```yaml
business:
  name: 'Your Business Name'
  type: 'Industry/Vertical'
  website: 'https://yourdomain.com'
  description: 'Brief description of your business'
  target_audience: 'Who you serve'
  differentiators:
    - 'What makes you unique #1'
    - 'What makes you unique #2'
```

## Geography
```yaml
geography:
  geo_scope: local_radius  # local_radius | multi_location | domestic
  geo_bucket: 0-10  # 0-10 | 10-50 | 50+ (mile radius)
  primary_market: 'City, State'
  headquarters:
    city: 'Your City'
    state: 'ST'
    zip: '12345'
  service_areas:
    - 'Nearby City 1'
    - 'Nearby City 2'
  service_radius: '25 miles'
```

## Known Competitors
```yaml
competitors_known:
  - name: 'Competitor A'
    url: 'https://competitor-a.com'
    notes: 'Main competitor in your area'
  - name: 'Competitor B'
    url: 'https://competitor-b.com'
    notes: 'Secondary competitor'
```

## Previous Analyses
```yaml
# This section is automatically updated by skills
previous_analyses: []
```

## Additional Context
```yaml
keywords:
  primary:
    - 'your main keyword'
    - 'another main keyword'
  secondary:
    - 'related keyword'
goals:
  short_term: 'What you want to achieve this quarter'
  long_term: 'What you want to achieve this year'
notes: 'Any additional context for analyses'
```
