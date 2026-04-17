# Intrusion Detection System

This documentation provides an in-depth overview of the project, including its purpose, how to use it, configuration details, available features, requirements, installation process, and guidelines for contributing.

---

## Introduction

Intrusion is a project focused on network security and behavioral threat detection. The repository features a real-time Intrusion Detection System (IDS) dashboard powered by a Random Forest machine learning classifier trained on the CICIDS2017 dataset. Its native Streamlit architecture allows users to employ lightning-fast mathematical detection methods for research, educational, or practical security purposes.

---

## Usage

To use the Intrusion Detection Engine, follow these steps:
- Clone the repository to your local machine (or host it directly on Streamlit Community Cloud).
- Set up the required environment as described in the Requirements and Installation sections.
- Execute the Streamlit UI to start analyzing offline network data.
- Upload a `.csv` packet capture file into the dashboard.
- Click **Initialize Threat Analysis** to seamlessly predict Malicious or Safe traffic in real-time.

---

## Configuration

Intrusion handles machine learning inference natively within the UI, significantly reducing configuration pain:
- **Automatic Caching**: The 39MB serialized Random Forest model (`rf_model.joblib`), scaler, and feature set are loaded internally into RAM using Streamlit `@st.cache_resource` for maximum speed.
- **Offline ML Tuning**: If you wish to retrain the algorithm boundaries or use a different dataset, run `train.py` directly. This will recalculate the SMOTE balancing and export fresh `.joblib` artifacts.

> [!IMPORTANT]
> The default model is designed to analyze 15 highly specific network features. Ensure your CSV uploads match the features natively logged in the CICIDS2017 schema.

---

## Features

Intrusion provides the following core features:
- **Network Traffic Analysis**: Analyze massive `.csv` network logs to detect suspicious activities (DDoS, Brute Force, Web Attacks).
- **Intrusion Detection Algorithms**: Implements a highly robust 100-tree Random Forest algorithm optimized for accuracy and low latency.
- **Native Web Interface**: Fully packaged, cinematic dark-themed Streamlit web interface removing the need for terminal interpretation.
- **Result Reporting**: Generates interactive Threat Distribution plots, high-confidence alerts, and natively exports classified reports back to CSV.
- **Cloud Ready**: Architecture optimized to be hosted natively on Streamlit Community Cloud without background server dependencies.

---

## Requirements

The following requirements must be met to use Intrusion:
- **Operating System**: Compatible with major platforms (Linux, Windows, macOS).
- **Python Version**: Python 3.8+ recommended.
- **Dependencies**: Install necessary Python packages via pip: `streamlit`, `scikit-learn`, `pandas`, `imbalanced-learn`, `plotly`, etc.

> [!NOTE]
> Training (`train.py`) requires significant RAM when applying SMOTE generation to massive network datasets.

---

## Installation

To install and set up Intrusion, follow these steps:

```steps
1. Clone the Repository | git clone https://github.com/AxonCodez/intrusion.git
2. Navigate to Project Directory | cd intrusion
3. Install Dependencies | pip install -r requirements.txt
4. Run the Engine | streamlit run app.py
5. Test Inference | Upload your network flow CSV to the local http://localhost:8501 dashboard
```

---

## Contributing

Contributions to Intrusion are welcome! To contribute:

- Fork the repository and create a new branch for your feature or fix.
- Make your changes following the coding style and guidelines in the repository.
- Write clear commit messages and update or add documentation as necessary.
- Submit a pull request describing your changes and their purpose.

> [!TIP]
> Please review any existing issues or discussion threads before starting new features. Ensure any ML feature alterations are logged.
