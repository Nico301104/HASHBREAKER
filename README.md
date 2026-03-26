# 🔐 HASHBREAKER

## 📌 Overview
HASHBREAKER is a project focused on understanding cryptographic hash functions and how input data is transformed into fixed-length hash outputs.

The project is built for learning purposes and helps demonstrate how hashing works, how different algorithms behave, and how small changes in input completely change the output.

## 🎯 Goals
- Understand how hash functions work
- Experiment with hashing algorithms
- Observe the avalanche effect
- Compare hash outputs for different inputs
- Learn basic cybersecurity and cryptography concepts

## ⚙️ Features
- Generate hash values from custom input
- Support for multiple hashing algorithms (depending on implementation)
- Compare outputs easily
- Simple command-line interface (CLI)
- Lightweight and easy to extend

## 🧠 Key Concepts
- Cryptographic hash functions
- One-way functions (non-reversible)
- Deterministic outputs
- Avalanche effect
- Data integrity verification

## 🛠️ Technologies Used
- Python (main language)
- hashlib or equivalent standard libraries
- CLI-based execution

## 🚀 How to Run
1. Clone the repository:
git clone https://github.com/Nico301104/HASHBREAKER.git

2. Enter the folder:
cd HASHBREAKER

3. Run the project:
python main.py

## 📁 Project Structure
HASHBREAKER/
├── constants.py

├── engine.py

├── gui.py

├── hash_utils.py
├── main.py

├── wordlist.txt
└── README.md
## 📌 Example
Input: hello
Output: SHA256 hash generated from input

Small change:
Input: hEllo
Output: completely different hash result (avalanche effect)
## 👤 Author
* Sandru Nicolae-Andrei
