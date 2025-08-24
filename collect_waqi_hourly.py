#!/usr/bin/env python3
import os, time, requests
from datetime import datetime, timezone
import pandas as pd

TOKEN = os.getenv("WAQI_TOKEN")
KEYWORD = os.getenv("WAQI_KEYWORD", "Bangkok")
MAX_STATIONS = int(os.getenv("WAQI_MAX_STATIONS", "20"))
OUT_CSV = os.getenv("WAQI_OUT", f"data/waqi_{datetime.utcnow().strftime('%Y-%m')}.csv")

def search_stations(keyword: str, token: str, max_n=20):
    url = f"https://api.waqi.info/search/?keyword={keyword}&token={token}"
    r = requests.get(url, timeout=20).json()
    data = []
    if r.get("status") == "ok":
        for it in r["data"]:
            st = it.get("station", {}) or {}
            uid = it.get("uid")
            if uid is None:
                continue
            country = st.get("country", "") or ""
            if "Thailand" in country or "ไทย" in country or country == "":
                data.append({
                    "uid": uid,
                    "station_name": st.get("name"),
                    "geo": st.get("geo"),
                    "aqi_snapshot": it.get("aqi"),
                })
    return pd.DataFrame(data).drop_duplicates("uid").head(max_n)

def fetch_station(uid: int, token: str):
    url = f"https://api.waqi.info/feed/@{uid}/?token={token}"
    r = requests.get(url, timeout=20).json()
    if r.get("status") != "ok":
        return None
    d = r["data"]
    iaqi = d.get("iaqi", {}) or {}
    def v(k):
        x = iaqi.get(k)
        return None if not isinstance(x, dict) else x.get("v")
    return {
        "uid": uid,
        "station_name": (d.get("city") or {}).get("name"),
        "time_iso": (d.get("time") or {}).get("s"),
        "aqi": d.get("aqi"),
        "pm25": v("pm25"),
        "pm10": v("pm10"),
        "o3":   v("o3"),
        "no2":  v("no2"),
        "so2":  v("so2"),
        "co":   v("co"),
        "temp": v("t"),
        "humidity": v("h"),
        "wind": v("w"),
        "pressure": v("p"),
        "ingested_at_utc": datetime.utcnow().isoformat(timespec="seconds")+"Z",
    }

def main():
    assert TOKEN, "Please set WAQI_TOKEN (e.g., via GitHub Secret)."
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    st_df = search_stations(KEYWORD, TOKEN, MAX_STATIONS)
    if st_df.empty:
        print("No stations found."); return
    rows = []
    for uid in st_df["uid"].tolist():
        try:
            rec = fetch_station(uid, TOKEN)
            if rec: rows.append(rec)
            time.sleep(0.2)
        except Exception as e:
            print("fetch error:", uid, e)
    if not rows:
        print("No data this round."); return
    df = pd.DataFrame(rows)
    if "time_iso" in df.columns:
        df["time"] = pd.to_datetime(df["time_iso"], errors="coerce", utc=True).dt.tz_convert("Asia/Bangkok")
        df = df.dropna(subset=["time"])
    write_header = not os.path.exists(OUT_CSV)
    df.to_csv(OUT_CSV, mode="a", header=write_header, index=False, encoding="utf-8")
    print(f"Appended {len(df)} rows to {OUT_CSV}")

if __name__ == "__main__":
    main()
