// ===============================
// 🌍 MULTI-LANGUAGE NLP DICTIONARY
// ===============================
const SYMPTOM_MAP = {
    fever: ["fever", "high", "temperature", "hot", "burning", "j্বর", "জ্বর", "jor", "bukhar"],
    cough: ["cough", "coughing", "throat", "কাশি", "kashi", "khasi"],
    headache: ["headache", "head", "migraine", "painhead", "মাথা", "matha", "mathabetha", "matha betha"],
    breathing: ["breathing", "shortness", "air", "chest", "tight", "শ্বাস", "shash", "shashkoshto"],
    fatigue: ["tired", "weak", "fatigue", "low energy", "দুর্বল", "durbol", "klanto"],
    vomiting: ["vomit", "throwing", "nausea", "sick", "বমি", "bomi"],
    rash: ["rash", "skin", "spots", "allergy", "চুলকানি", "chulkani"],
    diarrhea: ["loose", "motion", "diarrhea", "stomach", "পাতলা", "paykhana"],
    pain: ["pain", "ache", "hurt", "ব্যথা", "betha", "dard"],
    chestpain: ["chest pain", "buke betha", "buker betha", "chestpain", "বুকে ব্যথা"],
    allergy: ["allergy", "allargy", "chulkani", "চুলকানি", "khujli"] // 👈 নতুন অ্যালার্জি কি-ওয়ার্ড যুক্ত করা হলো
};

// ===============================
// TEXT PREPROCESSING (SAFE MULTI-LANGUAGE)
// ===============================
function preprocess(text) {
    return text
        .toLowerCase()
        .replace(/[^\u0980-\u09FFa-z\s]/g, " ") // Bangla + English allowed
        .replace(/\s+/g, " ")
        .trim();
}

// ===============================
// SMART SYMPTOM EXTRACTION (AI CORE)
// ===============================
function extractSymptoms(text) {
    let cleanedText = preprocess(text);
    let detected = [];

    // বাক্য বা ফ্রেজ সরাসরি চেক করা হচ্ছে যাতে "buke betha" বা "chulkani" নিখুঁতভাবে ধরা পড়ে
    for (let key in SYMPTOM_MAP) {
        for (let synonym of SYMPTOM_MAP[key]) {
            if (cleanedText.includes(synonym)) {
                if (!detected.includes(key)) {
                    detected.push(key);
                }
                break;
            }
        }
    }
    return detected; // এটি একটি Array রিটার্ন করবে
}

// ===============================
// PREGNANCY UI LOGIC
// ===============================
function checkPregnancy() {
    let gender = document.getElementById("gender").value;
    let pregnancyBox = document.getElementById("pregnancyBox");

    if (pregnancyBox) {
        if (gender === "female") {
            pregnancyBox.style.display = "block";
        } else {
            pregnancyBox.style.display = "none";
        }
    }
}

// ===============================
// 🎤 VOICE INPUT SYSTEM
// ===============================
function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US"; // browser limitation
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.start();

    recognition.onresult = function(event) {
        let voiceText = event.results[0][0].transcript;
        document.getElementById("userInput").value = voiceText;
    };

    recognition.onerror = function(event) {
        alert("Voice error: " + event.error);
    };
}

// ===============================
// 🚀 MAIN CHAT FUNCTION (SMART AI)
// ===============================
function sendMessage() {
    let rawText = document.getElementById("userInput").value;
    let age = document.getElementById("age").value;
    let gender = document.getElementById("gender").value;
    
    let pregnantElem = document.getElementById("pregnant");
    let pregnant = pregnantElem ? pregnantElem.value : "no";

    let resultBox = document.getElementById("result");

    if (rawText.trim() === "") {
        resultBox.innerHTML = "⚠ Please enter symptoms / দয়া করে উপসর্গ লিখুন";
        return;
    }

    // 🧠 NLP Processing
    let smartSymptoms = extractSymptoms(rawText);

    resultBox.innerHTML = "🧠 AI analyzing English + Bangla + Banglish...";

    fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            symptoms: smartSymptoms, // Array পাঠানো হচ্ছে
            age: age,
            gender: gender,
            pregnant: pregnant
        })
    })
    .then(res => res.json())
    .then(data => {
        if (typeof data.response === "string") {
            resultBox.innerHTML = `<p style="color: red; font-weight: bold;">${data.response}</p>`;
        } else {
            resultBox.innerHTML = `
                <h3>🧠 Possible Disease: ${data.response.disease}</h3>
                <p><b>Patient Type:</b> ${data.response.patient_type}</p>
                <p><b>Medicines:</b> ${data.response.medicines.join(", ")}</p>
            `;
        }
    })
    .catch(() => {
        resultBox.innerHTML = "❌ Server not running";
    });
}