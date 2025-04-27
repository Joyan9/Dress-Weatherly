# Dress-Weatherly™  
_"Es gibt kein schlechtes Wetter, nur falsche Kleidung."_

---

**Dress-Weatherly™** is an automated daily pipeline that fetches weather data, generates personalized outfit recommendations based on the forecast, and sends them to your email before you start your day! ☕👖🌧️



---

## 📅 Example Output

**Weather Summary for 2025-04-27**  
- Overall Temperature range: 15.0°C to 20.0°C (feels like 13.0°C to 18.0°C)  
- Morning (06–10): 12.0–18.0°C  
- Daytime (10–18): 18.0–20.0°C  
- Evening (18–24 & 00–06): 14.0–16.0°C  
- 🌧 No rain expected  
- 💨 Mild winds  

---

**Morning (06–10):**  
- Upper layer: Long-sleeve shirt or light sweater  
- Mid layer: None  
- Outer layer: None  
- Lower body: Regular pants or jeans  
- Accessories: None  

**Daytime (10–18):**  
- Upper layer: Light tee or shirt  
- Mid layer: None  
- Outer layer: Light jacket  
- Lower body: Light pants or skirt  
- Accessories: Sunglasses and sunscreen  

**Evening (18–24 & 00–06):**  
- Upper layer: Light sweater or fleece  
- Mid layer: None  
- Outer layer: Medium jacket (wind-resistant)  
- Lower body: Thick pants or jeans with thermal lining  
- Accessories: Windbreaker  

---

## 📦 Features
- Fetches hourly weather forecasts from the [Open-Meteo API](https://open-meteo.com/)
- Suggests clothing items for morning, daytime, and evening
- Adds weather-specific accessories like umbrellas, sunglasses, or windbreakers
- Sends daily outfit recommendations via email
- Runs automatically every morning with GitHub Actions
- Dockerized for easy deployment
- Includes unit and integration testing

---

## ⚙️ Tech Stack
- **Python 3.11**
- **DuckDB** – embedded database
- **dlt** – for data loading
- **Docker** – containerization
- **GitHub Actions** – CI/CD
- **Open-Meteo API** – weather data source

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Dress-Weatherly.git
cd Dress-Weatherly

# 2. Build Docker image
docker build -t dress-weatherly .

# 3. Run the pipeline
docker run --rm \
  -e SENDER_EMAIL=your_email@example.com \
  -e SENDER_APP_PASSWORD=your_app_password \
  dress-weatherly
```

_**Note:** You’ll need an app password from your email provider to send secure emails._

---

## 🛠 Project Structure

```
Dress-Weatherly/
├── .github/workflows/           # GitHub Actions for daily automation
├── data/                        # Local DuckDB database
├── scripts/                     # Main scripts
│   ├── fetch_weather.py         # Fetch weather forecast
│   ├── recommend_outfit.py      # Recommend outfits based on forecast
│   ├── send_notification.py     # Send email notifications
│   └── run_pipeline.py          # Main pipeline orchestrator
├── tests/                       # Unit and integration tests
├── Dockerfile                   # Docker container setup
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
└── README.md                    # You are here!
```

---

## 🧪 Testing

Run unit and integration tests easily:

```bash
pytest tests/
```

- `tests/unit/` — individual script testing
- Full pipeline integration testing available

---

## 📅 CI/CD Automation

- Scheduled **daily run at 6 AM UTC** via [GitHub Actions workflow](.github/workflows/dress-weatherly-run-pipeline.yml)
- Docker-based deployment for consistency across environments

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).

---

## 🔮 Future Goals
- Build a smarter recommendation engine using an LLM or lightweight model for weather-to-outfit matching
- Expand GitHub Actions to include CI workflows (unit testing + linting on PRs)
- Support multiple locations or travel outfit planning

---

## 👏 Acknowledgements
- [Open-Meteo](https://open-meteo.com/) for providing free weather API access
- Inspired by the German saying:  
  > _"Es gibt kein schlechtes Wetter, nur falsche Kleidung."_
- @dlthub for their amazing python library making extract-load super simple!

