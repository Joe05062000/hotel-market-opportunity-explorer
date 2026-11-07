"""Pricing comparisons and validation of user-supplied daily room totals."""
import csv
from datetime import date
import io
import math

from public_core import revenue_scenario

CSV_COLUMNS = ('date', 'rooms_available', 'rooms_sold', 'room_revenue')
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
SYNTHETIC_CSV = (
    'date,rooms_available,rooms_sold,room_revenue\n'
    '2026-01-01,100,80,24000\n'
    '2026-01-02,80,40,10000\n'
)


def pricing_decision(rooms, days, baseline_rate, baseline_occ, proposed_rate, proposed_occ):
    baseline = revenue_scenario(rooms, days, baseline_occ, baseline_rate)
    proposed = revenue_scenario(rooms, days, proposed_occ, proposed_rate)
    capacity = baseline['available_room_nights']
    threshold = None
    if not capacity or (not proposed_rate and not baseline['room_revenue']):
        status = 'any'
    elif not proposed_rate:
        status = 'impossible'
    else:
        threshold = baseline['revpar'] / proposed_rate * 100
        status = 'above_capacity' if threshold > 100 else 'reachable'
    return {
        'baseline': baseline, 'proposed': proposed, 'status': status,
        'parity_occupancy': threshold,
        'occupancy_cushion': None if threshold is None else proposed_occ - threshold,
        'revenue_change': proposed['room_revenue'] - baseline['room_revenue'],
        'revpar_change': proposed['revpar'] - baseline['revpar'],
    }


def summarize_upload(raw):
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError('Use a CSV no larger than 5 MB.')
    try:
        reader = csv.reader(io.StringIO(raw.decode('utf-8-sig')), strict=True)
        header = next(reader, [])
        if len(header) != len(CSV_COLUMNS) or set(header) != set(CSV_COLUMNS):
            raise ValueError('Expected four columns: date, rooms_available, rooms_sold, room_revenue.')
        dates = set()
        available = sold = 0
        revenues = []
        for row in reader:
            if not row:
                continue
            if len(row) != len(header):
                raise ValueError(f'Line {reader.line_num}: expected four fields.')
            values = dict(zip(header, (value.strip() for value in row)))
            try:
                day = date.fromisoformat(values['date'])
                if day.isoformat() != values['date']:
                    raise ValueError
            except ValueError:
                raise ValueError(f'Line {reader.line_num}: use a valid YYYY-MM-DD date.') from None
            if day in dates:
                raise ValueError(f'Line {reader.line_num}: duplicate date.')
            try:
                a, s = int(values['rooms_available']), int(values['rooms_sold'])
                r = float(values['room_revenue'])
                if min(a, s, r) < 0 or not all(map(math.isfinite, (a, s, r))):
                    raise ValueError
            except (ValueError, OverflowError):
                raise ValueError(f'Line {reader.line_num}: room counts must be nonnegative integers and revenue must be finite and nonnegative.') from None
            if s > a:
                raise ValueError(f'Line {reader.line_num}: rooms sold exceed rooms available.')
            if not s and r:
                raise ValueError(f'Line {reader.line_num}: positive room revenue requires rooms sold.')
            dates.add(day)
            available += a
            sold += s
            revenues.append(r)
        if not dates:
            raise ValueError('Include at least one daily data row.')
        revenue = math.fsum(revenues)
        return {
            'start': min(dates), 'end': max(dates), 'rows': len(dates),
            'rooms_available': available, 'rooms_sold': sold, 'room_revenue': revenue,
            'occupancy': sold / available * 100 if available else None,
            'adr': revenue / sold if sold else None,
            'revpar': revenue / available if available else None,
        }
    except (UnicodeError, csv.Error, OverflowError):
        raise ValueError('Use a well-formed UTF-8 CSV with finite period totals.') from None
