import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

# ----------------------------
# Paths
# ----------------------------
ROOT = Path("C:/Users/nabil/Downloads/covid19 analysis")
DATA = ROOT

# ----------------------------
# Load datasets
# ----------------------------
df_country = pd.read_csv(DATA / "country_wise_latest.csv")
df_daywise = pd.read_csv(DATA / "day_wise.csv")
df_clean   = pd.read_csv(DATA / "covid_19_clean_complete.csv")
df_world   = pd.read_csv(DATA / "worldometer_data.csv")

# ----------------------------
# Page settings
# ----------------------------
st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")
st.title("🌍 COVID-19 Data Analysis")

# ----------------------------
# Theme toggle
# ----------------------------
theme = st.toggle("Themes", value=False)

if theme:
    template = "plotly_dark"
else:
    template = "plotly_white"

# ----------------------------
# Global summary metrics
# ----------------------------
latest = df_country[["Confirmed", "Deaths", "Recovered", "Active"]].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Confirmed", f"{latest['Confirmed']:,}")
col2.metric("Deaths", f"{latest['Deaths']:,}")
col3.metric("Recovered", f"{latest['Recovered']:,}")
col4.metric("Active", f"{latest['Active']:,}")

# ----------------------------
# Prepare data
# ----------------------------
# Global totals over time
global_daily = df_daywise.groupby("Date")[["Confirmed","Deaths","Recovered","Active"]].sum().reset_index()

# World totals for pie chart
world_totals = df_world[["TotalCases","TotalDeaths","TotalRecovered","ActiveCases"]].sum()

# ----------------------------
# Tabs for navigation
# ----------------------------
tab1, tab2, tab3 = st.tabs(["🌍 Global Trends", "📊 Country Analysis", "🗺 World Overview"])

# ===== TAB 1: GLOBAL =====
with tab1:
    st.subheader("Global Trends Over Time")

    fig1 = px.line(global_daily, x="Date", y=["Confirmed","Deaths","Recovered","Active"],
                   title="Global Totals Over Time", template=template)
    st.plotly_chart(fig1, use_container_width=True)

    top_n = st.slider("Top N countries", 5, 20, 10, key="top_n_global")
    top_countries = df_country.sort_values("Confirmed", ascending=False).head(top_n)

    fig2 = px.bar(top_countries, x="Country/Region", y="Confirmed",
                  title=f"Top {top_n} Countries by Confirmed Cases", template=template)
    st.plotly_chart(fig2, use_container_width=True)

# ===== TAB 2: COUNTRY =====
with tab2:
    st.subheader("Country Analysis")

    # Country filters inside tab
    country = st.selectbox("Select a country:", df_clean["Country/Region"].unique(), key="country_select")

    country_data = df_clean[df_clean["Country/Region"] == country].copy()
    country_data["NewCases"] = country_data["Confirmed"].diff().clip(lower=0)
    country_data["NewDeaths"] = country_data["Deaths"].diff().clip(lower=0)
    country_data["NewRecovered"] = country_data["Recovered"].diff().clip(lower=0)

    fig3 = px.line(country_data, x="Date", y=["Confirmed","Recovered","Deaths","Active"],
                   title=f"{country} - Totals Over Time", template=template)
    st.plotly_chart(fig3, use_container_width=True)

    fig_new = px.line(country_data, x="Date", y=["NewCases","NewDeaths","NewRecovered"],
                      title=f"{country} - Daily New Cases", template=template)
    st.plotly_chart(fig_new, use_container_width=True)

# ===== TAB 3: WORLD =====
with tab3:
    st.subheader("World Overview")

    fig_map = px.scatter_geo(df_country,
                             locations="Country/Region",
                             locationmode="country names",
                             size="Confirmed",
                             color="Confirmed",
                             hover_name="Country/Region",
                             projection="natural earth",
                             title="Global COVID-19 Spread",
                             template=template)
    st.plotly_chart(fig_map, use_container_width=True)

    fig4 = px.pie(names=world_totals.index, values=world_totals.values,
                  title="World COVID-19 Breakdown", template=template)
    st.plotly_chart(fig4, use_container_width=True)