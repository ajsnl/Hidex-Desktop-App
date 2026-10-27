# HideX Pro 🔐
### Image Steganography Tool — MCA Mini Project

> **Hide secret text messages inside PNG images using LSB Steganography, protected with AES-256 encryption.**

---

## 📌 What is Steganography?

Steganography is the practice of hiding secret information within an ordinary, non-secret file so that it cannot be detected by an outside observer. Unlike cryptography (which scrambles data), steganography **conceals the very existence** of the message.

**HideX Pro** combines both:
- **LSB Steganography** — hides data in the least significant bits of image pixels (invisible to the human eye)
- **AES-256 Fernet Encryption** — encrypts the message before embedding, so even if extracted, it is unreadable without the correct password

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔒 **Hide Message** | Embed an encrypted secret message into any PNG image |
| 🔓 **Reveal Message** | Extract and decrypt the hidden message from a stego image |
| 🔐 **AES-256 Encryption** | Password-based encryption using Python `cryptography.fernet` |
| 👁 **Password Toggle** | Show/Hide password field for easy input |
| 📊 **Capacity Indicator** | Live display of how many characters the image can hold |
| 📋 **Copy to Clipboard** | Copy the revealed message with one click |
| 🗑 **Clear All** | Reset the entire interface instantly |
| 🖼 **Image Preview** | Preview selected image with filename and dimensions |
| 🚦 **Character Counter** | Live counter that warns when nearing or exceeding capacity |
| 🟢 **Status Bar** | Colour-coded feedback for every operation |

---



## ⚙️ Requirements

- Python 3.8 or higher
- The following Python packages:

```
stegano
cryptography
Pillow
```

---

## 🚀 Installation & Setup

### 1. Clone or Download the Project

```bash
# Download the project folder or clone via git
git clone <your-repo-url>
cd Hidex
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv env
```

### 3. Activate the Virtual Environment

```bash
# Windows (PowerShell)
.\env\Scripts\Activate.ps1

# Windows (Command Prompt)
.\env\Scripts\activate.bat

# macOS / Linux
source env/bin/activate
```

### 4. Install Dependencies

```bash
pip install stegano cryptography Pillow
```

### 5. Run the Application

```bash
python HideX_Pro.py
```

Or directly using the venv Python (without activating):

```bash
.\env\Scripts\python.exe HideX_Pro.py
```

---

## 📖 How to Use

### 🔒 Hiding a Message

1. **Launch** the app — `python HideX_Pro.py`
2. Click **"Select PNG Image"** and choose any `.png` file
3. Check the **capacity indicator** — it shows how many characters the image can hold
4. Type your **secret message** in the text box
5. Enter a **strong password** in the password field
6. Click **"Hide Message"**
7. A **Save dialog** will appear — save the output image (e.g., `stego_output.png`)
8. Share the saved image — the message is invisible inside it!

### 🔓 Revealing a Message

1. Click **"Select PNG Image"** and choose the **stego image** (output from step 7 above)
2. Enter the **same password** used when hiding
3. Click **"Reveal Message"**
4. The hidden message appears in a **popup window**
5. Use **"Copy to Clipboard"** to copy it

> ⚠️ **Important:** You must use the exact same password to reveal the message. Wrong password = decryption fails.

---

## 🔐 How the Security Works

```
Your Message  ──►  AES-256 Fernet Encrypt  ──►  Encrypted Token
                        (using Password)

Encrypted Token  ──►  LSB Embed into PNG pixels  ──►  Stego Image

Stego Image  ──►  LSB Extract  ──►  Encrypted Token
                                         │
                               AES-256 Fernet Decrypt
                                  (using Password)
                                         │
                                  Original Message ✅
```

### Why is this secure?

- The **password is never stored** anywhere — not in the image, not on disk
- The message is **AES-256 encrypted** before embedding, so even if someone extracts the LSB data, they only see an unreadable encrypted blob
- Only someone with the **correct password** can decrypt the message
- `cryptography.Fernet` raises an `InvalidToken` error on a wrong password — preventing any partial reads

---

## ⚠️ Important Notes

| Rule | Reason |
|---|---|
| ✅ Use **PNG only** | PNG is lossless — JPEG compression destroys LSB data |
| ✅ Share the **saved output image** | The original image is NOT modified |
| ✅ Remember your **password** | It cannot be recovered if forgotten |
| ❌ Do NOT convert to JPEG | It will destroy the hidden message permanently |
| ❌ Do NOT screenshot the image | Screenshots re-encode pixels and destroy the data |

---

## 📂 Project Structure

```
Hidex/
├── HideX_Pro.py       ← Main application (upgraded version)
├── projectversion1.txt          ← Original version (basic)
├── README.md          ← This file
├── hidden.png         ← Sample stego image
├── logo.png           ← App logo
├── env/               ← Python virtual environment
│   └── Scripts/
│       ├── python.exe
│       └── pip.exe
└── presentation.pptx  ← Project presentation
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3** | Core programming language |
| **Tkinter** | GUI framework (built into Python) |
| **Pillow (PIL)** | Image loading, thumbnail, and display |
| **stegano** | LSB steganography (hide/reveal) |
| **cryptography (Fernet)** | AES-256 symmetric encryption |
| **hashlib** | SHA-256 password → encryption key derivation |
| **ttk (Tkinter)** | Themed widgets (scrollbar, separator) |

---


## 🐞 Known Limitations

- Only **PNG** images are supported (by design — JPEG is lossy)
- Very **small images** have low capacity (a 100×100px image holds ~3,700 characters)
- The app requires a **local Python installation** — it is a desktop app, not a web app
- No support for hiding **files or images** — text only

---



---

## 👨‍🎓 About This Project

- **Project Name:** HideX Pro — Image Steganography Tool  
- **Course:** Master of Computer Applications (MCA)  
- **Type:** Mini Project  
- **Topic:** Cybersecurity / Data Hiding / Information Security  
- **Technique:** LSB (Least Significant Bit) Steganography  

---

## 📄 License

This project is created for academic purposes as part of the MCA curriculum.

---

*Built with ❤️ using Python*
