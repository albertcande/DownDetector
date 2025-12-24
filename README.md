# 🔍 Down Detector - Multi-Service Monitoring System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-MVP-orange.svg" alt="Status">
</p>

A Python-based monitoring tool that tracks the status of multiple web services and sends real-time alerts via **Email** and **Slack** when outages or status changes are detected.

---

## ✨ Features

- **📊 Multi-Service Monitoring** - Track multiple services simultaneously
- **🔔 Dual Alerting** - Get notified via Email (Gmail SMTP) and Slack
- **🛡️ Cloudflare Bypass** - Uses undetected-chromedriver to handle protected pages
- **🎯 Flexible Detection** - Support for DownDetector and generic status pages
- **🔒 Secure Credentials** - Environment-based configuration keeps secrets safe
- **⚙️ Configurable** - Adjustable monitoring intervals and targets

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Google Chrome** (latest version recommended)
- **Git** (for cloning the repository)

You'll also need:

- A **Gmail account** with [App Password](https://myaccount.google.com/apppasswords) enabled
- (Optional) A **Slack workspace** with an [Incoming Webhook](https://api.slack.com/messaging/webhooks)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/albertcande/DownDetector.git
cd DownDetector
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# Windows: notepad .env
# macOS/Linux: nano .env
```

Fill in your credentials in the `.env` file:

```env
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECEIVERS=recipient1@example.com,recipient2@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 5. Run the Monitor

```bash
python monitor.py
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_SENDER` | ✅ Yes | - | Gmail address for sending alerts |
| `EMAIL_PASSWORD` | ✅ Yes | - | Gmail App Password |
| `EMAIL_RECEIVERS` | ✅ Yes | - | Comma-separated list of recipient emails |
| `SLACK_WEBHOOK_URL` | ❌ No | - | Slack Incoming Webhook URL |
| `CHECK_DELAY_BETWEEN_SITES` | ❌ No | `10` | Seconds between checking each site |
| `LOOP_DELAY` | ❌ No | `60` | Seconds between monitoring cycles |

### Monitoring Targets

Edit the `TARGETS` list in `config.py` to add or modify monitored services:

```python
TARGETS = [
    {
        "name": "Service Name",
        "url": "https://downdetector.com/status/service/",
        "mode": "downdetector"  # or "generic"
    },
    {
        "name": "API Status",
        "url": "https://status.example.com/",
        "mode": "generic",
        "good_keywords": ["operational", "all systems go"]
    }
]
```

#### Monitoring Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `downdetector` | Parses DownDetector.com pages | User-reported outage tracking |
| `generic` | Keyword-based status detection | Official status pages |

---

## 📁 Project Structure

```
DownDetector/
├── .env.example      # Environment variables template
├── .env              # Your credentials (DO NOT COMMIT!)
├── .gitignore        # Git ignore rules
├── config.py         # Configuration and targets
├── monitor.py        # Main monitoring script
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 🔒 Security Best Practices

1. **Never commit `.env`** - It's already in `.gitignore`
2. **Use App Passwords** - Don't use your main Gmail password
3. **Rotate credentials** - Periodically update your passwords
4. **Limit webhook access** - Use channel-specific Slack webhooks

---

## 📧 Gmail Setup

1. Go to your [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Navigate to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Copy the 16-character password to your `.env` file

---

## 💬 Slack Setup

1. Go to your [Slack App Directory](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Enable **Incoming Webhooks**
4. Click **Add New Webhook to Workspace**
5. Select the channel for alerts
6. Copy the Webhook URL to your `.env` file

---

## 🛠️ Troubleshooting

### "Chrome not found"

Ensure Google Chrome is installed and accessible in your system PATH.

### "Cloudflare blocking"

The tool uses `undetected-chromedriver` to bypass Cloudflare, but aggressive protection may still block requests. Try:
- Increasing the delay between checks
- Running during off-peak hours

### "Email authentication failed"

- Ensure you're using an **App Password**, not your regular Gmail password
- Verify 2-Step Verification is enabled on your Google account

### "Module not found"

Make sure your virtual environment is activated and dependencies are installed:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [DownDetector](https://downdetector.com/) for crowdsourced outage data
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) for Cloudflare bypass

---

<p align="center">
  Made with ❤️ by Albert
</p>



