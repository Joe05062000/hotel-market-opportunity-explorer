"""Public, session-only pricing decision interface."""
import math

import plotly.graph_objects as go
import streamlit as st

from pricing import MAX_UPLOAD_BYTES, SYNTHETIC_CSV, pricing_decision, summarize_upload


def pricing_heatmap(result):
    baseline, proposed = result['baseline'], result['proposed']
    capacity = baseline['available_room_nights']
    top_rate = max(100, baseline['adr'], proposed['adr']) * 1.15
    rates = [top_rate * i / 50 for i in range(51)]
    occupancies = list(range(0, 101, 2))
    target = baseline['revpar']
    delta = [[capacity * (rate * occ / 100 - target) for rate in rates] for occ in occupancies]
    span = max(1, abs(delta[0][0]), abs(delta[-1][-1]))
    fig = go.Figure(go.Heatmap(
        x=rates, y=occupancies, z=delta, zmin=-span, zmax=span,
        colorscale=[[0, '#a94c3e'], [.5, '#faf7ef'], [1, '#087f8c']],
        colorbar={'title': 'Revenue change<br>(USD)'},
        hovertemplate='Rate: $%{x:,.2f}<br>Assumed occupancy: %{y:.0f}%<br>Revenue change: $%{z:,.0f}<extra></extra>',
    ))
    if capacity and target and target <= top_rate:
        parity_rates = [target + (top_rate - target) * i / 100 for i in range(101)]
        fig.add_scatter(x=parity_rates, y=[100 * target / rate for rate in parity_rates],
                        mode='lines', name='Room-revenue parity', line={'color': '#142b43', 'width': 3, 'dash': 'dash'})
    elif capacity and not target:
        fig.add_scatter(x=[0, 0, top_rate], y=[100, 0, 0], mode='lines',
                        name='Room-revenue parity', line={'color': '#142b43', 'width': 3, 'dash': 'dash'})
    for name, case, symbol in [('Baseline', baseline, 'circle-open'), ('Proposed', proposed, 'diamond')]:
        fig.add_scatter(x=[case['adr']], y=[case['occupancy']], name=name, mode='markers',
                        marker={'symbol': symbol, 'size': 15, 'color': '#142b43', 'line': {'width': 2, 'color': '#faf7ef' if name == 'Proposed' else '#142b43'}})
    fig.update_layout(xaxis_title='Room rate (USD per sold room-night)', yaxis_title='Assumed occupancy (%)',
                      yaxis={'range': [-3, 103]}, xaxis={'range': [-top_rate * .025, top_rate]},
                      legend={'orientation': 'h', 'y': -0.22}, height=440,
                      margin={'t': 20, 'b': 90, 'l': 50, 'r': 25},
                      paper_bgcolor='#faf7ef', plot_bgcolor='#faf7ef')
    return fig


def render_pricing_lab():
    st.subheader('Pricing Decision Lab')
    st.caption('Compare two rates at the same capacity. Occupancy is your assumption; the lab does not forecast demand.')
    capacity, horizon = st.columns(2)
    rooms = capacity.number_input('Fixed room inventory', 0, 100000, 100)
    days = horizon.number_input('Fixed operating days', 0, 3660, 365)
    baseline, proposed = st.columns(2)
    with baseline:
        st.markdown('**Baseline**')
        baseline_rate = st.number_input('Baseline room rate (USD)', 0.0, 2000.0, 300.0, step=5.0)
        baseline_occ = st.number_input('Baseline occupancy (%)', 0.0, 100.0, 80.0, step=0.1)
    with proposed:
        st.markdown('**Proposed**')
        proposed_rate = st.number_input('Proposed room rate (USD)', 0.0, 2000.0, 310.0, step=5.0)
        proposed_occ = st.number_input('Assumed occupancy after change (%)', 0.0, 100.0, 80.0, step=0.1)

    result = pricing_decision(rooms, days, baseline_rate, baseline_occ, proposed_rate, proposed_occ)
    threshold = result['parity_occupancy']
    cushion = result['occupancy_cushion']
    parity_label = 'Any occupancy' if result['status'] == 'any' else 'Unreachable' if threshold is None else f'{threshold:,.2f}%'
    left, right = st.columns(2)
    left.metric('Room-revenue parity', parity_label)
    right.metric('Occupancy cushion', '—' if cushion is None else f'{cushion:+,.2f} pp')
    left, right = st.columns(2)
    left.metric('Room revenue change', f"USD {result['revenue_change']:+,.2f}")
    right.metric('RevPAR change', f"USD {result['revpar_change']:+,.2f}")
    st.caption('Parity matches baseline room revenue before costs. Cushion is assumed occupancy minus the parity threshold, in percentage points.')
    if result['status'] == 'above_capacity':
        st.warning('Parity requires more than 100% occupancy and is unattainable at this proposed rate.')
    elif result['status'] == 'impossible':
        st.warning('A zero proposed rate cannot match positive baseline room revenue at any occupancy.')
    elif result['status'] == 'any':
        st.info('Any occupancy matches baseline room revenue because fixed capacity is zero or both room revenues are zero.')
    change = result['revenue_change']
    if math.isclose(change, 0, abs_tol=.005):
        takeaway = 'Your assumed occupancy matches baseline room revenue to the nearest cent.'
    else:
        direction = 'more' if change > 0 else 'less'
        takeaway = f'At {proposed_occ:.2f}% assumed occupancy, the proposed rate earns USD {abs(change):,.2f} {direction} in room revenue before costs.'
    st.markdown(f'**Takeaway:** {takeaway}')
    st.plotly_chart(pricing_heatmap(result), width='stretch')

    with st.expander('Optional: summarize a daily CSV'):
        st.caption('Use data you are permitted to share with this hosted app. Uploads are processed in the active session and are not saved to files, GitHub, or the evidence brief.')
        st.download_button('Download synthetic example CSV', SYNTHETIC_CSV, 'synthetic_daily_rooms.csv', 'text/csv')
        upload = st.file_uploader('Daily room totals (CSV, up to 5 MB)', type=['csv'])
        if upload is not None:
            try:
                if upload.size > MAX_UPLOAD_BYTES:
                    raise ValueError('Use a CSV no larger than 5 MB.')
                summary = summarize_upload(upload.getvalue())
            except ValueError as error:
                st.error(str(error))
            else:
                st.write(f"Reporting dates: {summary['start']} to {summary['end']} · {summary['rows']} daily rows")
                for column, key, label, fmt in zip(st.columns(3), ('occupancy', 'adr', 'revpar'),
                        ('Occupancy', 'ADR', 'RevPAR'), ('{:.2f}%', '${:,.2f}', '${:,.2f}')):
                    value = summary[key]
                    column.metric(label, 'Unavailable' if value is None else fmt.format(value))
                st.caption('Metrics use period totals from supplied rows only. Missing dates are not filled. Uploaded results do not change the pricing assumptions.')
    with st.expander('How the analysis works'):
        st.markdown("""
- **Room revenue** = rooms × operating days × assumed occupancy ÷ 100 × rate. **RevPAR** = rate × occupancy ÷ 100.
- **Room-revenue parity** = baseline RevPAR ÷ proposed rate × 100. Fixed room inventory and days cancel when capacity is positive. **Cushion** = assumed occupancy minus parity occupancy, in percentage points. The dashed line shows parity where it falls inside the chart.
- **Example:** USD 300 × 80% gives baseline RevPAR of USD 240. At USD 310, parity is 240 ÷ 310 × 100 = **77.42%**. At 80% assumed occupancy, the cushion is **2.58 percentage points** and RevPAR rises **USD 8.00**.
- **Zero cases:** a zero proposed rate cannot match positive baseline revenue. If every occupancy gives equal revenue, there is no unique threshold or cushion. A threshold above 100% is infeasible.
- **CSV checks:** one row per valid YYYY-MM-DD date; nonnegative integer room counts; finite nonnegative room revenue; sold rooms cannot exceed available rooms. Positive revenue requires rooms sold. No missing dates are imputed.
- **Period metrics:** occupancy = total sold ÷ total available; ADR = total room revenue ÷ total sold; RevPAR = total room revenue ÷ total available. Zero denominators show as unavailable.
- This comparison is before costs. The heatmap varies assumptions and makes no claim about how demand responds to price.
""")
