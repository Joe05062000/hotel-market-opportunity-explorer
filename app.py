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
    sources,_=load_metadata()
except (ValueError, OSError, KeyError, json.JSONDecodeError):
    st.error('Public-release metadata could not be validated. No historical results will be displayed.')
    st.stop()

with st.sidebar:
    st.markdown('## ◈ HOTEL MARKET')
    st.caption('NYC · PUBLIC PORTFOLIO EDITION')
    page=st.radio('Explore',['Scenario Explorer','Guided Analysis','Market Brief & Sources'])
    st.caption('No API key required')

st.markdown('<div class="eyebrow">NYC / HOSPITALITY STRATEGY</div>',unsafe_allow_html=True)
st.title('Hotel Market Opportunity Explorer')

if page=='Guided Analysis':
    st.subheader('Guided Analysis')
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

elif page=='Scenario Explorer':
    st.subheader('Scenario Explorer')
    st.markdown('Test how room rates and occupancy affect hotel room revenue.')
    st.caption('Hypothetical assumptions only. Room revenue excludes costs and is not profit.')
    cases={}
    saved=st.session_state.get('revenue_cases',{})
    for column,(name,initial) in zip(st.columns(3),DEFAULT_CASES.items()):
        default=saved.get(name,initial)
        with column:
            st.markdown(f'**{name} · hypothetical**')
            capacity,horizon=st.columns(2)
            rooms=capacity.number_input(f'{name} room count',min_value=0,max_value=100000,value=default['rooms'],step=1,key=f'{name}_rooms')
            days=horizon.number_input(f'{name} operating days',min_value=0,max_value=3660,value=default['operating_days'],step=1,key=f'{name}_days')
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

else:
    st.subheader('Market Brief & Sources')
    st.caption('Python templates · not AI-generated · evidence availability, not historical market findings')
    include=st.checkbox('Include my hypothetical revenue scenarios',value=False)
    cases=st.session_state.get('revenue_cases') if include else None
    if include and not cases: st.info('Set assumptions in Scenario Explorer first. No scenarios have been inserted.')
    brief=public_brief(sources,cases)
    st.download_button('Download public evidence brief',brief,'public_evidence_brief.md','text/markdown')
    with st.expander('Preview the evidence brief'):
        st.markdown(brief)
    st.markdown('### Historical data coverage')
    st.info('Historical numerical observations are withheld pending reuse clearance. This release includes source references and reporting periods, with no historical KPIs, trends or borough rankings.')
    st.markdown('The May 2023 borough source covers Manhattan, Brooklyn and Queens. The Bronx and Staten Island are absent from the selected table. Comparable hotel classes and sample sizes are not established.')
    st.markdown('### Research references')
    for source in sources.values():
        with st.expander(f"{source['publisher']} · {source['title']}"):
            st.markdown(source_link(source))
            for key in ['publication_date','reporting_periods','retrieved_on','geography','locator','upstream','access','reuse','public_disposition']:
                st.markdown(f"**{key.replace('_',' ').capitalize()}:** {source[key]}")
            st.markdown(f"[Policy / terms reference]({source['terms_url']})")
    st.download_button('Download source register (metadata only)',json.dumps(list(sources.values()),indent=2),'source_register.json','application/json')
    with st.expander('Data reuse and metric definitions'):
        for name,definition in DEFINITIONS.items():
            st.markdown(f'**{name}:** {definition}')
        st.markdown((ROOT/'docs/DATA_REUSE.md').read_text())

st.divider()
st.caption('Public portfolio edition · Guided data assistant · No API key required · No investment recommendation')
