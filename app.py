"""Streamlit Community Cloud entry point for the metadata-only public edition."""
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from public_core import (ROOT, QUESTIONS, DEFAULT_CASES, DEFINITIONS, load_metadata,
                         revenue_scenario, guided_answer, public_brief, source_link)

st.set_page_config(page_title='Hotel Market Opportunity Explorer',page_icon='◈',layout='wide')
st.markdown('''<style>
[data-testid="stAppViewContainer"] {background:#faf7ef;}
[data-testid="stSidebar"] {background:#142b43;}
[data-testid="stSidebar"] * {color:#faf7ef;}
h1,h2,h3 {color:#142b43;}
[data-testid="stMetric"] {background:#fffdf7;border:1px solid #ddd9ce;border-top:4px solid #087f8c;border-radius:10px;padding:18px;}
[data-testid="stMetricValue"] {color:#087f8c;font-size:1.4rem;}
.block-container {padding-top:2.5rem;max-width:1400px;}
.eyebrow {color:#087f8c;letter-spacing:3px;font-size:.8rem;font-weight:700;}
</style>''',unsafe_allow_html=True)
try:
    sources,manifest=load_metadata()
except (ValueError, OSError, KeyError, json.JSONDecodeError):
    st.error('Public-release metadata could not be validated. No historical results will be displayed.')
    st.stop()

with st.sidebar:
    st.markdown('## ◈ HOTEL MARKET')
    st.caption('NYC · PUBLIC PORTFOLIO EDITION')
    page=st.radio('Explore',['Market overview','Historical trends','Borough comparison','Price & demand','Explore the data','Scenario explorer','Market brief','Sources & data quality'])
    st.divider()
    st.caption('Guided data assistant · no API key required')
    st.caption('Historical observations withheld pending reuse clearance.')

st.markdown('<div class="eyebrow">NYC / HOSPITALITY STRATEGY</div>',unsafe_allow_html=True)
st.title('Hotel Market Opportunity Explorer')
st.caption('A guided research and room-revenue scenario tool. Evidence before conclusions.')

if page=='Market overview':
    st.subheader('A transparent public release')
    st.info('Historical observations are not included in this public edition because reuse rights have not been established. No historical KPIs, charts or market rankings are presented.')
    st.markdown('Use the **Guided data assistant** to inspect evidence limits, explore **hypothetical hotel revenue scenarios**, and download a **public evidence brief**. No API key, login or secret is needed to use these features.')
    st.markdown('The source register identifies primary publications, reporting periods and unresolved restrictions. It provides research references, not a licensed historical dataset. No publisher imagery, numerical observations, derived historical screenshots or full reports are distributed.')
    st.markdown('**Research purpose:** assess hotel pricing, utilization, visitor demand and capacity using compatible, permissioned observations. This release demonstrates the calculation workflow while making the current evidence boundary explicit.')
    for name,definition in DEFINITIONS.items():
        with st.expander(name): st.markdown(definition)

elif page=='Historical trends':
    st.subheader('Historical evidence · permission pending')
    st.info('No approved historical observations are bundled. Changes in occupancy, ADR, RevPAR or visitors cannot be calculated or charted in this public edition.')
    st.markdown('Future comparisons must use matching geography, units, reporting population, hotel category and frequency. Annual, monthly and year-to-date observations remain separate. Occupancy changes use percentage points; ADR changes use percent with nominal USD clearly labelled. Missing periods must stay missing; forecasts must not be treated as actuals.')
    for sid in ['nyc_cash_2025q2','tourism_trends_2024']:
        source=sources[sid]
        st.markdown(f"{source_link(source)} · {source['reporting_periods']}. Observations withheld.")

elif page=='Borough comparison':
    st.subheader('Borough coverage · source review only')
    st.markdown('**Historical source snapshot — May 2023.** The reviewed barometer identifies Manhattan, Brooklyn and Queens in its borough KPI table. Numerical ADR and occupancy observations and derived comparisons are excluded from this public edition.')
    st.warning('Bronx and Staten Island are absent from that selected source table. Missing does not mean zero. No borough rate or occupancy ranking is supported in this release.')
    rows=[{'Borough':name,'Source coverage':'Listed; values withheld' if name in ['Manhattan','Brooklyn','Queens'] else 'Absent from selected table','Comparable hotel categories':'Not established','Performance sample size':'Not disclosed in selected table'} for name in ['Manhattan','Brooklyn','Queens','Bronx','Staten Island']]
    st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')
    st.markdown(source_link(sources['tourism_barometer_may2023']))
    st.caption('Differences may reflect hotel category and guest mix. Historical aggregates are not current booking prices or like-for-like comparisons. Advertised booking offers and Airbnb observations are not substituted for realized hotel ADR.')

elif page=='Price & demand':
    st.subheader('Price and demand · evidence requirements')
    st.info('No numerical ADR/occupancy comparison is enabled without approved observations for the same geography, period and reporting population.')
    st.markdown('**Method:** RevPAR = ADR × occupancy decimal. A symmetric arithmetic decomposition splits change into a rate contribution and an occupancy contribution: change in ADR × mean occupancy decimal, plus change in occupancy decimal × mean ADR. This is an accounting identity, not a causal explanation.')
    st.markdown('Occupancy is utilization, not an absolute count of demand. Changing hotel or room mix can alter market aggregates. Profitability also requires costs; room revenue alone cannot establish an investment opportunity.')

elif page=='Explore the data':
    st.subheader('Guided data assistant')
    st.markdown('Preset questions answered by Python templates. These are not AI-generated responses. No API key or external API is used.')
    question=st.selectbox('Choose a question',QUESTIONS)
    st.markdown(guided_answer(question,sources))
    if question==QUESTIONS[3]:
        left,right=st.columns(2)
        results=[]
        for column,name,occ in [(left,'Baseline',80.0),(right,'Adjusted',85.0)]:
            with column:
                occupancy=st.slider(f'{name} assumed occupancy (%)',0.0,100.0,occ,0.5)
                adr=st.number_input(f'{name} assumed ADR (nominal USD)',min_value=0.0,max_value=2000.0,value=300.0,step=5.0)
                result=revenue_scenario(1,1,occupancy,adr)
                st.metric(f'{name} hypothetical RevPAR',f"${result['revpar']:,.2f}")
                results.append(result)
        st.markdown(f"**Calculated scenario change:** USD {results[1]['revpar']-results[0]['revpar']:+,.2f} per available room-night. Formula: ADR × occupancy / 100. All inputs are assumptions, with no historical reporting period.")

elif page=='Scenario explorer':
    st.subheader('Hypothetical hotel room-revenue scenarios')
    st.warning('User assumptions only · not historical results or forecasts. Room revenue excludes costs and is not profit.')
    cases={}
    saved=st.session_state.get('revenue_cases',{})
    for column,(name,initial) in zip(st.columns(3),DEFAULT_CASES.items()):
        default=saved.get(name,initial)
        with column:
            st.markdown(f'**{name} · hypothetical**')
            rooms=st.number_input(f'{name} room count',min_value=0,max_value=100000,value=default['rooms'],step=1,key=f'{name}_rooms')
            days=st.number_input(f'{name} operating days',min_value=0,max_value=3660,value=default['operating_days'],step=1,key=f'{name}_days')
            occupancy=st.slider(f'{name} occupancy (%)',0.0,100.0,default['occupancy'],0.5,key=f'{name}_occupancy')
            adr=st.number_input(f'{name} ADR (nominal USD / sold room-night)',min_value=0.0,max_value=2000.0,value=default['adr'],step=5.0,key=f'{name}_adr')
            case=revenue_scenario(rooms,days,occupancy,adr)
            cases[name]=case
            st.metric(f'{name} room revenue',f"${case['room_revenue']:,.2f}")
            st.metric(f'{name} RevPAR',f"${case['revpar']:,.2f}")
    st.session_state['revenue_cases']=cases
    results=pd.DataFrame([{'Hypothetical case':name,**case} for name,case in cases.items()])
    if not cases['Downside']['room_revenue'] <= cases['Base']['room_revenue'] <= cases['Upside']['room_revenue']:
        st.info('The edited revenues do not follow downside ≤ base ≤ upside. Case labels do not force an ordering; review the assumptions.')
    outputs=results[['Hypothetical case','available_room_nights','sold_room_nights','room_revenue','revpar']].rename(columns={'available_room_nights':'Available room-nights','sold_room_nights':'Expected sold room-nights','room_revenue':'Room revenue (USD)','revpar':'RevPAR (USD)'})
    st.dataframe(outputs.style.format({'Available room-nights':'{:,.0f}','Expected sold room-nights':'{:,.2f}','Room revenue (USD)':'{:,.2f}','RevPAR (USD)':'{:,.2f}'}),hide_index=True,width='stretch')
    fig=px.bar(results,x='Hypothetical case',y='room_revenue',color_discrete_sequence=['#087f8c'],labels={'room_revenue':'Hypothetical room revenue (USD, before costs)'})
    fig.update_layout(title='Hypothetical revenue over each case’s assumed operating days',paper_bgcolor='#faf7ef',plot_bgcolor='#faf7ef',font_color='#142b43')
    st.plotly_chart(fig,width='stretch')
    st.markdown('**Formulas:** available room-nights = rooms × days; sold room-nights = available × occupancy / 100; room revenue = sold × ADR; RevPAR = ADR × occupancy / 100.')
    st.caption('Expected sold room-nights may be fractional. Occupancy is entered as a percentage. If rooms or days differ, revenue changes reflect capacity or horizon too. No price-demand response, seasonality, taxes or costs are modeled. RevPAR remains the rate/occupancy assumption even when assumed capacity is zero.')
    st.download_button('Download hypothetical scenarios CSV',results.to_csv(index=False),'hypothetical_scenarios.csv','text/csv')

elif page=='Market brief':
    st.subheader('Public evidence brief')
    st.caption('Python templates · not AI-generated · evidence availability, not historical market findings')
    include=st.checkbox('Include my hypothetical revenue scenarios',value=False)
    cases=st.session_state.get('revenue_cases') if include else None
    if include and not cases: st.info('Set assumptions in Scenario explorer first. No scenarios have been inserted.')
    brief=public_brief(sources,cases)
    st.download_button('Download public evidence brief',brief,'public_evidence_brief.md','text/markdown')
    st.markdown(brief)

else:
    st.subheader('Sources & data quality')
    st.info('Source metadata only. Historical numerical observations, derived market briefs, screenshots and publisher media are excluded pending reuse clearance.')
    for source in sources.values():
        with st.expander(f"{source['publisher']} · {source['title']}"):
            st.markdown(source_link(source))
            for key in ['publication_date','reporting_periods','retrieved_on','geography','locator','upstream','access','reuse','public_disposition']:
                st.markdown(f"**{key.replace('_',' ').capitalize()}:** {source[key]}")
            st.markdown(f"[Policy / terms reference]({source['terms_url']})")
    st.download_button('Download source register (metadata only)',json.dumps(list(sources.values()),indent=2),'source_register.json','application/json')
    st.markdown((ROOT/'docs/DATA_REUSE.md').read_text())

st.divider()
st.caption('Public portfolio edition · Guided data assistant · No API key required · No investment recommendation')
