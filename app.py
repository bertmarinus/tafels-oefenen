"""
Tafels Oefenprogramma - Streamlit versie voor Base44
Een adaptief programma om tafels te oefenen voor basisschoolkinderen
"""

import streamlit as st
import random
import json
from datetime import datetime

# Pagina configuratie
st.set_page_config(
    page_title="Tafels Oefenen 🎯",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS voor kleurrijk design
st.markdown("""
    <style>
    .main {
        background-color: #FFE5B4;
    }
    .stButton>button {
        width: 100%;
        height: 80px;
        font-size: 28px;
        font-weight: bold;
        border-radius: 15px;
        margin: 10px 0;
    }
    .tafel-button {
        display: inline-block;
        margin: 5px;
    }
    div[data-testid="stNumberInput"] input {
        font-size: 60px !important;
        text-align: center;
        height: 100px;
    }
    .big-font {
        font-size: 60px !important;
        font-weight: bold;
        text-align: center;
        color: #2C3E50;
    }
    .feedback-good {
        font-size: 48px;
        font-weight: bold;
        color: #27AE60;
        text-align: center;
        padding: 20px;
        background-color: #D5F4E6;
        border-radius: 15px;
    }
    .feedback-bad {
        font-size: 48px;
        font-weight: bold;
        color: #E74C3C;
        text-align: center;
        padding: 20px;
        background-color: #FADBD8;
        border-radius: 15px;
    }
    .stats-box {
        font-size: 24px;
        padding: 20px;
        background-color: white;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
    }
    h1 {
        text-align: center;
        color: #FF6B6B;
    }
    h2 {
        text-align: center;
        color: #4ECDC4;
    }
    h3 {
        text-align: center;
        color: #2C3E50;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialiseer session state
if 'fase' not in st.session_state:
    st.session_state.fase = 'start'  # start, oefenen, einde

if 'geselecteerde_tafels' not in st.session_state:
    st.session_state.geselecteerde_tafels = []

if 'alle_sommen' not in st.session_state:
    st.session_state.alle_sommen = []

if 'moeilijke_sommen' not in st.session_state:
    st.session_state.moeilijke_sommen = {}

if 'geleerde_sommen' not in st.session_state:
    st.session_state.geleerde_sommen = {}

if 'huidige_som' not in st.session_state:
    st.session_state.huidige_som = None

if 'sommen_sinds_moeilijk' not in st.session_state:
    st.session_state.sommen_sinds_moeilijk = 0

if 'stats' not in st.session_state:
    st.session_state.stats = {
        'huidig_goed': 0,
        'huidig_fout': 0,
        'totaal_goed': 0,
        'totaal_fout': 0
    }

if 'feedback' not in st.session_state:
    st.session_state.feedback = None

if 'wacht_op_volgende' not in st.session_state:
    st.session_state.wacht_op_volgende = False

if 'som_counter' not in st.session_state:
    st.session_state.som_counter = 0


def laad_statistieken():
    """Laad totaal statistieken"""
    try:
        with open('stats.json', 'r') as f:
            data = json.load(f)
            st.session_state.stats['totaal_goed'] = data.get('totaal_goed', 0)
            st.session_state.stats['totaal_fout'] = data.get('totaal_fout', 0)
    except:
        pass


def sla_statistieken_op():
    """Sla totaal statistieken op"""
    with open('stats.json', 'w') as f:
        json.dump({
            'totaal_goed': st.session_state.stats['totaal_goed'],
            'totaal_fout': st.session_state.stats['totaal_fout']
        }, f)


def initialiseer_sommen():
    """Maak lijst van alle sommen voor geselecteerde tafels"""
    st.session_state.alle_sommen = []
    for tafel in st.session_state.geselecteerde_tafels:
        for i in range(1, 11):  # 1 t/m 10 (was 13 voor 1 t/m 12)
            st.session_state.alle_sommen.append((i, tafel))
    
    random.shuffle(st.session_state.alle_sommen)
    
    # Reset voor nieuwe sessie
    st.session_state.stats['huidig_goed'] = 0
    st.session_state.stats['huidig_fout'] = 0
    st.session_state.moeilijke_sommen = {}
    st.session_state.geleerde_sommen = {}
    st.session_state.sommen_sinds_moeilijk = 0
    st.session_state.feedback = None
    st.session_state.wacht_op_volgende = False


def get_volgende_som():
    """Kies de volgende som volgens het adaptieve algoritme"""
    # Check of we een moeilijke som moeten herhalen
    if st.session_state.moeilijke_sommen and st.session_state.sommen_sinds_moeilijk >= random.randint(2, 3):
        moeilijke_som_strings = list(st.session_state.moeilijke_sommen.keys())
        som_string = random.choice(moeilijke_som_strings)
        a, b = map(int, som_string.split('x'))
        st.session_state.sommen_sinds_moeilijk = 0
        return (a, b)
    
    # Anders een gewone som
    if st.session_state.alle_sommen:
        som = st.session_state.alle_sommen.pop(0)
        st.session_state.sommen_sinds_moeilijk += 1
        return som
    else:
        # Check of er nog moeilijke sommen zijn
        if st.session_state.moeilijke_sommen:
            moeilijke_som_strings = list(st.session_state.moeilijke_sommen.keys())
            som_string = random.choice(moeilijke_som_strings)
            a, b = map(int, som_string.split('x'))
            return (a, b)
        else:
            return None


def controleer_antwoord(antwoord_input):
    """Controleer het ingevoerde antwoord"""
    if not antwoord_input:
        st.warning("⚠️ Voer eerst een antwoord in!")
        return
    
    try:
        antwoord = int(antwoord_input)
        a, b = st.session_state.huidige_som
        correct_antwoord = a * b
        som_string = f"{a}x{b}"
        
        if antwoord == correct_antwoord:
            # Goed!
            st.session_state.stats['huidig_goed'] += 1
            st.session_state.stats['totaal_goed'] += 1
            st.session_state.feedback = ('good', 'Goed! 🎉')
            
            # Check of deze som moeilijk was
            if som_string in st.session_state.moeilijke_sommen:
                if som_string not in st.session_state.geleerde_sommen:
                    st.session_state.geleerde_sommen[som_string] = 0
                st.session_state.geleerde_sommen[som_string] += 1
                
                # 3x achter elkaar goed = geleerd
                if st.session_state.geleerde_sommen[som_string] >= 3:
                    del st.session_state.moeilijke_sommen[som_string]
                    del st.session_state.geleerde_sommen[som_string]
            else:
                if som_string in st.session_state.geleerde_sommen:
                    del st.session_state.geleerde_sommen[som_string]
        else:
            # Fout!
            st.session_state.stats['huidig_fout'] += 1
            st.session_state.stats['totaal_fout'] += 1
            st.session_state.feedback = ('bad', f'Fout! 😞<br>Het goede antwoord is {correct_antwoord}')
            
            # Voeg toe aan moeilijke sommen
            if som_string not in st.session_state.moeilijke_sommen:
                st.session_state.moeilijke_sommen[som_string] = 0
            st.session_state.moeilijke_sommen[som_string] += 1
            
            # Reset geleerd teller
            if som_string in st.session_state.geleerde_sommen:
                st.session_state.geleerde_sommen[som_string] = 0
        
        st.session_state.wacht_op_volgende = True
        sla_statistieken_op()
        
    except ValueError:
        st.warning("⚠️ Voer een geldig getal in!")


def volgende_som_actie():
    """Ga naar de volgende som"""
    st.session_state.feedback = None
    st.session_state.wacht_op_volgende = False
    st.session_state.som_counter += 1  # Verhoog counter voor nieuwe input key
    
    som = get_volgende_som()
    if som is None:
        # Alles geleerd!
        st.session_state.fase = 'einde'
        st.session_state.volledig_geleerd = True
    else:
        st.session_state.huidige_som = som


# START SCHERM
if st.session_state.fase == 'start':
    laad_statistieken()
    
    # Initialiseer geselecteerde tafels lijst
    if 'temp_geselecteerde_tafels' not in st.session_state:
        st.session_state.temp_geselecteerde_tafels = []
    
    st.markdown("# 🎯 Tafels Oefenen 🎯")
    st.markdown("---")
    
    st.markdown("### Welke tafels wil je oefenen?")
    st.markdown("*Klik op de tafels die je wilt oefenen*")
    st.markdown("")
    
    # Maak 3 rijen van 4 knoppen
    for row in range(3):
        cols = st.columns(4)
        for col_idx, col in enumerate(cols):
            tafel_num = row * 4 + col_idx + 1
            with col:
                # Check of deze tafel al geselecteerd is
                is_selected = tafel_num in st.session_state.temp_geselecteerde_tafels
                button_label = f"{'✓ ' if is_selected else ''}Tafel {tafel_num}"
                
                if st.button(button_label, key=f"tafel_{tafel_num}", 
                           type="primary" if is_selected else "secondary"):
                    # Toggle selectie
                    if tafel_num in st.session_state.temp_geselecteerde_tafels:
                        st.session_state.temp_geselecteerde_tafels.remove(tafel_num)
                    else:
                        st.session_state.temp_geselecteerde_tafels.append(tafel_num)
                    st.rerun()
    
    st.markdown("---")
    
    # Toon geselecteerde tafels
    if st.session_state.temp_geselecteerde_tafels:
        st.markdown(f"**Geselecteerd:** {', '.join(map(str, sorted(st.session_state.temp_geselecteerde_tafels)))}")
    else:
        st.markdown("*Geen tafels geselecteerd*")
    
    st.markdown("")
    
    if st.button("🚀 Start Oefenen!", type="primary", disabled=len(st.session_state.temp_geselecteerde_tafels) == 0):
        st.session_state.geselecteerde_tafels = st.session_state.temp_geselecteerde_tafels.copy()
        initialiseer_sommen()
        st.session_state.huidige_som = get_volgende_som()
        st.session_state.fase = 'oefenen'
        st.rerun()
    
    st.markdown("---")
    st.markdown("##### 📊 Je totale statistieken:")
    totaal = st.session_state.stats['totaal_goed'] + st.session_state.stats['totaal_fout']
    if totaal > 0:
        percentage = round((st.session_state.stats['totaal_goed'] / totaal) * 100)
        st.markdown(f"<div class='stats-box'>✓ {st.session_state.stats['totaal_goed']} goed  ✗ {st.session_state.stats['totaal_fout']} fout  ({percentage}%)</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='stats-box'>Nog geen sommen gemaakt</div>", unsafe_allow_html=True)


# OEFEN SCHERM
elif st.session_state.fase == 'oefenen':
    st.markdown("# 🎯 Tafels Oefenen")
    
    # Statistieken
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='stats-box' style='background-color: #D5F4E6;'>✓ Goed: {st.session_state.stats['huidig_goed']}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stats-box' style='background-color: #FADBD8;'>✗ Fout: {st.session_state.stats['huidig_fout']}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Som
    if st.session_state.huidige_som:
        a, b = st.session_state.huidige_som
        st.markdown(f"<p class='big-font'>{a} × {b} = ?</p>", unsafe_allow_html=True)
    
    st.markdown("")
    
    # Feedback tonen als er is
    if st.session_state.feedback:
        feedback_type, feedback_text = st.session_state.feedback
        if feedback_type == 'good':
            st.markdown(f"<div class='feedback-good'>{feedback_text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='feedback-bad'>{feedback_text}</div>", unsafe_allow_html=True)
        
        st.markdown("")
        
        # Form voor Enter ondersteuning bij Volgende
        with st.form(key=f"volgende_form_{st.session_state.get('som_counter', 0)}"):
            submitted = st.form_submit_button("➡️ Volgende Som (druk Enter)", type="primary", use_container_width=True)
            if submitted:
                volgende_som_actie()
                st.rerun()
        
        # JavaScript voor auto-focus op form
        st.markdown("""
            <script>
            setTimeout(function() {
                const buttons = window.parent.document.querySelectorAll('button[kind="formSubmit"]');
                if (buttons.length > 0) {
                    buttons[buttons.length - 1].focus();
                }
            }, 100);
            </script>
        """, unsafe_allow_html=True)
    else:
        # Antwoord invoer met number_input voor Enter support
        # Maak form voor Enter ondersteuning
        with st.form(key=f"antwoord_form_{st.session_state.get('som_counter', 0)}", clear_on_submit=True):
            antwoord = st.number_input(
                "Jouw antwoord:",
                min_value=0,
                max_value=999,
                value=None,
                step=1,
                placeholder="Type je antwoord...",
                label_visibility="collapsed",
                key=f"num_input_{st.session_state.get('som_counter', 0)}"
            )
            
            # Submit button (wordt getriggerd bij Enter)
            submitted = st.form_submit_button("✅ Controleer", type="primary", use_container_width=True)
            
            if submitted and antwoord is not None:
                controleer_antwoord(str(int(antwoord)))
                st.rerun()
        
        # Stop knop buiten de form
        if st.button("⏹ Stop", key="stop_btn", use_container_width=True):
            st.session_state.fase = 'einde'
            st.session_state.volledig_geleerd = False
            st.rerun()
        
        # JavaScript voor auto-focus
        st.markdown("""
            <script>
            setTimeout(function() {
                const inputs = window.parent.document.querySelectorAll('input[type="number"]');
                if (inputs.length > 0) {
                    const lastInput = inputs[inputs.length - 1];
                    lastInput.focus();
                    lastInput.select();
                }
            }, 100);
            </script>
        """, unsafe_allow_html=True)


# EIND SCHERM
elif st.session_state.fase == 'einde':
    if st.session_state.get('volledig_geleerd', False):
        st.markdown("# 🏆 Gefeliciteerd! 🏆")
        st.markdown("### Je beheerst alle sommen!")
    else:
        st.markdown("# 📊 Samenvatting 📊")
        st.markdown("### Goed gedaan!")
    
    st.markdown("---")
    
    # Statistieken deze sessie
    st.markdown("#### Deze sessie:")
    totaal_huidig = st.session_state.stats['huidig_goed'] + st.session_state.stats['huidig_fout']
    if totaal_huidig > 0:
        percentage_huidig = round((st.session_state.stats['huidig_goed'] / totaal_huidig) * 100)
    else:
        percentage_huidig = 0
    
    st.markdown(f"<div class='stats-box'>✓ {st.session_state.stats['huidig_goed']} goed  ✗ {st.session_state.stats['huidig_fout']} fout  ({percentage_huidig}%)</div>", unsafe_allow_html=True)
    
    # Statistieken totaal
    st.markdown("#### Totaal alle sessies:")
    totaal_alles = st.session_state.stats['totaal_goed'] + st.session_state.stats['totaal_fout']
    if totaal_alles > 0:
        percentage_totaal = round((st.session_state.stats['totaal_goed'] / totaal_alles) * 100)
    else:
        percentage_totaal = 0
    
    st.markdown(f"<div class='stats-box'>✓ {st.session_state.stats['totaal_goed']} goed  ✗ {st.session_state.stats['totaal_fout']} fout  ({percentage_totaal}%)</div>", unsafe_allow_html=True)
    
    # Moeilijke sommen
    if st.session_state.moeilijke_sommen and not st.session_state.get('volledig_geleerd', False):
        st.markdown("---")
        st.markdown("#### ⚠️ Deze sommen vond je lastig:")
        for som_string in st.session_state.moeilijke_sommen.keys():
            a, b = map(int, som_string.split('x'))
            antwoord = a * b
            st.markdown(f"<div class='stats-box' style='background-color: #FADBD8;'>{a} × {b} = {antwoord}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Knoppen
    col1, col2 = st.columns(2)
    
    if st.session_state.get('volledig_geleerd', False):
        with col1:
            if st.button("🔄 Nog een keer!", type="primary"):
                initialiseer_sommen()
                st.session_state.huidige_som = get_volgende_som()
                st.session_state.fase = 'oefenen'
                st.rerun()
    
    with col2:
        if st.button("🏠 Terug naar start"):
            st.session_state.fase = 'start'
            st.rerun()
