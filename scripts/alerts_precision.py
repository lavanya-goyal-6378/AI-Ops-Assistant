
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sklearn.metrics import confusion_matrix, classification_report

from telemetry import simulate_attack, get_live_telemetry
from detector import AnomalyDetector


# Initialize detector
detector = AnomalyDetector()

TP = 0
FP = 0
TN = 0
FN = 0

# Store actual and predicted labels
y_true = []
y_pred = []


# -----------------------------
# Test attack traffic
# -----------------------------

attacks = [
    "ddos",
    "dos",
    "portscan",
    "camoverflow"
]
attack_results = {
    "ddos": {"TP": 0, "FN": 0},
    "dos": {"TP": 0, "FN": 0},
    "portscan": {"TP": 0, "FN": 0},
    "camoverflow": {"TP": 0, "FN": 0}
}

# Test each attack 10 times
for attack in attacks:
    for _ in range(10):

        telemetry = simulate_attack(attack)
        result = detector.predict(telemetry)

        actual_attack = True
        predicted_attack = result["is_alert"]

        # Store labels
        y_true.append(1)
        y_pred.append(1 if predicted_attack else 0)

        if predicted_attack:
            TP += 1
            attack_results[attack]["TP"] += 1
        else:
            FN += 1
            attack_results[attack]["FN"] += 1


# -----------------------------
# Test benign traffic
# -----------------------------

for _ in range(40):

    telemetry = get_live_telemetry()
    result = detector.predict(telemetry)

    actual_attack = False
    predicted_attack = result["is_alert"]

    # Store labels
    y_true.append(0)
    y_pred.append(1 if predicted_attack else 0)

    if predicted_attack:
        FP += 1
    else:
        TN += 1


# -----------------------------
# Calculate Precision
# -----------------------------

precision = TP / (TP + FP) if (TP + FP) > 0 else 0

# Calculate Recall
recall = TP / (TP + FN) if (TP + FN) > 0 else 0

# Calculate F1
f1 = (
    2 * precision * recall / (precision + recall)
    if (precision + recall) > 0
    else 0
)


# -----------------------------
# Print Results
# -----------------------------

print("\nAlert Detection Results")
print("-----------------------")

print(f"TP: {TP}")
print(f"FP: {FP}")
print(f"TN: {TN}")
print(f"FN: {FN}")

print(f"\nPrecision: {precision:.4f}")
print(f"Precision: {precision * 100:.2f}%")

print(f"\nRecall: {recall:.4f}")
print(f"Recall: {recall * 100:.2f}%")

print(f"\nF1 Score: {f1:.4f}")
print(f"F1 Score: {f1 * 100:.2f}%")


# -----------------------------
# Confusion Matrix
# -----------------------------

cm = confusion_matrix(y_true, y_pred)

print("\nConfusion Matrix")
print("----------------")
print(cm)

print("\nConfusion Matrix Meaning")
print("------------------------")
print("                 Predicted")
print("                 Normal  Attack")
print(f"Actual Normal      {cm[0][0]:<6} {cm[0][1]}")
print(f"Actual Attack      {cm[1][0]:<6} {cm[1][1]}")


# -----------------------------
# Classification Report
# -----------------------------

print("\nClassification Report")
print("---------------------")

print(
    classification_report(
        y_true,
        y_pred,
        target_names=["Normal", "Attack"],
        zero_division=0
    )
)
print("\nAttack-wise Results")
print("-------------------")

for attack, result in attack_results.items():
    total = result["TP"] + result["FN"]
    recall = result["TP"] / total if total > 0 else 0

    print(
        f"{attack:12} "
        f"TP: {result['TP']:2} "
        f"FN: {result['FN']:2} "
        f"Recall: {recall * 100:.2f}%"
    )