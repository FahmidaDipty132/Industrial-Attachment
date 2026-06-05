from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ===============================
# 🧠 SEARCH HISTORY (CHAT MEMORY)
# ===============================
search_history = []

# ===============================
# 🚨 EMERGENCY KEYWORDS
# ===============================
EMERGENCY = [
    "heart attack", "stroke", "unconscious", "severe bleeding", "chestpain"
]

# ===============================
# 🧠 MEDICAL DATABASE (AI READY)
# ===============================
medical_data = {
    "Flu": {
        "symptoms": ["fever", "cough", "headache", "fatigue", "pain"],
        "adult_medicine": ["Paracetamol", "Cough Syrup", "Vitamin C", "Rest"],
        "child_medicine": ["Child Paracetamol Syrup", "Honey", "Warm fluids"],
        "pregnant_medicine": ["Paracetamol (safe dose)", "Rest", "Hydration"]
    },

    "Cold": {
        "symptoms": ["cough", "pain"],
        "adult_medicine": ["Antihistamine", "Steam inhalation", "Warm water"],
        "child_medicine": ["Saline drops", "Warm soup"],
        "pregnant_medicine": ["Steam inhalation", "Warm fluids"]
    },

    "Dengue": {
        "symptoms": ["fever", "rash", "pain", "fatigue"],
        "adult_medicine": ["Paracetamol", "ORS", "Hydration"],
        "child_medicine": ["Child Paracetamol", "ORS"],
        "pregnant_medicine": ["Hospital consultation", "IV fluids"]
    },

    "Migraine": {
        "symptoms": ["headache", "vomiting"],
        "adult_medicine": ["Paracetamol", "Ibuprofen", "Rest in dark room"],
        "child_medicine": ["Child Paracetamol", "Rest"],
        "pregnant_medicine": ["Paracetamol (safe dose)", "Rest"]
    },

    "Diabetes": {
        "symptoms": ["fatigue"],
        "adult_medicine": ["Doctor consultation", "Insulin check", "Diet control"],
        "child_medicine": ["Hospital checkup", "Diet control"],
        "pregnant_medicine": ["Doctor consultation", "Glucose monitoring"]
    },

    "Hypertension": {
        "symptoms": ["headache", "fatigue"],
        "adult_medicine": ["Amlodipine", "Lifestyle change"],
        "child_medicine": ["Doctor consultation"],
        "pregnant_medicine": ["Hospital monitoring"]
    },

    "Asthma": {
        "symptoms": ["breathing", "cough"],
        "adult_medicine": ["Inhaler", "Bronchodilator"],
        "child_medicine": ["Pediatric inhaler"],
        "pregnant_medicine": ["Inhaler (safe)", "Doctor supervision"]
    },

    "Food Poisoning": {
        "symptoms": ["vomiting", "diarrhea", "pain", "fever"],
        "adult_medicine": ["ORS", "Hydration"],
        "child_medicine": ["ORS", "Fluids"],
        "pregnant_medicine": ["Hospital care", "ORS"]
    },

    "COVID": {
        "symptoms": ["fever", "cough", "fatigue"],
        "adult_medicine": ["Paracetamol", "Rest", "Isolation"],
        "child_medicine": ["Child Paracetamol"],
        "pregnant_medicine": ["Doctor supervision"]
    },

    "Allergy": {  # 👈 সম্পূর্ণ নতুন অ্যালার্জি ক্যাটাগরি এবং এর মেডিসিন যোগ করা হলো
        "symptoms": ["allergy"],
        "adult_medicine": ["Antihistamine (Fexofenadine / Cetirizine)", "Calamine Lotion", "Avoid allergen"],
        "child_medicine": ["Cetirizine Syrup (Doctor dose)", "Calamine Lotion"],
        "pregnant_medicine": ["Loratadine (Consult doctor first)", "Calamine Lotion"]
    }
}

# ===============================
# 🚀 API ROUTE
# ===============================
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}

    symptoms_list = data.get("symptoms", [])
    
    try:
        age = int(data.get("age", 0)) if data.get("age") else 0
    except ValueError:
        age = 0
        
    gender = data.get("gender", "").lower()
    pregnant = data.get("pregnant", "no").lower()

    # ===============================
    # 🚨 EMERGENCY CHECK
    # ===============================
    if any(word in symptoms_list for word in EMERGENCY):
        return jsonify({
            "response": "⚠ Emergency detected! Go to hospital immediately."
        })

    # ===============================
    # 🤰 PREGNANCY CHECK
    # ===============================
    if gender != "female" or not (18 <= age <= 35):
        pregnant = "no"

    # ===============================
    # 🧠 SAVE HISTORY
    # ===============================
    search_history.append({
        "symptoms": symptoms_list,
        "age": age,
        "gender": gender
    })

    if len(search_history) > 5:
        search_history.pop(0)

    # ===============================
    # 🧠 DISEASE MATCHING
    # ===============================
    best_match = None
    best_score = 0

    for disease, info in medical_data.items():
        score = 0
        for symptom in symptoms_list:
            if symptom in info["symptoms"]:
                score += 1

        if score > best_score:
            best_score = score
            best_match = disease
        # বিশেষ চেক: যদি ইউজার শুধু অ্যালার্জি ইনপুট দেয় এবং তার জ্বর (fever) না থাকে, তবে প্রায়োরিটি Allergy পাবে (Dengue নয়)
        elif score == best_score and disease == "Allergy" and "fever" not in symptoms_list:
            best_match = disease

    # ===============================
    # ❌ LOW CONFIDENCE CHECK
    # ===============================
    if best_score < 1:
        return jsonify({
            "response": "⚠ Symptoms not clear. Please describe more clearly."
        })

    # ===============================
    # 💊 MEDICINE SELECTION
    # ===============================
    if 0 < age <= 12:
        medicines = medical_data[best_match]["child_medicine"]
        patient_type = "Child"
    elif gender == "female" and pregnant == "yes":
        medicines = medical_data[best_match]["pregnant_medicine"]
        patient_type = "Pregnant Woman"
    else:
        medicines = medical_data[best_match]["adult_medicine"]
        patient_type = "Adult"

    # ===============================
    # ✅ RESPONSE
    # ===============================
    return jsonify({
        "response": {
            "disease": best_match,
            "confidence": best_score,
            "patient_type": patient_type,
            "medicines": medicines
        },
        "history": search_history
    })

if __name__ == "__main__":
    app.run(debug=True)