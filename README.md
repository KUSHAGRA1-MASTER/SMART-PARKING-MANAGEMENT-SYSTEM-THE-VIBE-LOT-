# 🚗 SMART PARKING MANAGEMENT SYSTEM (THE VIBE LOT)

A comprehensive Flask-based parking management system featuring real-time bay tracking, vehicle classification, automated billing, discounted monthly subscriptions, and remote IP/GPS tracking via ngrok tunneling.

---

## 🌟 Key Features

* **Real-Time Bay Tracking:** Live visual status grid monitoring available, occupied, and vehicle-tagged bays.
* **Vehicle Classification:** Dedicated allocation logic for 2-Wheelers and 4-Wheelers with custom slot assignments[cite: 4, 5].
* **Flexible Billing Engine:** 
  * Standard hourly rates (₹10 base + ₹5/hr for 2-Wheelers; ₹20 base + ₹10/hr for 4-Wheelers).
  * Flat monthly subscription passes (₹300/mo for 2-Wheelers; ₹1,000/mo for 4-Wheelers)[cite: 5].
* **Input Validation:** Strict validation checks for 10-digit mobile numbers and Indian RTO vehicle number formats[cite: 5].
* **Attendant Console & Ledger:** Real-time parking lot management dashboard and historical financial reporting[cite: 1, 3].
* **Network & Geolocation Tracking:** 
  * Exposed local development ports over public HTTPS using **ngrok tunneling**.
  * Visitor IP identification via `X-Forwarded-For` HTTP header parsing.
  * Precise GPS tracking using HTML5 Geolocation API with Google Maps link generation.

---

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask, SQLite3[cite: 5]
* **Frontend:** HTML5, CSS3 (Glassmorphism Dark Theme), JavaScript[cite: 2, 4]
* **Networking & Tools:** ngrok, Git, VS Code

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3 installed on your machine.

### 2. Installation & Setup
Clone the repository and navigate into the project directory:
```bash
git clone [https://github.com/KUSHAGRA1-MASTER/SMART-PARKING-MANAGEMENT-SYSTEM-THE-VIBE-LOT-.git](https://github.com/KUSHAGRA1-MASTER/SMART-PARKING-MANAGEMENT-SYSTEM-THE-VIBE-LOT-.git)
cd SMART-PARKING-MANAGEMENT-SYSTEM-THE-VIBE-LOT-/"parking system"
