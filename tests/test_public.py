"""Only hypothetical inputs; no fixtures from withheld historical datasets."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from public_core import QUESTIONS, load_metadata, guided_answer, revenue_scenario, public_brief
from scripts.check_release import check

ROOT=Path(__file__).resolve().parents[1]


def test_hypothetical_revenue_and_decimal_occupancy():
    r=revenue_scenario(5,20,40,120)
    assert r['available_room_nights']==100
    assert r['sold_room_nights']==40
    assert r['room_revenue']==4800
    assert r['revpar']==48
    assert revenue_scenario(1,1,25,120)['sold_room_nights']==0.25
    assert revenue_scenario(1,1,100,120)['room_revenue']==120
    for rooms,days,occ,adr in [(0,20,40,120),(5,0,40,120),(5,20,0,120),(5,20,40,0)]:
        assert revenue_scenario(rooms,days,occ,adr)['room_revenue']==0


@pytest.mark.parametrize('args',[(1.5,1,50,100),(1,-1,50,100),(1,1,101,100),(1,1,-1,100),(1,1,50,-1),(1,1,float('nan'),100),(float('inf'),1,50,100)])
def test_invalid_scenario_inputs(args):
    with pytest.raises(ValueError): revenue_scenario(*args)


def test_manifest_excludes_observations_and_all_guided_presets_work():
    sources,manifest=load_metadata()
    assert manifest['edition']=='public'
    assert not manifest['observations_included']
    assert not manifest['historical_numeric_claims_enabled']
    assert manifest['approved_observation_files']==[]
    for question in QUESTIONS:
        assert guided_answer(question,sources)
    for question in QUESTIONS[:3]:
        answer=guided_answer(question,sources)
        assert 'No historical' in answer and 'https://' in answer and 'permission' in answer
    with pytest.raises(ValueError): guided_answer('Invent a market forecast',sources)
    assert not list((ROOT/'data').glob('*.csv'))


def test_brief_never_masquerades_as_numerical_market_findings():
    sources,_=load_metadata()
    brief=public_brief(sources)
    assert 'not a numerical assessment' in brief
    assert 'No scenario assumptions selected' in brief
    assert 'historical charts and derived market findings are excluded' in brief
    scenario=public_brief(sources,{'Base':dict(rooms=5,operating_days=20,occupancy=40,adr=120)})
    assert '4,800.00' in scenario and 'not profit' in scenario
    assert '|\n\n|' not in scenario
    assert 'no historical reporting dates' in scenario


def test_public_app_all_pages_and_presets_without_secrets(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    monkeypatch.delenv('OPENAI_MODEL',raising=False)
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    assert app.sidebar.radio[0].options == ['Scenario Explorer', 'Guided Analysis', 'Market Brief & Sources']
    assert app.sidebar.radio[0].value == 'Scenario Explorer'
    assert app.metric[2].value == '$8,760,000.00'
    assert not app.chat_input
    for page in list(app.sidebar.radio[0].options):
        app.sidebar.radio[0].set_value(page).run(timeout=30)
        assert not app.exception and not app.chat_input
        if page=='Guided Analysis':
            for question in QUESTIONS:
                app.selectbox[0].set_value(question).run()
                assert not app.exception
                if question==QUESTIONS[3]:
                    app.slider[1].set_value(100.0).run()
                    assert app.metric[1].value=='$300.00'
        if page=='Scenario Explorer':
            app.number_input(key='Base_rooms').set_value(5).run()
            app.number_input(key='Base_days').set_value(20).run()
            app.slider(key='Base_occupancy').set_value(40.0).run()
            app.number_input(key='Base_adr').set_value(120.0).run()
            assert app.metric[2].value=='$4,800.00'
            assert app.metric[3].value=='$48.00'
        if page=='Market Brief & Sources':
            assert {button.label for button in app.get('download_button')} == {
                'Download public evidence brief', 'Download source register (metadata only)'
            }
            assert any('Historical numerical observations are withheld' in note.value for note in app.info)
            app.checkbox[0].set_value(True).run()
            assert not app.exception
            assert any('4,800.00' in m.value for m in app.markdown)


def test_public_app_does_not_enable_ai_if_key_present(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','placeholder-not-a-credential')
    app=AppTest.from_file(str(ROOT/'app.py')).run(timeout=30)
    assert not app.exception
    assert 'Optional AI chat' not in app.sidebar.radio[0].options
    assert not app.chat_input


def test_release_allowlist_and_secret_scan():
    included=check()
    assert 'app.py' in included
    assert 'data/observations.csv' not in included
    assert not any(name.endswith(('.png','.pdf','.csv')) for name in included)
    assert all('..' not in name for name in included)
