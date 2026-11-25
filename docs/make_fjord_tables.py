"""Make the four fjord practice tables of simplydata (src/simplydata/data/fjord_*.csv): MADE-UP data with a real mess.

One made-up sampling cruise in a made-up fjord, 12 to 14 May 2026: water samples at eight stations, qPCR results for
four antibiotic resistance genes, the stations themselves, and a logger in the water. Every value is drawn here from a
fixed seed; nothing is copied from a real study. The tables are messy on purpose, in the ways real files are messy, so
that each cleaning word of simplydata has a real mess to fix in its examples and lessons:

- fjord_samples: sample_id stored as a number (7), while the lab writes "007"; station names typed with a space at the
  end ("St.3 "), in other capitals ("st.3"), and one with the "å" of "Råvika" typed as "a" plus a combining ring (it
  looks the same but is other characters); the crew of each sample as one cell with names separated by ";".
- fjord_lab: one row per sample and gene; sample_id is zero-padded text ("007"); one sample (23) has no lab result;
  one ID was mistyped ("141" for sample 41, one gene); copies per ml are text with "<LOD" and "n.d."; lab codes
  such as "3-12" and "2/4" are the kind a spreadsheet turns into dates; 6 rows were pasted twice; 2 rows and
  the column "checked_by" are completely empty, as a spreadsheet export leaves them.
- fjord_stations: column names as a spreadsheet writes them ("Latitude (°N)", "Distance to outfall (km)").
- fjord_logger: a temperature and oxygen logger, every 10 minutes in UTC (the samples are in local time, UTC+2).

Run once from the repository root: python docs/make_fjord_tables.py. It writes the same files on every computer.
"""

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "src" / "simplydata" / "data"
SEED = 20261125
GENES = ["sul1", "tetM", "blaOXA-48", "intI1"]
# station, fjord, latitude, longitude, distance from the outfall in km (all made up)
STATIONS = [
    ("St.1", "Inner fjord", 60.412, 5.318, 0.4),
    ("St.2", "Inner fjord", 60.405, 5.301, 1.1),
    ("St.3", "Inner fjord", 60.398, 5.287, 2.0),
    ("St.4", "Middle fjord", 60.389, 5.262, 3.6),
    ("St.5", "Middle fjord", 60.377, 5.240, 5.2),
    ("Råvika", "Middle fjord", 60.366, 5.219, 6.9),
    ("St.7", "Outer fjord", 60.351, 5.190, 9.4),
    ("St.8", "Outer fjord", 60.334, 5.158, 12.8),
]
CREW = ["AH", "KL", "MS", "TO", "IB"]


def fjord_stations():
    return pd.DataFrame(STATIONS, columns=["Station", "Fjord", "Latitude (°N)", "Longitude (°E)",
                                           "Distance to outfall (km)"])


def fjord_samples(seed=SEED):
    """60 water samples: 8 stations, 2 or 3 depths, over three days, in local time (UTC+2)."""
    rng = np.random.default_rng(seed)
    rows = []
    days = ["2026-05-12", "2026-05-13", "2026-05-14"]
    sample = 0
    for day_number, day in enumerate(days):
        start = pd.Timestamp(f"{day} 08:30")
        for place, (station, _, _, _, distance) in enumerate(STATIONS):
            depths = [1, 10] if day_number == 1 else [1, 10, 30]
            if day_number == 2 and place % 2:
                depths = [1, 10]
            for depth in depths:
                sample += 1
                if sample > 60:
                    break
                minutes = int(place * 40 + depths.index(depth) * 12 + rng.integers(0, 6))
                salinity = 20 + 1.0 * distance + 0.15 * depth + rng.normal(0, 0.6)
                crew = rng.choice(CREW, size=int(rng.integers(1, 4)), replace=False)
                rows.append({"sample_id": sample, "station": station, "sampled_local": start + pd.Timedelta(minutes=minutes),
                             "depth_m": depth, "salinity": round(float(salinity), 1), "crew": ";".join(crew),
                             "notes": ""})
    frame = pd.DataFrame(rows[:60])
    # the mess of hand-typed station names
    frame.loc[frame["sample_id"] == 8, "station"] = "St.3 "
    frame.loc[frame["sample_id"] == 30, "station"] = "st.3"
    frame.loc[frame["sample_id"] == 46, "station"] = "St.3 "
    decomposed = "Råvika"  # looks like Råvika, but is "a" followed by a combining ring
    frame.loc[frame["sample_id"] == 37, "station"] = decomposed
    frame.loc[frame["sample_id"] == 12, "notes"] = "bottle cracked, refilled"
    frame.loc[frame["sample_id"] == 23, "notes"] = "sample lost in transport"
    frame.loc[frame["sample_id"] == 51, "notes"] = "strong current"
    frame["sampled_local"] = frame["sampled_local"].dt.strftime("%Y-%m-%d %H:%M")
    return frame


def fjord_lab(samples, seed=SEED + 1):
    """qPCR results: one row per sample and gene, copies per ml as the lab writes them."""
    rng = np.random.default_rng(seed)
    distance = {s[0]: s[4] for s in STATIONS}
    level = {"sul1": 4.2, "tetM": 3.1, "blaOXA-48": 1.6, "intI1": 3.8}  # log10 copies per ml at the outfall
    rows = []
    for _, sample in samples.iterrows():
        if sample["sample_id"] == 23:  # lost in transport: never analysed
            continue
        name = sample["station"].strip().lower().replace("å", "å").replace("st.", "St.")
        name = "Råvika" if name.lower() == "råvika" else name
        plate = 1 + (sample["sample_id"] - 1) // 24
        well = 1 + (sample["sample_id"] - 1) % 24
        code = f"{plate}/{well}" if plate == 2 else f"{plate}-{well}"
        for gene in GENES:
            log_copies = level[gene] - 0.22 * distance[name] - 0.01 * sample["depth_m"] + rng.normal(0, 0.25)
            ct = round(float(38.5 - 3.32 * log_copies + rng.normal(0, 0.2)), 2)
            if log_copies < 0.9:
                copies, ct_value = "n.d.", None
            elif log_copies < 1.4:
                copies, ct_value = "<LOD", ct
            else:
                copies, ct_value = str(int(round(10 ** log_copies, -1))), ct
            rows.append({"sample_id": f"{sample['sample_id']:03d}", "lab_code": code, "gene": gene,
                         "copies_per_ml": copies, "ct": ct_value, "checked_by": None})
    frame = pd.DataFrame(rows)
    frame.loc[(frame["sample_id"] == "041") & (frame["gene"] == "tetM"), "sample_id"] = "141"  # a 1 typed twice
    repeats = frame.iloc[[17, 18, 90, 91, 150, 200]]  # pasted twice
    blank = pd.DataFrame([{c: None for c in frame.columns}] * 2)
    frame = pd.concat([frame.iloc[:60], blank.iloc[:1], frame.iloc[60:180], repeats, frame.iloc[180:], blank.iloc[1:]],
                      ignore_index=True)
    return frame


def fjord_logger(seed=SEED + 2):
    """A logger at St.4, 10 m deep, every 10 minutes in UTC over the three cruise days."""
    rng = np.random.default_rng(seed)
    time = pd.date_range("2026-05-12 00:00", "2026-05-14 23:50", freq="10min")
    hours = (time - time[0]).total_seconds().to_numpy() / 3600
    tide = np.sin(2 * np.pi * hours / 12.42)
    temperature = 8.4 + 0.02 * hours + 0.35 * tide + rng.normal(0, 0.05, len(time))
    oxygen = 9.1 - 0.15 * tide - 0.003 * hours + rng.normal(0, 0.04, len(time))
    return pd.DataFrame({"time_utc": time.strftime("%Y-%m-%d %H:%M"), "temperature": np.round(temperature, 2),
                         "oxygen": np.round(oxygen, 2)})


if __name__ == "__main__":
    samples = fjord_samples()
    tables = {"fjord_samples": samples, "fjord_lab": fjord_lab(samples), "fjord_stations": fjord_stations(),
              "fjord_logger": fjord_logger()}
    for name, frame in tables.items():
        frame.to_csv(OUT / f"{name}.csv", index=False, lineterminator="\n", encoding="utf-8")
        print(f"wrote {OUT / name}.csv ({len(frame)} rows)")
