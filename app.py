import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Youth Unemployment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0f1117; border-right: 1px solid #2a2f45; }
    .block-container { padding-top: 2.5rem; padding-bottom: 1rem; }
    .dashboard-title { font-size: 2.8rem; font-weight: 900; color: #ffffff; margin-bottom: 0.3rem; line-height: 1.2; }
    .dashboard-subtitle { color: #8899aa; font-style: italic; font-size: 1rem; margin-bottom: 1rem; }
    div[data-testid="metric-container"] {
        background: #1a1f35;
        border-radius: 10px;
        padding: 12px 18px;
        border-top: 3px solid #4da6ff;
    }
    div[data-testid="metric-container"] label { color: #8899aa !important; font-size: 0.78rem !important; }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 1.8rem !important; color: #ffffff !important; font-weight: 800 !important; }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.85rem !important; }
    .section-title { font-size: 1.4rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem; }
    .insight-box {
        background: #1a1f35; border-left: 4px solid #4da6ff;
        padding: 10px 16px; border-radius: 8px;
        margin-bottom: 8px; font-size: 0.85rem; color: #dde3f0;
    }
    hr { border-color: #2a3050; margin: 0.8rem 0; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1f35; border-radius: 8px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8899aa; border-radius: 6px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #4da6ff !important; color: white !important; }
    .stDataFrame { background: #1a1f35 !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("youth_unemployment_cleaned.csv")

df = load_data()
col_name = "Unemployment Rate (%)"
all_countries = sorted(df["Country Name"].unique())
all_years = sorted(df["Year"].unique())

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 Dashboard Controls")
    st.markdown("---")

    st.markdown("##### 🗂️ Select Category")
    category = st.selectbox("", ["All Genders", "Male Only", "Female Only"], label_visibility="collapsed")

    st.markdown("##### 🌍 Select Countries")
    selected_countries = st.multiselect("", all_countries,
        default=["United Kingdom", "Sri Lanka", "India", "United States", "South Africa"],
        label_visibility="collapsed")

    st.markdown("##### 📅 Year Range")
    year_min, year_max = st.slider("", min_value=int(min(all_years)),
        max_value=int(max(all_years)), value=(1990, 2023), label_visibility="collapsed")

    st.markdown("##### 🎨 Chart Theme")
    theme_map = {"Dark": "plotly_dark", "Light": "plotly", "GGPlot": "ggplot2", "Seaborn": "seaborn"}
    theme_label = st.selectbox("", list(theme_map.keys()), label_visibility="collapsed")
    chart_theme = theme_map[theme_label]

    normalise = st.toggle("📊 Normalise Data", value=False)

    st.markdown("---")
    st.markdown("##### 🚀 About")
    st.caption("Youth Unemployment Gender Gap Dashboard\n\nStudent: Senuji Thuduhenage\nID: 20242176\n\n5DATA004C Coursework\nUniversity of Westminster")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

# Title
col_title, col_flag = st.columns([5, 1])
with col_title:
    st.markdown('<div class="dashboard-title">📊 Youth Unemployment<br>Gender Gap Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Tracking male vs female youth unemployment (ages 15–24) from 1960 to 2025 &nbsp;|&nbsp; Source: World Bank WDI &nbsp;|&nbsp; SDG 5: Gender Equality &nbsp;|&nbsp; SDG 8: Decent Work</div>', unsafe_allow_html=True)
with col_flag:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Flag_of_Sri_Lanka.svg/200px-Flag_of_Sri_Lanka.svg.png", width=80)

st.markdown("---")

# ── About expander ─────────────────────────────────────────────────────────────
with st.expander("ℹ️ About This Dashboard"):
    st.markdown("""
    This dashboard visualises **youth unemployment rates** (ages 15–24) for **males and females** across **239 countries** from **1960 to 2025**.
    Data is sourced from the **World Bank World Development Indicators (WDI)** — an approved open data source.
    - **SDG 5**: Gender Equality — highlights disparities in employment opportunities
    - **SDG 8**: Decent Work and Economic Growth — tracks youth labour market outcomes
    Use the **sidebar controls** to filter by gender, countries, year range and visual theme.
    """)

# ── Compute KPI data for selected year range ───────────────────────────────────
latest_year = year_max
earliest_year = year_min

all_latest = df[df["Year"] == latest_year]
all_earliest = df[df["Year"] == earliest_year]

male_latest = all_latest[all_latest["Gender"] == "Male"][col_name].mean()
female_latest = all_latest[all_latest["Gender"] == "Female"][col_name].mean()
male_earliest = all_earliest[all_earliest["Gender"] == "Male"][col_name].mean()
female_earliest = all_earliest[all_earliest["Gender"] == "Female"][col_name].mean()
gap = female_latest - male_latest
countries_count = all_latest["Country Name"].nunique()

top_female = all_latest[all_latest["Gender"] == "Female"].nlargest(1, col_name)
top_female_country = top_female["Country Name"].values[0] if len(top_female) > 0 else "N/A"
top_female_val = top_female[col_name].values[0] if len(top_female) > 0 else 0

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown(f'<div class="section-title">📈 Key Statistics ({latest_year})</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(f"Avg Female Unemp.", f"{female_latest:.1f}%",
          delta=f"{female_latest - female_earliest:+.1f}% since {earliest_year}")
k2.metric(f"Avg Male Unemp.", f"{male_latest:.1f}%",
          delta=f"{male_latest - male_earliest:+.1f}% since {earliest_year}")
k3.metric("Gender Gap (F - M)", f"{gap:+.1f}%")
k4.metric("Countries with Data", int(countries_count))
k5.metric("Highest Female Rate", f"{top_female_val:.1f}%", help=f"Country: {top_female_country}")

st.markdown("---")

# ── Auto Insights ──────────────────────────────────────────────────────────────
with st.expander("💡 Auto Insights", expanded=True):
    i1, i2 = st.columns(2)
    with i1:
        if gap > 5:
            msg = f"🔴 <b>High gender gap:</b> Female youth unemployment is <b>{gap:.1f}%</b> higher than male in {latest_year}."
        elif gap > 0:
            msg = f"🟡 <b>Moderate gender gap:</b> Female unemployment is <b>{gap:.1f}%</b> higher than male in {latest_year}."
        else:
            msg = f"🟢 <b>Unusual trend:</b> Male unemployment exceeds female by <b>{abs(gap):.1f}%</b> in {latest_year}."
        st.markdown(f'<div class="insight-box">{msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-box">📍 <b>Worst affected ({latest_year}):</b> <b>{top_female_country}</b> — female rate at <b>{top_female_val:.1f}%</b>.</div>', unsafe_allow_html=True)
    with i2:
        f_change = female_latest - female_earliest
        direction = "📈 increased" if f_change > 0 else "📉 decreased"
        st.markdown(f'<div class="insight-box">📆 <b>Long-term change:</b> Global avg female youth unemployment <b>{direction} by {abs(f_change):.1f}%</b> from {earliest_year} to {latest_year}.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-box">📊 <b>Data coverage:</b> <b>{int(countries_count)}</b> countries reported data in {latest_year}, out of 239 in the dataset.</div>', unsafe_allow_html=True)

st.markdown("---")

# ── Filter data ────────────────────────────────────────────────────────────────
filtered = df[(df["Year"] >= year_min) & (df["Year"] <= year_max)].copy()
if category == "Male Only":
    filtered = filtered[filtered["Gender"] == "Male"]
elif category == "Female Only":
    filtered = filtered[filtered["Gender"] == "Female"]

if normalise:
    max_v = filtered[col_name].max()
    if max_v > 0:
        filtered[col_name] = (filtered[col_name] / max_v * 100).round(2)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trend Analysis", "🌍 World Map", "🏆 Top Countries", "⚖️ Gender Comparison", "🗃️ Data Explorer"
])

# ── TAB 1: Trend Analysis ──────────────────────────────────────────────────────
with tab1:
    if selected_countries:
        trend_df = filtered[filtered["Country Name"].isin(selected_countries)]
        fig = px.line(trend_df, x="Year", y=col_name, color="Country Name", line_dash="Gender",
                      template=chart_theme, title="Youth Unemployment Trend Over Time",
                      labels={col_name: "Unemployment %"})
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(height=420, legend=dict(orientation="h", y=-0.2, font=dict(size=10)))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Select at least one country in the sidebar to see trends.")

# ── TAB 2: World Map ───────────────────────────────────────────────────────────
with tab2:
    map_gender = st.radio("Map gender:", ["Male", "Female"], horizontal=True)
    map_data = all_latest[all_latest["Gender"] == map_gender].copy()
    fig_map = px.choropleth(map_data, locations="Country Code", color=col_name,
        hover_name="Country Name", color_continuous_scale="RdYlGn_r", range_color=[0, 60],
        projection="natural earth", template=chart_theme,
        title=f"{map_gender} Youth Unemployment (%) – {latest_year}")
    fig_map.update_layout(height=450, margin=dict(l=0, r=0, t=40, b=0),
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="gray",
                 showland=True, landcolor="#1a1f35" if "dark" in chart_theme else "#f0f0f0",
                 showocean=True, oceancolor="#0d1117" if "dark" in chart_theme else "#cde5f5"),
        coloraxis_colorbar=dict(thickness=14, len=0.7, title="%"))
    st.plotly_chart(fig_map, use_container_width=True)

# ── TAB 3: Top Countries ───────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        top_f = all_latest[all_latest["Gender"] == "Female"].nlargest(10, col_name)
        fig_f = px.bar(top_f, x=col_name, y="Country Name", orientation="h",
            color=col_name, color_continuous_scale="Reds", template=chart_theme,
            title=f"Top 10 – Female ({latest_year})", labels={col_name: "Unemployment %", "Country Name": ""})
        fig_f.update_layout(height=380, yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig_f, use_container_width=True)
    with c2:
        top_m = all_latest[all_latest["Gender"] == "Male"].nlargest(10, col_name)
        fig_m = px.bar(top_m, x=col_name, y="Country Name", orientation="h",
            color=col_name, color_continuous_scale="Blues", template=chart_theme,
            title=f"Top 10 – Male ({latest_year})", labels={col_name: "Unemployment %", "Country Name": ""})
        fig_m.update_layout(height=380, yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig_m, use_container_width=True)

# ── TAB 4: Gender Comparison ───────────────────────────────────────────────────
with tab4:
    male_yr = all_latest[all_latest["Gender"] == "Male"][["Country Name", "Country Code", col_name]].rename(columns={col_name: "Male"})
    female_yr = all_latest[all_latest["Gender"] == "Female"][["Country Name", "Country Code", col_name]].rename(columns={col_name: "Female"})
    scatter_data = male_yr.merge(female_yr, on=["Country Name", "Country Code"]).dropna()
    fig_s = px.scatter(scatter_data, x="Male", y="Female", hover_name="Country Name",
        color="Female", color_continuous_scale="OrRd", template=chart_theme,
        title=f"Male vs Female Youth Unemployment – {latest_year}",
        labels={"Male": "Male Unemployment %", "Female": "Female Unemployment %"})
    max_v = max(scatter_data["Male"].max(), scatter_data["Female"].max())
    fig_s.add_shape(type="line", x0=0, y0=0, x1=max_v, y1=max_v, line=dict(color="cyan", dash="dash", width=2))
    fig_s.add_annotation(x=max_v*0.7, y=max_v*0.82, text="← Equality Line →", showarrow=False, font=dict(color="cyan", size=11))
    fig_s.update_layout(height=430, coloraxis_showscale=False)
    st.plotly_chart(fig_s, use_container_width=True)

# ── TAB 5: Data Explorer ───────────────────────────────────────────────────────
with tab5:
    show_all = st.checkbox("Show all countries", value=False)
    sort_by = st.selectbox("Sort by", [col_name, "Country Name", "Year", "Gender"])
    if show_all or not selected_countries:
        display_df = filtered.sort_values(sort_by, ascending=(sort_by != col_name)).reset_index(drop=True)
    else:
        display_df = filtered[filtered["Country Name"].isin(selected_countries)].sort_values(sort_by, ascending=(sort_by != col_name)).reset_index(drop=True)
    st.dataframe(display_df, use_container_width=True, height=380)
    st.caption(f"Showing {len(display_df):,} rows")

st.markdown("---")
st.caption("🎓 5DATA004C Individual Coursework | Senuji Thuduhenage (20242176) | University of Westminster | Data: World Bank WDI")