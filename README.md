# WhatsApp Desktop Automation Sender & Batch Messenger

Lightweight automation engine for batch WhatsApp messaging on Windows, leveraging the native `whatsapp://send` protocol URI handler, **Win32 API** window management, low-level hardware scan-code injection, and anti-spam jitter pacing without heavy Selenium or Chromium browser overhead.

[![Live Simulator](https://img.shields.io/badge/Live%20Simulator-Vercel-10B981?style=flat&logo=vercel)](https://wa-desktop-automation.vercel.app)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20(Win32%20API)-0078D6.svg)](https://docs.microsoft.com/en-us/windows/win32/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Live Web Simulator

- **Browser Simulation Interface**: [https://wa-desktop-automation.vercel.app](https://wa-desktop-automation.vercel.app)

## Technical Architecture

```
                    +---------------------------+
                    |    Input Dataset (CSV/XLSX)
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    | Dynamic Template Compiler |
                    | ({name}, {dept}, {role})  |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |   Protocol Dispatcher     |
                    |  (whatsapp://send?phone)  |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |    Win32 Window Manager   |
                    | Focus window & ScanCode   |
                    | (Hardware Key Event 0x1C) |
                    +-------------+-------------+
                                  |
                                  v
                    +---------------------------+
                    |   Jitter Delay & Logger   |
                    |  (Random 15-25s sleep)    |
                    +---------------------------+
```

## Key Capabilities

- **Native Protocol URI Handling**: Dispatches messages directly via `whatsapp://send?phone=<phone>&text=<encoded_text>`, bypassing heavy headless browser frameworks (Selenium, Puppeteer, Playwright) and cutting memory footprint by >90%.
- **Low-Level Hardware Key Injection**: Leverages the Win32 API (`user32.dll`) to detect window handles, bring WhatsApp Desktop to the foreground, and inject raw hardware keyboard scan codes (`0x1C` for Enter key).
- **Dynamic Variable Substitution**: Compiles templates with contextual metadata (`{nama}`, `{panggilan}`, `{divisi}`, `{instansi}`) loaded from spreadsheet sources (CSV or XLSX).
- **Anti-Spam Delay Pacing**: Randomized jitter delays (configurable between 15–25 seconds) mimicking human interaction to mitigate automated rate-limiting.
- **De-duplication & Audit Trail**: Thread-safe logging to `sent_log.csv` ensuring zero double-sends upon restart or failure recovery.
- **Safe Dry-Run Mode**: Interactive sandbox simulator (`demo.py`) verifying pipeline logic, data parsing, and template syntax without dispatching live messages.

## Quickstart

### Prerequisites

- Windows 10 / 11
- Python 3.10+
- WhatsApp Desktop installed from official release

### Installation & Run

1. Clone the repository:
   ```bash
   git clone https://github.com/zakski-bit/wa-desktop-automation.git
   cd wa-desktop-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run dry-run simulation (Safe test mode):
   ```bash
   python demo.py
   ```

4. Run live batch sender:
   ```bash
   python main.py
   ```

## Repository Structure

```
├── main.py                  # Production batch automation runner
├── demo.py                  # Interactive dry-run terminal simulator
├── index.html               # Web demo client for Vercel deployment
├── app.js                   # Client-side workflow simulator
├── kontak_sample.csv        # Template input dataset schema
├── requirements.txt         # Python dependencies
└── sent_log.csv             # Execution history & deduplication ledger
```

## License

MIT License. See [LICENSE](LICENSE) for details.
