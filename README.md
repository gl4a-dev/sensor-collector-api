# sensor-collector-api

## Running Locally & Testing with Physical Devices

Follow these instructions to run the FastAPI server locally and allow physical mobile devices on the same Wi-Fi network to connect.

### Prerequisites & Environment Variables

Ensure your `.env` file is created at the root of the project:

```env
PORT=8000

# Database
DB_USER = database_user
DB_PASSWORD = database_password
DB_HOST = database_host
DB_NAME = database_name

# Google Auth
GOOGLE_CLIENT_ID = your_google_web_cliend_id
```

### Identify Your Computer's Local IP Address

To accept connections from a physical mobile device, the app must point to your machine's local IPv4 address instead of `localhost`.

* **Windows Command Prompt / PowerShell:**
```cmd
ipconfig
```

*Look for your active Wi-Fi or Ethernet adapter and copy the **IPv4 Address** (e.g., `192.168.1.15`).*

### Start the FastAPI Server

Run `uvicorn` bound to `0.0.0.0`. Binding to `0.0.0.0` tells the server to listen on all available network interfaces rather than locking traffic strictly to `127.0.0.1`.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> **Note (Windows Firewall):** If prompted by Windows Defender Firewall when launching Uvicorn, check **Allow access on Private networks**.

### Verify Network Connectivity

1. Ensure both your computer and physical mobile device are connected to the **same Wi-Fi network**.
2. Open the mobile browser on your device and navigate to:
```text
http://<YOUR_LOCAL_IP>:8000/
```
3. You should receive the JSON health payload confirming the connection is established:
```json
{
    "message": "Sensor Collector API is running."
}
```

### Flutter `.env` Configuration

Configure your Flutter app's `.env` file to point directly to your local workstation IP:

```env
BACKEND_URL=http://<YOUR_LOCAL_IP>:8000
GOOGLE_SERVER_CLIENT_ID=your_google_web_client_id.apps.googleusercontent.com
```