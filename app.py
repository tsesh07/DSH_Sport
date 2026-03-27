import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import datetime


# DASHBOARD SETUP
st.set_page_config(page_title="Sport Data Dashboard", page_icon="🚴‍♂️", layout="wide")

st.title("🚴‍♂️ Docenten vs. De Rest van de Wereld")
st.markdown("Welkom bij het officiële Hackathon Dashboard. Hoe ontwikkelen onze docenten zich?")

with st.expander("ℹ️ Over de Referentie Dataset (Fister Atleten)"):
    st.markdown("""
    Om de prestaties van onze docenten in het juiste perspectief te plaatsen, hebben we dit dashboard verrijkt met open-source data van drie externe sporters uit de gerenommeerde *Fister dataset*:
    
    * 🚴‍♂️ **Amateur 6 (Athlete 6):** Man, 41 jaar. Een actieve amateurwielrenner.
    * 🚴‍♂️ **Amateur 7 (Athlete 7):** Man, 22 jaar. Een jonge, fanatieke amateurwielrenner.
    * ⭐ **Pro Wielrenner (Athlete 8):** Man, 19 jaar. Een professioneel wielrenner op topniveau.
    
    Aantal ritten per sporter:
   * PRO WIELRENNER:     322
   * Robin:              318
   * Amateur 7:          308
   * Amateur 6:          52
   * Jan:                51
   * Pieter:             33
    """)

# 2. DATA INLADEN
@st.cache_data 
def load_data():
    df = pd.read_csv('masterfile_alle_docenten_referentie.csv', sep=';')
    df['Datum'] = pd.to_datetime(df['Datum'])
    return df

df = load_data()

# 3. ZIJBALK (FILTERS & CREDITS)
st.sidebar.header("Filter de Data")
geselecteerde_docenten = st.sidebar.multiselect(
    "Kies Sporters:",
    options=df['Docent'].unique(),
    default=df['Docent'].unique() # Standaard iedereen geselecteerd
)

st.sidebar.divider() 
st.sidebar.markdown("### Gemaakt door:")
st.sidebar.markdown("**Groep 4**") 
st.sidebar.write("• Sai-Hong Tse")
st.sidebar.write("• Micha Bakker")
st.sidebar.write("• Stijn Kooistra")
st.sidebar.write("• Juri van der Ster")
st.sidebar.caption("Hackathon 2026 - Data Science")

df_filtered = df[df['Docent'].isin(geselecteerde_docenten)]

# 4. KPI's
st.subheader("🏆 Algemene Statistieken")
col1, col2, col3 = st.columns(3)

with col1:
    totale_afstand = df_filtered['Afstand_km'].sum()
    st.metric("Totale Afstand Gefietst", f"{totale_afstand:,.0f} km")
with col2:
    gem_snelheid = df_filtered['Gem_Snelheid_kmu'].mean()
    st.metric("Gemiddelde Snelheid", f"{gem_snelheid:.1f} km/u")
with col3:
    aantal_ritten = len(df_filtered)
    st.metric("Aantal Ritten", f"{aantal_ritten}")
    

# 5. TABBLADEN
st.divider()

tab6, tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Route Kaart","📈 Snelheid & Volume", "🫀 Fysieke Efficiëntie", "🏆 Leaderboard & Gedrag", "🤖 Prestatie Voorspellingen", "📈 Conditiegroei"])

# TAB 1: Snelheid & Kilometervreters
with tab1:
    col_links, col_rechts = st.columns(2)
    
    # 1. Splits de data op in twee groepen (Docenten vs. Referentie)
    df_sorted = df_filtered.sort_values('Datum').copy()
    docenten_namen = ['Jan', 'Pieter', 'Robin']
    
    df_docenten = df_sorted[df_sorted['Docent'].isin(docenten_namen)].copy()
    df_referentie = df_sorted[~df_sorted['Docent'].isin(docenten_namen)].copy()
    
    # 2. Bereken de rolling average & cumulatieve afstand per groep apart
    if not df_docenten.empty:
        df_docenten['Snelheid_Trend'] = df_docenten.groupby('Docent')['Gem_Snelheid_kmu'].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
        df_docenten['Cumulatieve_Afstand'] = df_docenten.groupby('Docent')['Afstand_km'].cumsum()
        
    if not df_referentie.empty:
        df_referentie['Snelheid_Trend'] = df_referentie.groupby('Docent')['Gem_Snelheid_kmu'].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
        df_referentie['Cumulatieve_Afstand'] = df_referentie.groupby('Docent')['Afstand_km'].cumsum()

    # LINKER KOLOM: SNELHEID

    with col_links:
        st.markdown("### 🚀 Snelheidsontwikkeling (Trend)")
        st.write("Gemiddelde van de laatste 5 ritten voor een strakke trendlijn.")
        
        if not df_docenten.empty:
            st.markdown("##### 🚴‍♂️ Onze Docenten (2021 - 2026)")
            fig_prog_doc = px.line(df_docenten, x='Datum', y='Snelheid_Trend', color='Docent', render_mode='svg')
            fig_prog_doc.update_traces(line=dict(width=3), line_shape='spline')
            st.plotly_chart(fig_prog_doc, use_container_width=True)
            
        if not df_referentie.empty:
            st.markdown("##### ⏱️ Referentie Atleten (2013 - 2017)")
            fig_prog_ref = px.line(df_referentie, x='Datum', y='Snelheid_Trend', color='Docent', render_mode='svg')
            # Bij de pro/amateurs maken we de lijnen ook mooi vloeiend
            fig_prog_ref.update_traces(line=dict(width=3, dash='dot'), line_shape='spline') 
            st.plotly_chart(fig_prog_ref, use_container_width=True)

    # RECHTER KOLOM: CUMULATIEF

    with col_rechts:
        st.markdown("### 🌍 Cumulatieve Kilometers")
        st.write("De Race: Wie heeft in zijn actieve periode het meeste gefietst?")
        
        if not df_docenten.empty:
            st.markdown("##### 🚴‍♂️ Onze Docenten (2021 - 2026)")
            fig_cum_doc = px.line(df_docenten, x='Datum', y='Cumulatieve_Afstand', color='Docent')
            fig_cum_doc.update_traces(line=dict(width=3), line_shape='hv')
            st.plotly_chart(fig_cum_doc, use_container_width=True)
            
        if not df_referentie.empty:
            st.markdown("##### ⏱️ Referentie Atleten (2013 - 2017)")
            fig_cum_ref = px.line(df_referentie, x='Datum', y='Cumulatieve_Afstand', color='Docent')
            fig_cum_ref.update_traces(line=dict(width=3, dash='dot'), line_shape='hv')
            st.plotly_chart(fig_cum_ref, use_container_width=True)

# TAB 2: De "Motor" (Efficiëntie)
with tab2:
    st.markdown("### 🫀 Snelheid vs. Hartslag")
    st.info("Let op: Niet elke rit heeft hartslagdata. We laten hier alleen de ritten met een hartslagband zien.")
    
    df_hartslag = df_filtered.dropna(subset=['Gem_Hartslag'])
    
    if not df_hartslag.empty:
        fig_motor = px.scatter(
            df_hartslag, x='Gem_Snelheid_kmu', y='Gem_Hartslag', color='Docent', 
            size='Afstand_km', hover_data=['Datum'],
            title="Efficiëntie: Lagere hartslag bij hogere snelheid is beter!",
            render_mode='svg'
        )
        st.plotly_chart(fig_motor, use_container_width=True)
    else:
        st.warning("Geen hartslagdata gevonden voor de geselecteerde sporters.")

# TAB 3: Gedrag & Hall of Fame
with tab3:
    col_links, col_rechts = st.columns(2)
    
    with col_links:
        st.markdown("### 📅 Welke dag wordt er gefietst?")
        df_dagen = df_filtered.copy()
        df_dagen['Dag_Nummer'] = df_dagen['Datum'].dt.dayofweek
        dagen_dict = {0:'Ma', 1:'Di', 2:'Wo', 3:'Do', 4:'Vr', 5:'Za', 6:'Zo'}
        df_dagen['Dag_Naam'] = df_dagen['Dag_Nummer'].map(dagen_dict)
        
        ritten_per_dag = df_dagen.groupby(['Docent', 'Dag_Naam', 'Dag_Nummer']).size().reset_index(name='Aantal')
        ritten_per_dag = ritten_per_dag.sort_values('Dag_Nummer')
        
        fig_dagen = px.bar(
            ritten_per_dag, x='Dag_Naam', y='Aantal', color='Docent', barmode='group',
            title="Trainingsdagen (Zondagsfietsers of elke dag?)"
        )
        st.plotly_chart(fig_dagen, use_container_width=True)
        
    with col_rechts:
        st.markdown("### 🏆 Hall of Fame (Persoonlijke Records)")
        records = df_filtered.groupby('Docent').agg(
            Max_Afstand_km=('Afstand_km', 'max'),
            Max_Snelheid_kmu=('Gem_Snelheid_kmu', 'max'),
            Max_Vermogen_Watt=('Gem_Vermogen_Watt', 'max')
        ).reset_index()
        
        records['Max_Afstand_km'] = records['Max_Afstand_km'].round(1)
        records['Max_Snelheid_kmu'] = records['Max_Snelheid_kmu'].round(1)
        records['Max_Vermogen_Watt'] = records['Max_Vermogen_Watt'].fillna(0).round(0).astype(int)
        
        st.dataframe(records, use_container_width=True, hide_index=True)
        
# ------------------------------------------
# TAB 4: AI Voorspellingen (Random Forest)
# ------------------------------------------
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go

with tab4:
    st.markdown("### Toekomstige sportprestaties")
    st.write("Pas de sliders aan om een toekomstige sportprestatie te voorspellen op basis van Machine Learning.")

    # 1. Data voorbereiden voor het model (gebaseerd op je actieve filters!)
    df_ml = df_filtered.copy()
    
    # We voegen de maand toe als extra variabele
    df_ml['Maand'] = pd.to_datetime(df_ml['Datum']).dt.month
    
    # Vul lege hartslagen in met het gemiddelde van die specifieke docent
    df_ml['Gem_Hartslag'] = df_ml.groupby('Docent')['Gem_Hartslag'].transform(lambda x: x.fillna(x.mean()))
    df_ml = df_ml.dropna(subset=['Gem_Hartslag', 'Gem_Snelheid_kmu'])

    if not df_ml.empty:
        # 2. MODEL TRAINING (Gecached zodat hij niet bij elke klik traag wordt)
        @st.cache_resource
        def train_rf_model(data):
            df_encoded = pd.get_dummies(data, columns=['Docent'], prefix='Coach')
            coach_cols = [c for c in df_encoded.columns if c.startswith('Coach_')]
            features = ['Afstand_km', 'Gem_Hartslag', 'Maand'] + coach_cols
            
            X = df_encoded[features]
            y = df_encoded['Gem_Snelheid_kmu']
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            return model, features

        model, feature_names = train_rf_model(df_ml)

        # 3. DASHBOARD LAYOUT (Precies zoals je groepsgenoot het had bedacht)
        col_ml_links, col_ml_rechts = st.columns([1, 3])

        with col_ml_links:
            st.subheader("⚙️ Instellingen")
            
            # Sliders en Selectbox
            naam = st.selectbox("Wie gaat er sporten?", df_ml['Docent'].unique())
            
            # Afstand slider gebaseerd op max uit de dataset
            afstand = st.slider("Afstand (km)", 
                                min_value=0.0, 
                                max_value=float(df_ml['Afstand_km'].max()), 
                                value=30.0)
            
            maand = st.slider("Maand van het jaar", 1, 12, 6)

            # Berekening voorbereiden
            input_row = pd.DataFrame(0, index=[0], columns=feature_names)
            input_row['Afstand_km'] = afstand
            input_row['Maand'] = maand
            
            # Pak de gemiddelde hartslag van deze sporter
            gem_hr = df_ml[df_ml['Docent'] == naam]['Gem_Hartslag'].mean()
            input_row['Gem_Hartslag'] = gem_hr
            
            # Zet het vinkje (de 1) bij de juiste docent in de onzichtbare wiskunde
            coach_col = f'Coach_{naam}'
            if coach_col in feature_names:
                input_row[coach_col] = 1
            
            # De voorspelling!
            snelheid_pred = model.predict(input_row)[0]
            
            st.write("---")
            st.metric(label="🎯 Voorspelde Snelheid", value=f"{snelheid_pred:.2f} km/u")
            st.caption(f"Gebaseerd op een geschatte hartslag van {gem_hr:.0f} bpm.")

        with col_ml_rechts:
            # Maak de Plotly grafiek
            subset = df_ml[df_ml['Docent'] == naam].sort_values('Datum')
            
            fig_rf = px.scatter(
                subset, x='Afstand_km', y='Gem_Snelheid_kmu', 
                title=f"Historische Prestaties vs. Voorspelling: {naam}",
                labels={'Gem_Snelheid_kmu': 'Snelheid (km/u)', 'Afstand_km': 'Afstand (km)'},
                opacity=0.6,
                render_mode='svg'
            )
            
            # Maak de bolletjes van de historie lekker dik
            fig_rf.update_traces(marker=dict(size=10, color='#636EFA'))

            # 🔥 DE RODE STER VAN JE GROEPSGENOOT 🔥
            fig_rf.add_trace(go.Scatter(
                x=[afstand], 
                y=[snelheid_pred],
                mode='markers+text',
                name='Voorspelling',
                text=["VOORSPELLING"],
                textposition="top center",
                marker=dict(color='Red', size=20, symbol='star', line=dict(width=2, color='white'))
            ))

            # Update layout voor een strakker uiterlijk in het dashboard
            fig_rf.update_layout(
                margin=dict(l=20, r=20, t=50, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            st.plotly_chart(fig_rf, use_container_width=True)

        # Tabel met ruwe data (Expander)
        with st.expander(f"Bekijk de volledige trainingsdata van {naam}"):
            st.dataframe(subset[['Datum', 'Afstand_km', 'Gem_Snelheid_kmu', 'Gem_Hartslag']], use_container_width=True)
            
    else:
        st.warning("⚠️ Er is niet genoeg data beschikbaar om het model te trainen. Controleer de filters in de zijbalk.")

# TAB 5: Conditiegroei (Lineaire Regressie)
from sklearn.linear_model import LinearRegression
import plotly.colors as pc

with tab5:
    st.markdown("### 🫀📈 Conditiegroei: Is er nog groei mogelijk?")
    st.write("We berekenen de **Efficiëntie-score** (Snelheid gedeeld door Hartslag). Een stijgende lijn betekent dat je harder fietst met minder moeite. Met een *Lineair Regressie Model* berekenen we het exacte groeipercentage over tijd!")

    # 1. Haal alle ritten zonder hartslag eruit
    df_conditie = df_filtered.dropna(subset=['Gem_Snelheid_kmu', 'Gem_Hartslag', 'Datum']).copy()

    if not df_conditie.empty:
        # BEREKEN DE EFFICIËNTIE (Hoe hoger, hoe beter)
        df_conditie['Efficientie'] = df_conditie['Gem_Snelheid_kmu'] / df_conditie['Gem_Hartslag']
        
        # Bereken dagen sinds eerste rit (voor de X-as van het wiskundige model)
        datum_min = df_conditie['Datum'].min()
        df_conditie['Dagen'] = (pd.to_datetime(df_conditie['Datum']) - pd.to_datetime(datum_min)).dt.days

        st.markdown("#### 🏆 Groeipercentage per Sporter:")
        
        # Maak dynamische kolommen voor de statistieken
        docenten_met_hartslag = df_conditie['Docent'].unique()
        kolommen = st.columns(len(docenten_met_hartslag))
        
        # 🔥 DE FIX: Maak een vast kleurenpalet aan voor deze sporters!
        standaard_kleuren = pc.qualitative.Plotly # Plotly's standaard mooie kleuren
        kleuren_map = {docent: standaard_kleuren[i % len(standaard_kleuren)] for i, docent in enumerate(docenten_met_hartslag)}

        # Basis grafiek met de losse puntjes (nu geforceerd met onze kleuren_map)
        fig_reg = px.scatter(
            df_conditie, x='Datum', y='Efficientie', color='Docent', 
            color_discrete_map=kleuren_map, # <-- Gebruik het vaste palet
            hover_data=['Gem_Snelheid_kmu', 'Gem_Hartslag'],
            title="Cardiovasculaire Ontwikkeling over Tijd",
            render_mode='svg'
        )
        
        fig_reg.update_traces(marker=dict(size=17, opacity=0.6, line=dict(width=1.5, color='DarkSlateGrey')))

        for i, docent in enumerate(docenten_met_hartslag):
            df_docent = df_conditie[df_conditie['Docent'] == docent].sort_values('Dagen')
            
            if len(df_docent) > 3: 
                X = df_docent[['Dagen']]
                y = df_docent['Efficientie']
                
                # Train lineair model
                lr = LinearRegression()
                lr.fit(X, y)
                
                # Voorspel de efficiëntie op Dag 0 en de Laatste Dag
                start_eff = lr.predict(pd.DataFrame({'Dagen': [0]}))[0]
                laatste_dag = df_docent['Dagen'].max()
                eind_eff = lr.predict(pd.DataFrame({'Dagen': [laatste_dag]}))[0]
                
                # Groeipercentage Formule: (Nieuw - Oud) / Oud * 100
                groei_pct = ((eind_eff - start_eff) / start_eff) * 100
                
                # Voeg de berekende trendlijn (de voorspelling) toe aan de grafiek
                df_docent['Trendlijn'] = lr.predict(X)
                fig_reg.add_scatter(
                    x=df_docent['Datum'], y=df_docent['Trendlijn'], 
                    mode='lines', name=f"Trend {docent}", 
                    line=dict(dash='dash', width=6, color=kleuren_map[docent]) 
                )
                
                with kolommen[i]:
                    st.metric(label=f"{docent}", value=f"{groei_pct:+.1f}%", delta="Efficiëntie")
            else:
                with kolommen[i]:
                    st.metric(label=f"{docent}", value="Te weinig data")

        # Bepaal het absolute minimum en maximum van de data voor strakke Y-as
        min_y = df_conditie['Efficientie'].min() * 0.90
        max_y = df_conditie['Efficientie'].max() * 1.10
        
        fig_reg.update_layout(
            height=600, 
            yaxis_range=[min_y, max_y], 
            yaxis_title="Efficiëntie Score (Snelheid / Hartslag)",
            xaxis_title="Datum",
            hovermode="x unified"
        )

        st.plotly_chart(fig_reg, use_container_width=True)
        
        st.info("💡 **Hoe lees je dit?** Een score van 0.20 betekent dat je voor elke hartslag per minuut, exact 0.20 km/u fietst. Hoe hoger de gestippelde trendlijn eindigt, hoe fitter de sporter fysiologisch is geworden!")
    else:
        st.warning("Geen hartslagdata gevonden om conditiegroei te berekenen. Zet de filters in de zijbalk aan!")
        

# TAB 6: Waar wordt er gefietst
with tab6:
    st.markdown("### 🗺️ GPS Telemetrie: Waar wordt er gefietst?")
    # Laad de GPS data in via het cache-geheugen
    @st.cache_data
    def load_gps_data():
        try:
            return pd.read_csv('gps_trajecten.csv', sep=';')
        except:
            return pd.DataFrame()
            
    df_gps = load_gps_data()
    
    if not df_gps.empty:
        df_gps_merged = pd.merge(df_gps, df_filtered[['Bestand', 'Docent']], on='Bestand', how='inner')
        
        if not df_gps_merged.empty:
            kaart_modus = st.radio(
                "Kies de kaartweergave:", 
                ["🌍 Alle Routes (Wie fietst waar?)", "📍 Specifieke Rit Analyseren (Snelheidskaart)"], 
                horizontal=True
            )
            
            st.divider()
            
            if kaart_modus == "🌍 Alle Routes (Wie fietst waar?)":
                st.write("Hier zie je het 'fietsgebied' van alle geselecteerde sporters. (Geoptimaliseerd voor snelheid!)")
                
                df_overzicht = df_gps_merged.copy()
                if len(df_overzicht) > 15000:
                    df_overzicht = df_overzicht.sample(n=15000, random_state=42)
                
                # Teken de wereldkaart over de volle breedte
                fig_all = px.scatter_mapbox(
                df_overzicht, lat="lat", lon="lon", color="Docent",
                zoom=6, mapbox_style="carto-darkmatter",
                center={"lat": 52.1326, "lon": 5.2913}  
        )
                
                fig_all.update_traces(marker=dict(size=3, opacity=0.5))
                fig_all.update_layout(
                    margin={"r":0,"t":40,"l":0,"b":0},
                    height=1500,
                    width=1500  
                )
                
                st.plotly_chart(fig_all, use_container_width=True, config={"scrollZoom": True})
                
            # MODUS 2: 1 RIT OP DE KAART
            else:
                st.write("Kies hieronder een specifieke rit om deze op de kaart te tekenen. De kleur geeft de snelheid aan!")
                col_links, col_rechts = st.columns([1, 2])
                
                with col_links:
                    beschikbare_ritten = df_gps_merged['Bestand'].unique()
                    gekozen_rit = st.selectbox("Kies een rit om te analyseren:", options=beschikbare_ritten)
                    
                    rit_info = df_filtered[df_filtered['Bestand'] == gekozen_rit].iloc[0]
                    st.metric("Sporter", f"{rit_info['Docent']}")
                    st.metric("Afstand", f"{rit_info['Afstand_km']} km")
                    st.metric("Snelheid", f"{rit_info['Gem_Snelheid_kmu']} km/u")
                    st.metric("Datum", f"{rit_info['Datum'].strftime('%d-%m-%Y')}")
                    
                with col_rechts:
                    df_route = df_gps_merged[df_gps_merged['Bestand'] == gekozen_rit]
                    
                    fig_map = px.scatter_mapbox(
                        df_route, lat="lat", lon="lon", color="snelheid_kmu",
                        color_continuous_scale=px.colors.sequential.Turbo, 
                        size_max=5, zoom=10, 
                        mapbox_style="carto-darkmatter",
                        title=f"Telemetrie Route: {gekozen_rit}"
                    )
                    fig_map.update_traces(marker=dict(size=4))
                    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
                    
                    st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True})
        else:
            st.warning("Geen GPS data gevonden voor de sporters die je nu in het filter hebt staan.")
    else:
        st.error("Kan gps_trajecten.csv niet vinden. Heb je het script gedraaid?")