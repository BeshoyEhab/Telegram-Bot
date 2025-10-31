# =============================================================================
# FILE: test_telegram_connection.py
# DESCRIPTION: Test Telegram API connection and bot token
# LOCATION: Project root directory
# PURPOSE: Diagnose connection issues with Telegram
# USAGE: python test_telegram_connection.py
# =============================================================================

"""
Test script to verify Telegram connection and bot token.
"""

import sys
import asyncio
import httpx
from config import BOT_API


async def test_connection():
    """Test connection to Telegram API."""
    
    print("=" * 60)
    print("TELEGRAM CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Test 1: Check token format
    print("1. Checking bot token format...")
    if not BOT_API:
        print("   ❌ BOT_API not set in .env")
        return False
    
    if not BOT_API or len(BOT_API) < 40:
        print(f"   ❌ Invalid token format: {BOT_API[:10]}...")
        print("   Token should be like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        return False
    
    print(f"   ✅ Token format looks valid: {BOT_API[:10]}...")
    print()
    
    # Test 2: Test internet connectivity
    print("2. Testing internet connection...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.telegram.org")
            print(f"   ✅ Can reach Telegram API (status: {response.status_code})")
    except httpx.ConnectTimeout:
        print("   ❌ Connection timeout - Internet/firewall issue")
        print("   Possible causes:")
        print("      - No internet connection")
        print("      - Firewall blocking Telegram")
        print("      - Telegram blocked in your region")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    print()
    
    # Test 3: Test bot token with getMe
    print("3. Testing bot token with Telegram API...")
    url = f"https://api.telegram.org/bot{BOT_API}/getMe"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("   Sending request to Telegram...")
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    print("   ✅ Bot token is VALID!")
                    print()
                    print("   Bot Information:")
                    print(f"      ID: {bot_info.get('id')}")
                    print(f"      Username: @{bot_info.get('username')}")
                    print(f"      Name: {bot_info.get('first_name')}")
                    print(f"      Can Join Groups: {bot_info.get('can_join_groups')}")
                    print(f"      Can Read Messages: {bot_info.get('can_read_all_group_messages')}")
                    return True
                else:
                    print(f"   ❌ API returned error: {data.get('description')}")
                    return False
            elif response.status_code == 401:
                print("   ❌ Invalid bot token (401 Unauthorized)")
                print("   Please check your BOT_API in .env")
                return False
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except httpx.ConnectTimeout:
        print("   ❌ Connection timeout (30 seconds)")
        print("   This usually means:")
        print("      - Telegram is blocked in your region")
        print("      - You need to use a VPN")
        print("      - Firewall is blocking the connection")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print()


async def test_send_message():
    """Test sending a message (optional)."""
    print()
    print("4. Would you like to test sending a message? (y/n): ", end="")
    
    try:
        choice = input().strip().lower()
        if choice != 'y':
            return True
        
        print()
        print("   Enter your Telegram ID to send a test message: ", end="")
        chat_id = input().strip()
        
        if not chat_id.isdigit():
            print("   ❌ Invalid Telegram ID")
            return False
        
        url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "🤖 Test message from Telegram School Bot!\n\nIf you see this, the bot is working correctly! ✅"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                print("   ✅ Test message sent successfully!")
                print("   Check your Telegram to confirm.")
                return True
            else:
                data = response.json()
                print(f"   ❌ Failed to send message: {data.get('description')}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def main():
    """Run all tests."""
    success = await test_connection()
    
    if success:
        await test_send_message()
    
    print()
    print("=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("Your bot is ready to run!")
        print("Start it with: python main.py")
    else:
        print("❌ TESTS FAILED")
        print("=" * 60)
        print()
        print("Troubleshooting steps:")
        print("1. Check .env file has correct BOT_API token")
        print("2. Get token from @BotFather in Telegram")
        print("3. Check internet connection")
        print("4. Try using a VPN if Telegram is blocked")
        print("5. Check firewall settings")
    print()
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
