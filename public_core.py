"""No API calls, secrets, private file loading, or historical observations."""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parent
QUESTIONS = [
    'How has NYC hotel occupancy changed?',
    'How have average room rates changed?',
    'What does the available visitor data show?',
    'What happens to RevPAR if occupancy or ADR changes?',
    'What evidence is missing from this market assessment?',
]
DEFINITIONS = {
    'Occupancy': 'Sold room-nights divided by available room-nights for the same period, expressed as a percentage.',
    'ADR': 'Realized room revenue divided by sold room-nights, in nominal USD. An advertised booking offer is not realized ADR.',
    'RevPAR': 'Room revenue per available room-night. With matching inputs: ADR × occupancy / 100 when occupancy is entered as a percentage.',
    'Visitors': 'Estimated visits, potentially including day trips and overnight trips; not a count of hotel guests.',
    'Room revenue': 'Expected sold room-nights × ADR. This excludes operating costs, taxes and other revenue; it is not profit.',
}
DEFAULT_CASES = {
    'Downside': dict(rooms=100, operating_days=365, occupancy=65.0, adr=250.0),
    'Base': dict(rooms=100, operating_days=365, occupancy=80.0, adr=300.0),
    'Upside': dict(rooms=100, operating_days=365, occupancy=90.0, adr=350.0),
}


def load_metadata():
    sources=json.loads((ROOT/'data/sources.json').read_text())
    manifest=json.loads((ROOT/'data/release_manifest.json').read_text())
    if manifest['observations_included'] or manifest['historical_numeric_claims_enabled'] or manifest['approved_observation_files']:
        raise ValueError('This public edition has no approved historical observation files.')
    if set(manifest['source_ids']) != {s['source_id'] for s in sources}:
        raise ValueError('Source register and release manifest disagree.')
    for source in sources:
        if not source['url'].startswith('https://') or not source['reuse'] or not source['public_disposition']:
            raise ValueError('Incomplete provenance metadata')
    return {s['source_id']: s for s in sources},manifest


def revenue_scenario(rooms, operating_days, occupancy, adr):
    for name,value in [('rooms',rooms),('operating_days',operating_days)]:
        if isinstance(value,bool) or not math.isfinite(float(value)) or value < 0 or int(value) != value:
            raise ValueError(f'{name} must be a nonnegative integer')
    if not all(math.isfinite(float(v)) for v in [occupancy,adr]) or not 0 <= occupancy <= 100 or adr < 0:
        raise ValueError('Occupancy must be between zero and one hundred percent; ADR must be nonnegative.')
    available=int(rooms)*int(operating_days)
    sold=available*float(occupancy)/100
    revenue=sold*float(adr)
    return dict(rooms=int(rooms),operating_days=int(operating_days),occupancy=float(occupancy),adr=float(adr),
                available_room_nights=available,sold_room_nights=sold,room_revenue=revenue,revpar=float(adr)*float(occupancy)/100)


def source_link(source):
    return f"[{source['publisher']} — {source['title']}]({source['url']})"


def guided_answer(question,sources):
    if question not in QUESTIONS: raise ValueError('Unknown preset')
    if question == QUESTIONS[3]:
        return ('**Hypothetical calculation:** RevPAR = ADR × occupancy / 100. Use the controls below to compare two assumptions. '
                'These inputs are not historical data, current market rates or forecasts. '
                'Changing price may affect demand in practice; this arithmetic does not estimate that relationship.')
    if question == QUESTIONS[4]:
        return ('**Evidence unavailable in the public edition:** historical occupancy, ADR, RevPAR and visitor observations have been withheld pending reuse clearance. '
                'Class-matched borough rates, performance sample counts and property operating costs are not supplied. '
                'No trend, borough ranking, market opportunity score or investment recommendation can be supported. '
                'The source register provides reporting coverage and unresolved restrictions, not a licensed numerical dataset.')
    metric={QUESTIONS[0]:'occupancy',QUESTIONS[1]:'ADR',QUESTIONS[2]:'visitor volume'}[question]
    relevant=['nyc_cash_2025q2','tourism_2025'] if metric != 'visitor volume' else ['tourism_trends_2024','tourism_2025']
    refs='\n\n'.join(f"{source_link(sources[sid])} · reporting coverage: {sources[sid]['reporting_periods']}." for sid in relevant)
    return (f'**No historical {metric} comparison is available in this public edition.** '
            'The reviewed observations are excluded until permission or an applicable reuse license is established. '
            'No missing values have been fabricated and no scenarios are presented as historical evidence. '
            'Review these original publications for their own reported results:\n\n'+refs+
            '\n\nPublic access and attribution do not establish redistribution permission. Historical series must also match geography, frequency, hotel category and reporting population before comparison.')


def public_brief(sources,scenarios=None):
    lines=['# Hotel Market Opportunity Explorer — Public Evidence Brief',
           'Generated locally by Python templates, without an API. This is an evidence-availability brief, not a numerical assessment of the NYC hotel market.',
           '## Release scope',
           'Historical hotel and visitor observations, historical charts and derived market findings are excluded pending reuse clearance. Source metadata was reviewed on November 2, 2026.',
           '## Evidence-readiness findings',
           '1. Numerical historical comparisons cannot be reproduced from this release because no approved observations are bundled. This is a release limitation, not a claim that no external data exist.',
           '2. A class-matched comparison across all five boroughs is not established. Reviewed aggregate reports do not provide an approved, class-matched dataset with performance sample sizes for this release.',
           '3. Room-revenue scenarios can be calculated transparently from user assumptions, but cannot establish demand, profitability or investment suitability.',
           '## Business interpretation and risks',
           'Obtain appropriate reuse rights and comparable observations before making market claims. Examine active room supply, hotel category/guest mix, seasonality and operating costs. Correlation and arithmetic attribution do not establish causation.',
           '## Hypothetical scenarios']
    if scenarios:
        rows=['| Case (hypothetical) | Rooms | Days | Occupancy (%) | ADR (USD) | Available room-nights | Sold room-nights | Room revenue (USD) | RevPAR (USD) |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for name,case in scenarios.items():
            r=revenue_scenario(**{k:case[k] for k in ['rooms','operating_days','occupancy','adr']})
            rows.append(f"| {name} | {r['rooms']} | {r['operating_days']} | {r['occupancy']:.1f} | {r['adr']:.2f} | {r['available_room_nights']:,} | {r['sold_room_nights']:,.2f} | {r['room_revenue']:,.2f} | {r['revpar']:.2f} |")
        lines.append('\n'.join(rows))
    else: lines.append('No scenario assumptions selected for inclusion.')
    lines.extend(['Available room-nights = rooms × operating days; sold room-nights = available × occupancy / 100; room revenue = sold × ADR; RevPAR = ADR × occupancy / 100.',
                  'All scenario inputs are hypothetical and have no historical reporting dates. Room revenue excludes costs and is not profit. Expected sold room-nights may be fractional.',
                  '## Source register — references only, observations not redistributed'])
    for source in sources.values():
        lines.append(f"- {source_link(source)}. Reporting coverage: {source['reporting_periods']}. Retrieved {source['retrieved_on']}. Reuse: {source['reuse']}")
    return '\n\n'.join(lines)+'\n'
