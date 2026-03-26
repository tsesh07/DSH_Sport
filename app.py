import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
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

# 3. ZIJBALK (FILTERS)
st.sidebar.header("Filter de Data")
geselecteerde_docenten = st.sidebar.multiselect(
    "Kies Sporters:",
    options=df['Docent'].unique(),
    default=df['Docent'].unique() # Standaard iedereen geselecteerd
)

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

tab6, tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Route Kaart","📈 Snelheid & Volume", "🫀 Fysieke Efficiëntie", "🏆 Leaderboard & Gedrag", "🤖 AI Voorspellingen", "📈 Conditiegroei"])

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
        # Deze code is extra robuust gemaakt zodat het dataframe niet onverwacht wijzigt
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
        
# TAB 4: AI & Machine Learning (Random Forest)
with tab4:
    st.markdown("### 🔮 Random Forest Predictor")
    st.write("We hebben live een Random Forest Machine Learning model getraind op jullie data. Vul hieronder een geplande rit in, en de AI voorspelt de gemiddelde snelheid!")
    
    # 1. Data voorbereiden voor het model
    df_ml = df_filtered.dropna(subset=['Gem_Snelheid_kmu', 'Afstand_km', 'Datum']).copy()
    
    if len(df_ml) > 10: # Het model heeft data nodig om van te leren
        
        # Feature Engineering: We maken een variabele "Conditie". 
        # Hoe meer dagen sinds de eerste rit, hoe meer getraind de sporter is.
        datum_min = df_ml['Datum'].min()
        df_ml['Dagen_sinds_start'] = (pd.to_datetime(df_ml['Datum']) - pd.to_datetime(datum_min)).dt.days
        
        # encoding van namen naar numericals
        df_ml_encoded = pd.get_dummies(df_ml, columns=['Docent'])
        
        features = ['Afstand_km', 'Dagen_sinds_start'] + [col for col in df_ml_encoded.columns if col.startswith('Docent_')]
        X = df_ml_encoded[features]
        y = df_ml_encoded['Gem_Snelheid_kmu'] 
        
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X, y)
        
        st.divider()
        
        # Interactieve Voorspeller (User Interface)
        col_links, col_rechts = st.columns(2)
        
        with col_links:
            input_docent = st.selectbox("Wie gaat er fietsen?", options=df_filtered['Docent'].unique())
            input_afstand = st.slider("Geplande Afstand (km)", min_value=5.0, max_value=250.0, value=60.0, step=5.0)
            
            vandaag = datetime.date.today()
            dagen_nu = (pd.to_datetime(vandaag) - pd.to_datetime(datum_min)).days
            
        with col_rechts:
            input_data = pd.DataFrame(columns=X.columns)
            input_data.loc[0] = 0 # Zet alles standaard op 0
            
            input_data['Afstand_km'] = input_afstand
            input_data['Dagen_sinds_start'] = dagen_nu
            
            docent_kolom = f'Docent_{input_docent}'
            if docent_kolom in input_data.columns:
                input_data[docent_kolom] = 1
                
            voorspelling = rf_model.predict(input_data)[0]
            
            st.markdown(f"#### 🎯 Verwachte Snelheid:")
            st.metric(label="", value=f"{voorspelling:.1f} km/u")
            
            st.info(f"💡 **Hoe werkt dit?** Het AI-model kijkt naar historische ritten rond de {input_afstand} km van {input_docent}, neemt de actuele opgebouwde conditie mee, en vergelijkt dit met patronen van de andere rijders.")

    else:
        st.warning("Te weinig ritten geselecteerd om de AI te trainen. Kies meer sporters in het filter!")

# TAB 5: Conditiegroei (Lineaire Regressie)
from sklearn.linear_model import LinearRegression

with tab5:
    st.markdown("### 🫀📈 Conditiegroei: Wordt de motor groter?")
    st.write("We berekenen de **Efficiëntie-score** (Snelheid gedeeld door Hartslag). Een stijgende lijn betekent dat je harder fietst met minder moeite. Met een *Lineair Regressie Model* berekenen we het exacte groeipercentage over tijd!")

    # 1. Haal alle ritten zonder hartslag eruit
    df_conditie = df_filtered.dropna(subset=['Gem_Snelheid_kmu', 'Gem_Hartslag', 'Datum']).copy()

    if not df_conditie.empty:
        # 2. BEREKEN DE EFFICIËNTIE (Hoe hoger, hoe beter)
        df_conditie['Efficientie'] = df_conditie['Gem_Snelheid_kmu'] / df_conditie['Gem_Hartslag']
        
        # Bereken dagen sinds eerste rit (voor de X-as van het wiskundige model)
        datum_min = df_conditie['Datum'].min()
        df_conditie['Dagen'] = (pd.to_datetime(df_conditie['Datum']) - pd.to_datetime(datum_min)).dt.days

        st.markdown("#### 🏆 Groeipercentage per Sporter:")
        
        # Maak dynamische kolommen voor de statistieken
        docenten_met_hartslag = df_conditie['Docent'].unique()
        kolommen = st.columns(len(docenten_met_hartslag))
        
        # Basis grafiek met de losse puntjes
        fig_reg = px.scatter(
            df_conditie, x='Datum', y='Efficientie', color='Docent', 
            hover_data=['Gem_Snelheid_kmu', 'Gem_Hartslag'],
            title="Cardiovasculaire Ontwikkeling over Tijd",
            render_mode='svg'
        )

        # 3. TRAIN HET MODEL PER DOCENT
        for i, docent in enumerate(docenten_met_hartslag):
            df_docent = df_conditie[df_conditie['Docent'] == docent].sort_values('Dagen')
            
            # Een lineaire lijn trekken kan pas vanaf minimaal 3 ritten
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
                    line=dict(dash='dash') # Maak er een stippellijn van
                )
                
                # Toon het groeipercentage mooi in de app
                with kolommen[i]:
                    st.metric(label=f"{docent}", value=f"{groei_pct:+.1f}%", delta="Efficiëntie")
            else:
                with kolommen[i]:
                    st.metric(label=f"{docent}", value="Te weinig data")

        # Laat de complete grafiek zien
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
                
                fig_all = px.scatter_mapbox(
                    df_overzicht, lat="lat", lon="lon", color="Docent",
                    zoom=7, mapbox_style="carto-darkmatter",
                    title="Overzichtskaart: Actieve Regio's"
                )
                
                fig_all.update_traces(marker=dict(size=3, opacity=0.5))
                fig_all.update_layout(
                    margin={"r":0,"t":40,"l":0,"b":0},
                    height=1500,
                    width=1500  
                )
                
                st.plotly_chart(fig_all, use_container_width=True)
                
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
                    
                    st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Geen GPS data gevonden voor de sporters die je nu in het filter hebt staan.")
    else:
        st.error("Kan gps_trajecten.csv niet vinden. Heb je het script gedraaid?")