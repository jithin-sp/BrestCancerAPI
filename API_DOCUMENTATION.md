# Breast Cancer Risk Prediction API Documentation

## Base URL
- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-render-url.onrender.com`

## Endpoints

### 1. Health Check
Check if the API is running and the model is loaded.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "model_loaded": true,
  "threshold": 0.5186692476272583,
  "feature_count": 19
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

---

### 2. Predict Risk
Predict breast cancer risk based on patient features.

**Endpoint**: `POST /predict`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "data": {
    "menopaus": 0,
    "agegrp": 1,
    "density": 3,
    "bmi": 2,
    "agefirst": 0,
    "nrelbc": 0,
    "brstproc": 0,
    "lastmamm": 0,
    "surgmeno": 0,
    "hrt": 0,
    "bmi_value": 27.5,
    "age_value": 37,
    "has_relatives": 0,
    "race_unknown": 0,
    "race_2": 0,
    "race_3": 0,
    "race_4": 0,
    "race_5": 0,
    "hisp_1": 0
  }
}
```

**Response**:
```json
{
  "probability": 0.3641417920589447,
  "label": 0,
  "threshold": 0.5186692476272583,
  "confidence": 0.6358582079410553,
  "feature_order": [
    "menopaus", "agegrp", "density", "bmi", "agefirst",
    "nrelbc", "brstproc", "lastmamm", "surgmeno", "hrt",
    "bmi_value", "age_value", "has_relatives", "race_unknown",
    "race_2", "race_3", "race_4", "race_5", "hisp_1"
  ]
}
```

**Response Fields**:
- `probability`: Risk probability (0.0 to 1.0)
- `label`: Risk classification (0 = Low Risk, 1 = High Risk)
- `threshold`: Decision threshold used for classification
- `confidence`: Confidence level of the prediction (0.0 to 1.0)
- `feature_order`: Order of features expected by the model

---

## Feature Descriptions

All features should be provided as numeric values (integers or floats):

| Feature | Description | Type |
|---------|-------------|------|
| `menopaus` | Menopausal status (coded) | int |
| `agegrp` | Age group (coded) | int |
| `density` | Breast density (coded) | int |
| `bmi` | BMI category (coded) | int |
| `agefirst` | Age at first birth (coded) | int |
| `nrelbc` | Number of relatives with breast cancer | int |
| `brstproc` | Previous breast procedure (coded) | int |
| `lastmamm` | Time since last mammogram (coded) | int |
| `surgmeno` | Surgical menopause (coded) | int |
| `hrt` | Hormone replacement therapy (coded) | int |
| `bmi_value` | Actual BMI value | float |
| `age_value` | Actual age value | float |
| `has_relatives` | Has relatives with breast cancer (0/1) | int |
| `race_unknown` | Race unknown indicator | int |
| `race_2` | Race category 2 | int |
| `race_3` | Race category 3 | int |
| `race_4` | Race category 4 | int |
| `race_5` | Race category 5 | int |
| `hisp_1` | Hispanic ethnicity indicator | int |

---

## Example Usage

### cURL
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "menopaus": 0,
      "agegrp": 1,
      "density": 3,
      "bmi": 2,
      "agefirst": 0,
      "nrelbc": 0,
      "brstproc": 0,
      "lastmamm": 0,
      "surgmeno": 0,
      "hrt": 0,
      "bmi_value": 27.5,
      "age_value": 37,
      "has_relatives": 0,
      "race_unknown": 0,
      "race_2": 0,
      "race_3": 0,
      "race_4": 0,
      "race_5": 0,
      "hisp_1": 0
    }
  }'
```

### JavaScript (Fetch API)
```javascript
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    data: {
      menopaus: 0,
      agegrp: 1,
      density: 3,
      bmi: 2,
      agefirst: 0,
      nrelbc: 0,
      brstproc: 0,
      lastmamm: 0,
      surgmeno: 0,
      hrt: 0,
      bmi_value: 27.5,
      age_value: 37,
      has_relatives: 0,
      race_unknown: 0,
      race_2: 0,
      race_3: 0,
      race_4: 0,
      race_5: 0,
      hisp_1: 0
    }
  })
});

const result = await response.json();
console.log(result);
```

### Python (requests)
```python
import requests

url = "http://localhost:8000/predict"
payload = {
    "data": {
        "menopaus": 0,
        "agegrp": 1,
        "density": 3,
        "bmi": 2,
        "agefirst": 0,
        "nrelbc": 0,
        "brstproc": 0,
        "lastmamm": 0,
        "surgmeno": 0,
        "hrt": 0,
        "bmi_value": 27.5,
        "age_value": 37,
        "has_relatives": 0,
        "race_unknown": 0,
        "race_2": 0,
        "race_3": 0,
        "race_4": 0,
        "race_5": 0,
        "hisp_1": 0
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## Error Responses

### 400 Bad Request - Unknown Features
```json
{
  "detail": "Unknown features in request: ['invalid_feature']"
}
```

### 400 Bad Request - Invalid Value
```json
{
  "detail": "Feature bmi_value could not be parsed as float: invalid"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Interactive Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to test the API directly from your browser.

---

## CORS Configuration

The API currently allows requests from any origin (`*`). For production, update the CORS settings in `app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

---

## Notes

- Missing features in the request will default to `0`
- All feature values are converted to floats internally
- Predictions are logged to `/tmp/request_log.csv` (configurable via `REQUEST_LOG` env variable)
- The model threshold is loaded from `model_metadata.json`
