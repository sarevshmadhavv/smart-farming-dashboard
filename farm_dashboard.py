# ==============================
# 🌱 AI Smart Farming Dashboard
# Works with villages & towns (geocoding)
# Features: Weather • Crop Advisory • Irrigation • Pest Risk • Yield Score • Climate Scenario
# ==============================

import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from math import isfinite
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------- CONFIG ----------
USERS_FILE = "users.csv"
ADMIN_EMAIL = "ms.sarveshmadhavv@gmail.com"
ADMIN_PASSWORD = "sarvesh21"
LOG_FILE = "user_activity_log.csv"

# ---------- INIT FILES ----------
if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["name", "email", "phone", "password"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["timestamp","name","email","phone","action"]).to_csv(LOG_FILE, index=False)

# ---------- FUNCTIONS ----------
def load_users():
    return pd.read_csv(USERS_FILE)

def save_user(name, email, phone, password):
    df = load_users()
    df = pd.concat([df, pd.DataFrame([[name, email, phone, password]], columns=df.columns)], ignore_index=True)
    df.to_csv(USERS_FILE, index=False)

def check_user(email, password):
    df = load_users()
    return not df[(df["email"] == email) & (df["password"] == password)].empty

def get_user_by_email(email):
    df = load_users()
    user_row = df[df["email"] == email]
    if user_row.empty: return None
    row = user_row.iloc[0]
    return {"name": row["name"], "email": row["email"], "phone": row["phone"], "password": row["password"]}

def log_activity(name, email, phone, action):
    df_log = pd.read_csv(LOG_FILE)
    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email, phone, action]], columns=df_log.columns)
    df_log = pd.concat([df_log, new_row], ignore_index=True)
    df_log.to_csv(LOG_FILE, index=False)

# ---------- SESSION STATE ----------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

# ---------- AUTH UI ----------
if not st.session_state["logged_in"]:
    st.title("🌱 AI Smart Farming Dashboard - Login / Register")
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    # ----- LOGIN -----
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):

            # Admin login
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                st.session_state["logged_in"] = True
                st.session_state["is_admin"] = True
                st.session_state["user_email"] = email
                st.success("Welcome Admin!")
                log_activity("Admin", ADMIN_EMAIL, "", "login")
                st.rerun()

            # Normal user login
            elif check_user(email, password):
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.success("Login successful!")
                user = get_user_by_email(email)
                log_activity(user["name"], user["email"], user.get("phone",""), "login")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    # ----- REGISTER -----
    with tab2:
        name = st.text_input("Full Name", key="reg_name")
        email_r = st.text_input("Email", key="reg_email")
        phone = st.text_input("Phone Number", key="reg_phone")
        password_r = st.text_input("Create Password", type="password", key="reg_password")

        if st.button("Register", key="register_btn"):
            if not name or not email_r or not password_r:
                st.warning("Please fill all required fields.")
            else:
                df = load_users()
                if email_r in df["email"].values:
                    st.error("Email already registered.")
                else:
                    save_user(name, email_r, phone, password_r)
                    st.success("Registration successful! You can now log in.")

    st.stop()

# ---------- DASHBOARD ----------
if st.session_state["logged_in"]:

        # ----- ADMIN DASHBOARD -----
    if st.session_state.get("is_admin"):
        st.sidebar.success("👑 Admin Access Granted")
        st.sidebar.markdown("---")
        st.sidebar.write("**All Registered Users:**")

        # Load users
        try:
            users = load_users()
        except Exception as e:
            st.error(f"Failed to load users.csv: {e}")
            users = pd.DataFrame(columns=["name","email","phone","password"])

        # Display table
        if users.empty:
            st.sidebar.info("No users registered yet.")
        else:
            st.sidebar.dataframe(users)

        # Download button (works even if empty)
        st.sidebar.download_button(
            label="📥 Download Users CSV",
            data=users.to_csv(index=False),
            file_name="users.csv",
            mime="text/csv",
            key="download_users_csv"
        )

            # Reset all app data
        st.sidebar.markdown("---")
        if st.sidebar.button("⚠️ Reset All App Data"):
            # Clear users CSV
            pd.DataFrame(columns=["name","email","phone","password"]).to_csv("users.csv", index=False)
            # Clear activity log
            pd.DataFrame(columns=["timestamp","name","email","phone","action"]).to_csv("user_activity_log.csv", index=False)
            st.sidebar.success("All app data cleared! Users and activity logs are reset.")

        # Optional: display login/logout activity
        try:
            log_df = pd.read_csv("user_activity_log.csv")
            st.sidebar.markdown("---")
            st.sidebar.write("**Login/Logout Activity:**")
            if log_df.empty:
                st.sidebar.info("No activity yet.")
            else:
                st.sidebar.dataframe(log_df)
            st.sidebar.download_button(
                label="📥 Download Activity Log",
                data=log_df.to_csv(index=False),
                file_name="user_activity_log.csv",
                mime="text/csv",
                key="download_activity_csv"
            )
        except FileNotFoundError:
            st.sidebar.info("No activity log found yet.")

    # ----- NORMAL USER DASHBOARD -----
    else:
        st.title("🌱 AI Smart Farming Dashboard")
        user_email = st.session_state["user_email"]
        user = get_user_by_email(user_email)
        st.subheader(f"Welcome, {user['name']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Phone:** {user['phone'] or '—'}")

    # ---------- LOGOUT BUTTON ----------
    logout_clicked = st.button("Logout", key="logout_btn")
    if logout_clicked:
        # Log logout activity
        if st.session_state.get("is_admin"):
            log_activity("Admin", ADMIN_EMAIL, "", "logout")
        else:
            user = get_user_by_email(st.session_state.get("user_email"))
            if user:
                log_activity(user["name"], user["email"], user.get("phone",""), "logout")

        # Clear session state
        st.session_state.clear()

        # Instead of st.experimental_rerun(), just show message and stop
        st.success("Logged out successfully. Please refresh or relaunch the app to login again.")
        st.stop()



# ------------------------------
# 🎨 Background Image
# ------------------------------
background_url = "https://plus.unsplash.com/premium_photo-1661907005604-cec7ffb6a042?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# 🔑 OpenWeatherMap API KEY
# ------------------------------
API_KEY = "18406bb4885186a7985d590bb3109abd"  # <-- keep it in quotes!

# ------------------------------
# 🧩 Utilities
# ------------------------------
@st.cache_data(show_spinner=False, ttl=60 * 30)
def geocode_place(place: str):
    """Return (lat, lon, display_name) using OpenWeather Geocoding API."""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={place}&limit=1&appid={API_KEY}"
    r = requests.get(url, timeout=12).json()
    if not isinstance(r, list) or len(r) == 0:
        return None
    d = r[0]
    name_bits = [d.get("name")]
    if d.get("state"):
        name_bits.append(d["state"])
    if d.get("country"):
        name_bits.append(d["country"])
    return float(d["lat"]), float(d["lon"]), ", ".join([x for x in name_bits if x])

@st.cache_data(show_spinner=False, ttl=15 * 60)
def fetch_forecast(lat: float, lon: float):
    """5-day / 3-hour forecast for the coordinates. Returns raw JSON."""
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    r = requests.get(url, timeout=12).json()
    if "list" not in r:
        return None
    return r

def to_frames(forecast_json):
    """Convert forecast JSON to tidy DataFrames: 3-hourly and daily aggregates."""
    rows = []
    for it in forecast_json["list"]:
        rows.append({
            "time": it["dt_txt"],
            "temp": it["main"]["temp"],
            "humidity": it["main"]["humidity"],
            "wind": it["wind"]["speed"],
            "rain_3h": it.get("rain", {}).get("3h", 0.0),
            "weather": it["weather"][0]["main"],
            "desc": it["weather"][0]["description"],
        })
    df3h = pd.DataFrame(rows)
    # Daily aggregates
    df3h["date"] = pd.to_datetime(df3h["time"]).dt.date
    dfd = df3h.groupby("date").agg(
        tmin=("temp", "min"),
        tmax=("temp", "max"),
        tavg=("temp", "mean"),
        humidity_mean=("humidity", "mean"),
        wind_mean=("wind", "mean"),
        rain_total=("rain_3h", "sum"),
    ).reset_index()
    return df3h, dfd

# ------------------------------
# 🤖 Simple AI/Heuristics (no training needed)
# ------------------------------
def crop_recommendation(avg_temp, avg_hum, rain_total):
    """Return a friendly crop suggestion string."""
    if avg_temp is None or avg_hum is None or rain_total is None:
        return "Data not available"
    if avg_temp >= 26 and rain_total >= 40 and avg_hum >= 60:
        return "🌾 Best fit: Rice / Maize"
    if 20 <= avg_temp < 26 and 20 <= rain_total < 60 and 40 <= avg_hum <= 75:
        return "🌿 Best fit: Pulses / Groundnut"
    if avg_temp < 20 and rain_total < 20:
        return "🌾 Best fit: Wheat / Barley"
    return "🌱 Mixed conditions → Consider Vegetables / Millets"

def irrigation_advice(tavg, humidity, rain_next_days):
    """ Simple irrigation in mm/day. """
    if any(x is None for x in [tavg, humidity, rain_next_days]):
        return 0.0, "Data not available"
    base = max(0.0, 0.35 * tavg - 0.12 * (humidity / 10))
    effective_rain_per_day = (rain_next_days / 3.0)  # distribute forecasted rain over next 3 days
    mm_day = max(0.0, base - 0.6 * effective_rain_per_day)  # 60% effective rainfall
    tip = "💧 Irrigate in early morning; avoid evening irrigation if humidity is high."
    return round(mm_day, 2), tip

def pest_disease_risk(tavg, humidity, rain_total):
    """ Simple risk score 0-100. """
    if any(x is None for x in [tavg, humidity, rain_total]):
        return 0, "Data not available"
    score = 0
    if 20 <= tavg <= 30:
        score += 35
    if humidity >= 75:
        score += 40
    if rain_total >= 20:
        score += 25
    score = min(100, score)
    if score >= 70:
        msg = "🔴 High risk: consider spacing, better airflow, and preventive fungicide if advised locally."
    elif score >= 40:
        msg = "🟠 Medium risk: monitor closely; avoid late watering; remove infected leaves."
    else:
        msg = "🟢 Low risk: keep normal hygiene and watch weather changes."
    return score, msg

def yield_potential_index(tavg, humidity, rain_total):
    """Friendly 0–100 score based on conditions."""
    if any(x is None for x in [tavg, humidity, rain_total]):
        return 0
    s = 0
    # Temperature
    if 22 <= tavg <= 28:
        s += 45
    elif 18 <= tavg < 22 or 28 < tavg <= 32:
        s += 30
    else:
        s += 15
    # Humidity
    if 50 <= humidity <= 75:
        s += 30
    elif 40 <= humidity < 50 or 75 < humidity <= 85:
        s += 20
    else:
        s += 10
    # Rain
    if 10 <= rain_total <= 40:
        s += 25
    elif 0 <= rain_total < 10 or 40 < rain_total <= 80:
        s += 15
    else:
        s += 5
    return int(min(100, s))

def format_badge(value, good_high=True):
    """Return HTML badge with color based on value."""
    if not isfinite(float(value)):
        value = 0
    v = float(value)
    if good_high:
        color = "#16a34a" if v >= 70 else ("#f59e0b" if v >= 40 else "#ef4444")
    else:
        color = "#ef4444" if v >= 70 else ("#f59e0b" if v >= 40 else "#16a34a")
    return f"<span style='background:{color};color:white;padding:4px 10px;border-radius:12px;font-weight:600'>{int(v)}</span>"

# ------------------------------
# 🎨 Page & Header
# ------------------------------
st.set_page_config(page_title="AI Smart Farming", page_icon="🌱", layout="wide")
st.markdown("<h1 style='text-align:center;color:#16a34a;'>🌱 AI Smart Farming Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:black;'>Weather • Crop Advisory • Irrigation • Pest Risk • Yield Score • Climate Scenario</p>", unsafe_allow_html=True)
st.markdown("---")

# ------------------------------
# 📍 Input (Villages/Cities)
# ------------------------------
colA, colB = st.columns([2,1])
with colA:
    place = st.text_input("Enter village/town/city name (anywhere):", "Kumbakonam")
with colB:
    if st.button("Run Advisor", type="primary"):
        st.session_state["run_advisor"] = True  # ✅ Save state

# ------------------------------
# Main Logic
# ------------------------------
if st.session_state.get("run_advisor", False):   # ✅ Persist after button
    if not API_KEY or API_KEY.strip() == "PASTE_YOUR_OPENWEATHER_API_KEY_HERE":
        st.error("Please paste your OpenWeatherMap API key at the top of the file (inside quotes).")
        st.stop()
    
    with st.spinner("Finding your location…"):
        geo = geocode_place(place)
        if not geo:
            st.error("Place not found. Try another name or include district/state.")
            st.stop()
        lat, lon, pretty_name = geo
        st.success(f"📍 Location detected: **{pretty_name}** (lat: {lat:.3f}, lon: {lon:.3f})")
        st.map(pd.DataFrame({"lat":[lat], "lon":[lon]}), size=100)

    with st.spinner("Fetching 5-day forecast…"):
        raw = fetch_forecast(lat, lon)
        if raw is None:
            st.error("Could not fetch forecast. Check your API key/quota or try again later.")
            st.stop()
        df3h, dfd = to_frames(raw)

    # ✅ Rest of your metrics, tabs, climate simulator remain unchanged...

    # ------------- Top Metrics -------------
    next3 = dfd.head(3)
    tavg = float(next3["tavg"].mean()) if not next3.empty else None
    hum = float(next3["humidity_mean"].mean()) if not next3.empty else None
    rain3d = float(next3["rain_total"].sum()) if not next3.empty else None

    yscore = yield_potential_index(tavg, hum, rain3d)
    pest_score, pest_msg = pest_disease_risk(tavg, hum, rain3d)
    irr_mm, irr_tip = irrigation_advice(tavg, hum, rain3d)
    crop_msg = crop_recommendation(tavg, hum, rain3d)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Avg Temp (next 3 days)", f"{tavg:.1f} °C" if tavg is not None else "—")
    m2.metric("Avg Humidity (next 3 days)", f"{hum:.0f} %" if hum is not None else "—")
    m3.metric("Rain (next 3 days)", f"{rain3d:.1f} mm" if rain3d is not None else "—")
    m4.metric("Irrigation Need", f"{irr_mm:.1f} mm/day" if irr_mm is not None else "—")
    st.markdown("---")

    # ------------- Tabs -------------
    tab1, tab2, tab3 = st.tabs(["🌤 Weather", "🚜 Crop & Yield", "🐛 Pest & Irrigation"])

    with tab1:
        st.subheader("3-Hourly Forecast (next ~2 days)")
        st.dataframe(df3h[["time","temp","humidity","wind","rain_3h","desc"]].head(16), use_container_width=True)

        st.subheader("Daily Summary (next 5 days)")
        st.dataframe(dfd, use_container_width=True)

        st.subheader("Trends")
        c1, c2 = st.columns(2)
        with c1:
            tmp = df3h[["time","temp"]].copy()
            tmp.set_index("time", inplace=True)
            st.line_chart(tmp)
        with c2:
            rainp = df3h[["time","rain_3h"]].copy()
            rainp.set_index("time", inplace=True)
            st.bar_chart(rainp)

    with tab2:
        st.subheader("AI Crop Recommendation")
        st.success(crop_msg)

        st.subheader("Yield Potential Index (0–100)")
        badge = format_badge(yscore, good_high=True)
        st.markdown(f"**Score:** {badge}", unsafe_allow_html=True)
        st.caption("Higher is better based on next-3-day temp, humidity, and rain.")

        st.subheader("Climate Scenario Simulator")
        colx, coly = st.columns(2)
        with colx:
            dT = st.slider("Δ Temperature (°C)", -3, 4, 0)
        with coly:
            dR = st.slider("Δ Rainfall (%)", -40, 40, 0)
        tavg_s = None if tavg is None else (tavg + dT)
        rain3d_s = None if rain3d is None else (rain3d * (1 + dR/100))
        hum_s = hum  # keep same humidity for simplicity
        yscore_s = yield_potential_index(tavg_s, hum_s, rain3d_s)
        st.write(f"**Scenario Score:** {yscore_s} (was {yscore})")
        st.caption("Try hotter/drier or cooler/wetter to see resilience.")

    with tab3:
        st.subheader("Pest/Disease Risk (0–100)")
        bad = format_badge(pest_score, good_high=False)
        st.markdown(f"**Risk:** {bad}", unsafe_allow_html=True)
        st.info(pest_msg)

        st.subheader("Smart Irrigation Advice")
        st.write(f"💧 **Recommended:** **{irr_mm:.1f} mm/day** (adjust with rainfall)")
        st.caption(irr_tip)

        st.subheader("Actionable Tips")
        tips = []
        if hum and hum > 80:
            tips.append("Avoid evening irrigation; promote airflow to reduce leaf wetness.")
        if rain3d and rain3d > 30:
            tips.append("Expect runoff; consider split irrigation after rainy spell.")
        if tavg and tavg > 32:
            tips.append("High heat stress: mulching and mid-day shade can reduce evaporation.")
        if not tips:
            tips.append("Conditions are normal. Keep standard field hygiene and monitor forecasts.")
        for t in tips:
            st.write(f"• {t}")

st.markdown("Built For SASTRA by Sarvesh Madhav M S - 229004092")
