# Community Microgrid Energy Forecasting
HCLTech BTech Learner Program · Embedded Systems & IoT · Vikas Raghav · v1.0

ESP32 sensing nodes → MQTT (HiveMQ, TLS) → Node-RED + SQLite → Python 24 h-ahead forecasting → Streamlit / Telegram / buzzer alerts.

> **Data note:** forecast results come from a 90-day *synthetic* dataset (simulation). Hardware bench results (tests HT-01…HT-10) are recorded separately in `docs/` once measured.

## Repository layout
```
firmware/common/   edge_logic.py (validate, average, stuck-sensor, SoC), net.py (Wi-Fi/MQTT TLS + back-off), ina219.py, bh1750.py, oled.py
firmware/node_a/   main.py, dht_reader.py, config.example.py     (PV + light + temp/humidity)
firmware/node_b/   main.py, battery.py, load_ctrl.py, alerts.py, config.example.py   (battery + load + local alerts)
nodered/flows.json ingest flow: MQTT-in → validate → SQLite + chart; alerts → Node B command
forecast/          generate_data.py, features.py, train.py, evaluate.py, dispatch.py, predict.py, notify.py
app/streamlit_app.py
tests/             test_edge_logic.py (UT-01..08), test_forecast.py (ST-01..07)
data/ outputs/ docs/
```

## Quick start (software, no hardware needed)
```bash
pip install -r requirements.txt
python forecast/generate_data.py      # writes data/synthetic_microgrid_hourly.csv (seed 42)
python forecast/train.py              # metrics -> outputs/results.json, outputs/test_predictions.csv
pytest -q                             # 15 tests
streamlit run app/streamlit_app.py    # dashboard
python forecast/predict.py            # next-24 h forecast (add --db data/microgrid.db --publish for live use)
```

## Hardware setup
1. Wire nodes per report Fig. 5.1 (I2C GPIO21/22; DHT22 GPIO4; divider GPIO34; MOSFET GPIO18; buzzer GPIO25; LEDs GPIO26/27).
2. Flash MicroPython on both ESP32s. Install `micropython-ssd1306` for the OLED (optional).
3. Copy `firmware/common/*` and the node folder to each board. Copy `config.example.py` → `config.py` and fill in Wi-Fi/HiveMQ values (git-ignored).
4. Create a HiveMQ Cloud cluster, add credentials for `nodeA`, `nodeB`, `nodered`, and use port 8883 (TLS). Inspect topics with MQTT Explorer.
5. Node-RED: install `node-red-node-sqlite` and `node-red-dashboard`, import `nodered/flows.json`, set broker host/credentials.
6. Hourly forecast job: `python forecast/predict.py --db data/microgrid.db --publish` (cron / Task Scheduler).

## Secrets
Only in `config.py` (git-ignored) or environment variables: `MQTT_HOST, MQTT_USER, MQTT_PASS, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID`.

## Notes
- MicroPython epoch is 2000-01-01; `net.unix_ts()` converts to Unix time for payloads.
- Telegram alerts are sent from `forecast/notify.py` (env-var secrets); Node-RED forwards alerts to Node B (buzzer/LED/load).
- Links (GitHub, live dashboard, demo video): see docs/LINKS.md. Live dashboard: https://claude.ai/artifact/52yFDMf3CPxrkyxTfP56wQ
