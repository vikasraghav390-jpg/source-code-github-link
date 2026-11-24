"""Run: streamlit run app/streamlit_app.py   (first run: python forecast/train.py)"""
import json, sqlite3, sys
import pandas as pd, streamlit as st
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forecast"))
from dispatch import advice

st.set_page_config(page_title="Community Microgrid Forecast", layout="wide")
st.title("Community Microgrid Energy Forecasting")
res_p, pred_p = ROOT / "outputs/results.json", ROOT / "outputs/test_predictions.csv"
if not (res_p.exists() and pred_p.exists()):
    st.error("No results yet. Run `python forecast/train.py` first."); st.stop()
res, tp = json.loads(res_p.read_text()), pd.read_csv(pred_p, parse_dates=["ts"])
st.warning("Forecast tabs show results from a synthetic dataset (simulation), not field measurements.")
tab1, tab2, tab3 = st.tabs(["Forecast", "Model metrics", "Live telemetry"])

with tab1:
    tp["date"] = tp.ts.dt.date
    day = st.selectbox("Date", sorted(tp.date.unique()))
    d = tp[tp.date == day].set_index("ts")
    c1, c2 = st.columns(2)
    c1.subheader("PV generation (kW)"); c1.line_chart(d[["pv_actual", "pv_forecast", "pv_persistence"]])
    c2.subheader("Community load (kW)"); c2.line_chart(d[["load_actual", "load_forecast", "load_persistence"]])
    st.subheader("Battery SoC (simulated, %)"); st.line_chart(d[["soc"]])
    st.info(advice((d.load_forecast - d.pv_forecast).values, float(d.soc.iloc[0]), res["threshold_kw"]))

with tab2:
    rows = [{"target": k.split("|")[0], "model": k.split("|")[1], **v} for k, v in res["metrics"].items()]
    st.dataframe(pd.DataFrame(rows).round(2), use_container_width=True)
    a = res["alert"]
    st.metric("Alert precision %", f"{a['precision']:.1f}"); st.metric("Alert recall %", f"{a['recall']:.1f}")
    st.json(res["dispatch"])

with tab3:
    db = ROOT / "data/microgrid.db"
    if db.exists():
        t = pd.read_sql("SELECT * FROM telemetry ORDER BY ts DESC LIMIT 500", sqlite3.connect(db))
        t["ts"] = pd.to_datetime(t.ts, unit="s"); st.dataframe(t.head(20)); st.line_chart(t.set_index("ts")[["pv_w", "load_w"]])
    else:
        st.write("No data/microgrid.db yet. The Node-RED flow creates it once the nodes publish.")
