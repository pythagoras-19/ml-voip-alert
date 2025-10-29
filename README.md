# ML VoIP Alert System

A cardiac risk prediction system that uses machine learning to assess patient risk scores and sends VoIP alerts via Asterisk AMI when high-risk cases are detected.

## Features

- **ML-based Risk Scoring**: Predicts cardiac risk using a trained scikit-learn model
- **SHAP Explanations**: Provides interpretable explanations for predictions
- **VoIP Alerts**: Sends voice alerts via Asterisk AMI Manager Interface
- **Cooldown Management**: Prevents alert spam with configurable cooldown periods
- **Redis Integration**: Optional Redis backend for persistent storage
- **Web Interface**: HTML case view for reviewing alerts

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ml-voip-alert
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and configure:
```bash
cp env.example .env
```

5. Train the model (or place your own in `models/` directory):
```bash
python models/train_heart_pipeline.py
```

## Configuration

Create a `.env` file with the following variables:

### Required
- `MODEL_PATH`: Path to your trained model file (default: `./models/heart_pipeline.joblib`)
- `RISK_THRESHOLD`: Risk score threshold for triggering alerts (default: `0.80`)

### Optional - Redis
- `REDIS_URL`: Redis connection URL (e.g., `redis://localhost:6379/0`)

### Optional - Asterisk AMI (for VoIP alerts)
- `ASTERISK_HOST`: Asterisk server hostname or IP
- `ASTERISK_PORT`: AMI port (default: `5038`)
- `ASTERISK_USER`: AMI username
- `ASTERISK_PASS`: AMI password
- `ALERT_CALL_NUMBER`: Phone number to call for alerts

### Optional - Alerts
- `COOLDOWN_MINUTES`: Minutes between alerts for the same patient (default: `30`)

## Usage

### Start the Server

Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Then start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or with reload for development:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Train the Model (.joblib)

Generate `models/heart_pipeline.joblib` with the provided training script:

```bash
python models/train_heart_pipeline.py
```

Notes:
- By default, it downloads the dataset from a public URL used in the notebook.
- You can override inputs/outputs via env vars:
  - `DATA_PATH=/path/to/heart.csv`
  - `MODEL_PATH=/absolute/or/relative/path/to/heart_pipeline.joblib`

### API Endpoints

#### POST `/score`
Score a patient for cardiac risk.

**Request:**
```json
{
  "patient_ref_token": "patient_123",
  "features": {
    "age": 65,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }
}
```

**Response:**
```json
{
  "risk": 0.85,
  "top_factors": [
    {"feature": "age", "impact": 0.15},
    {"feature": "cp", "impact": 0.12},
    {"feature": "oldpeak", "impact": 0.10}
  ],
  "alerted": true,
  "alert_id": "alrt_a1b2c3d4"
}
```

#### GET `/case/{token}`
View case details in HTML format.

#### GET `/health`
Health check endpoint.

#### GET `/`
API information and available endpoints.

## Architecture

- **`app/main.py`**: FastAPI application and endpoints
- **`app/deps.py`**: Model loading and dependency injection
- **`app/rules.py`**: Alert logic and cooldown checking
- **`app/notifier.py`**: VoIP notification via Asterisk AMI
- **`app/storage.py`**: Alert storage (Redis or in-memory)
- **`app/schemas.py`**: Pydantic models for API requests/responses
- **`app/shap_explain.py`**: SHAP-based explainability

## Alert System

The system triggers alerts when:
1. Risk score exceeds the configured threshold
2. Patient is not in cooldown period

When an alert is triggered:
1. Alert data is saved to storage
2. Cooldown period is set for the patient
3. VoIP call is initiated via Asterisk AMI (if configured)
4. Alert ID is returned for case tracking

## Storage Backend

The system supports two storage backends:
- **Redis**: Persists alerts and cooldowns across restarts
- **In-Memory**: Fallback when Redis is unavailable

## Security & Privacy

- Patient tokens are used instead of PHI
- Alert messages are PHI-free (only contain alert IDs)
- Model features should not contain PHI

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

The project uses:
- Type hints throughout
- Pydantic for data validation
- Proper error handling and logging

## License

[Add your license here]

