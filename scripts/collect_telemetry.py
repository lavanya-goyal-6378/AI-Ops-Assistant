import sys
import os
import csv
import time

# Allow imports from src/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from telemetry import get_live_telemetry


LABELS = [
    "BENIGN",
    "DDoS",
    "DoS",
    "PortScan",
    "CAM_Overflow"
]

FEATURES = [
    "flow_duration",
    "fwd_pkt_count",
    "bwd_pkt_count",
    "mean_pkt_size",
    "iat_mean",
    "pps",
    "flood_score",
    "mac_fill",
    "new_mac_rate",
    "syn_count"
]


label = input(
    "Enter traffic label "
    "(BENIGN/DDoS/DoS/PortScan/CAM_Overflow): "
).strip()

if label not in LABELS:
    print("Invalid label.")
    print("Choose one of:", LABELS)
    sys.exit(1)


num_samples = int(input("How many samples to collect? "))

output_dir = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data"
)

os.makedirs(output_dir, exist_ok=True)

filename = os.path.join(
    output_dir,
    f"{label.lower()}_telemetry.csv"
)


print()
print(f"Collecting {num_samples} samples for: {label}")
print(f"Output: {filename}")
print("Press Ctrl+C to stop.")
print()


with open(filename, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=FEATURES + ["label"]
    )

    writer.writeheader()

    for i in range(num_samples):

        telemetry = get_live_telemetry()

        row = {
            feature: telemetry.get(feature, 0)
            for feature in FEATURES
        }

        row["label"] = label

        writer.writerow(row)

        print(
            f"[{i + 1}/{num_samples}] "
            f"pps={row['pps']:.2f} "
            f"flood={row['flood_score']:.3f} "
            f"mac={row['mac_fill']:.3f}"
        )

        time.sleep(1)


print()
print("Collection complete!")
print(f"Saved to: {filename}")