# Connection Troubleshooting Guide

Your bot is experiencing connection timeout errors when trying to reach Telegram servers.

---

## 🐛 The Error

```
httpx.ConnectTimeout
RuntimeError: ExtBot is not properly initialized
```

**Meaning:** The bot cannot connect to Telegram API servers.

---

## 🔍 Diagnosis Steps

### Step 1: Test Your Connection

Run the connection test script:

```bash
python test_telegram_connection.py
```

This will check:
- ✅ Bot token format
- ✅ Internet connectivity
- ✅ Telegram API accessibility
- ✅ Bot token validity

---

### Step 2: Verify Bot Token

```bash
# Test manually with curl
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Replace <YOUR_TOKEN> with your actual token from .env
```

**Expected response (if valid):**
```json
{
  "ok": true,
  "result": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "YourBot",
    "username": "your_bot_username"
  }
}
```

**If you get 401 Unauthorized:**
- Token is invalid or expired
- Get new token from @BotFather

---

### Step 3: Check Internet Connection

```bash
# Test general internet
ping google.com

# Test Telegram specifically
ping api.telegram.org

# Test HTTPS access
curl -I https://api.telegram.org
```

**If ping fails:**
- No internet connection
- DNS issues
- Network configuration problem

---

### Step 4: Check if Telegram is Blocked

**Regions where Telegram may be blocked:**
- China
- Iran
- Russia (partially)
- Some corporate networks

**Test:**
```bash
# Try accessing Telegram web
curl https://web.telegram.org

# If this times out, Telegram is likely blocked
```

---

## ✅ Solutions

### Solution 1: Fix Bot Token (If Invalid)

1. Open Telegram
2. Search for **@BotFather**
3. Send `/mybots`
4. Select your bot
5. Click "API Token"
6. Copy the new token
7. Update `.env`:
   ```env
   BOT_API=123456789:NEW_TOKEN_HERE
   ```

---

### Solution 2: Use VPN (If Telegram is Blocked)

If Telegram is blocked in your region:

```bash
# Install and configure VPN
# Then restart bot
python main.py
```

**Recommended VPNs for Development:**
- ProtonVPN (free tier available)
- Windscribe
- TunnelBear

---

### Solution 3: Use Proxy (Alternative to VPN)

Update `main.py` to use a proxy:

```python
from telegram.request import HTTPXRequest

# Add proxy configuration
request = HTTPXRequest(
    proxy_url="http://proxy.example.com:8080",  # Your proxy
    connection_pool_size=8,
    connect_timeout=30.0,
    read_timeout=30.0,
)

application = (
    Application.builder()
    .token(config.BOT_API)
    .request(request)
    .build()
)
```

**SOCKS5 Proxy:**
```python
request = HTTPXRequest(
    proxy_url="socks5://127.0.0.1:1080",
    connection_pool_size=8,
)
```

---

### Solution 4: Increase Timeouts (Slow Connection)

Already included in the fixed `main.py`:

```python
request = HTTPXRequest(
    connect_timeout=30.0,  # Increased from 5.0
    read_timeout=30.0,     # Increased from 5.0
    write_timeout=30.0,
    pool_timeout=30.0
)
```

This helps if your connection is slow but working.

---

### Solution 5: Check Firewall

**Linux:**
```bash
# Check if firewall is blocking
sudo iptables -L

# Allow HTTPS (port 443)
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
```

**Windows:**
```powershell
# Check firewall
Get-NetFirewallRule | Where-Object {$_.Direction -eq "Outbound"}

# Or disable temporarily to test
# (Not recommended for production)
```

**macOS:**
```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

---

### Solution 6: Use Different Network

Try connecting from:
- Different WiFi network
- Mobile hotspot
- University/office network (if not blocked there)
- Public WiFi (with VPN for security)

---

## 🚀 Quick Fixes

### Fix 1: Update main.py with Better Timeouts

Copy the fixed `main.py` from artifact `main_py_connection_fix`.

Key changes:
- Increased connection timeouts to 30 seconds
- Added `post_init` to verify connection
- Better error messages
- Drops pending updates on start

---

### Fix 2: Test Without Starting Full Bot

```python
# test_simple.py
import asyncio
from telegram import Bot
from config import BOT_API

async def test():
    bot = Bot(token=BOT_API)
    async with bot:
        me = await bot.get_me()
        print(f"✅ Bot: @{me.username}")

asyncio.run(test())
```

Run:
```bash
python test_simple.py
```

If this works but `main.py` doesn't, the issue is in the application setup.

---

## 📋 Checklist

Go through this checklist:

- [ ] Verified bot token is correct in `.env`
- [ ] Tested token with curl (got valid response)
- [ ] Internet connection working (can ping google.com)
- [ ] Can reach api.telegram.org (curl test passes)
- [ ] Not behind corporate firewall blocking Telegram
- [ ] Telegram not blocked in my region (or using VPN)
- [ ] Copied updated `main.py` with longer timeouts
- [ ] Ran `test_telegram_connection.py` (all tests pass)

---

## 🎯 Most Common Causes

### 1. Telegram is Blocked (50%)
**Symptom:** Connection timeout specifically to api.telegram.org

**Solution:** Use VPN

---

### 2. Invalid Bot Token (30%)
**Symptom:** 401 Unauthorized error or connection refused

**Solution:** Get new token from @BotFather

---

### 3. Firewall Blocking (15%)
**Symptom:** All HTTPS connections fail or specific ports blocked

**Solution:** Configure firewall or use different network

---

### 4. Network Issues (5%)
**Symptom:** All internet connections slow/failing

**Solution:** Check internet connection, restart router

---

## 🔧 Advanced Debugging

### Enable Debug Logging

In `config.py`:
```python
LOG_LEVEL = "DEBUG"
DEBUG = True
```

Restart bot and check logs:
```bash
tail -f logs/bot.log
```

### Check Python HTTPX Version

```bash
pip show httpx
pip show python-telegram-bot
```

Required versions:
- httpx >= 0.24.0
- python-telegram-bot >= 20.0

### Test with Different HTTP Client

```python
# In requirements.txt
httpx==0.27.0
python-telegram-bot==22.5
```

Then:
```bash
pip install -r requirements.txt --upgrade
```

---

## 📞 Need More Help?

If none of these solutions work:

1. **Share your test results:**
   ```bash
   python test_telegram_connection.py > test_results.txt
   ```

2. **Check Telegram Status:**
   - Visit: https://downdetector.com/status/telegram/

3. **Try Example Bot:**
   ```python
   # minimal_test.py
   import asyncio
   from telegram import Bot
   
   async def main():
       bot = Bot("YOUR_TOKEN")
       async with bot:
           print(await bot.get_me())
   
   asyncio.run(main())
   ```

4. **System Information:**
   - OS: `uname -a` (Linux/Mac) or `ver` (Windows)
   - Python: `python --version`
   - Location/Country
   - ISP/Network provider

---

## ✅ After Fixing

Once connection works:

1. Run auto-registration test:
   ```bash
   python test_auto_registration.py
   ```

2. Start bot:
   ```bash
   python main.py
   ```

3. Send `/start` in Telegram

4. Check logs:
   ```bash
   tail -f logs/bot.log | grep "Auto-registered"
   ```

---

**Most likely cause based on your error:** Telegram is blocked in your region or network. Try using a VPN.
