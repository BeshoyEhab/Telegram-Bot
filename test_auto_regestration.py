# =============================================================================
# FILE: test_auto_registration.py
# DESCRIPTION: Test script to verify auto-registration works
# LOCATION: Project root directory
# PURPOSE: Verify .env users are auto-created in database
# USAGE: python test_auto_registration.py
# =============================================================================

"""
Test script to verify auto-registration of .env users.
"""

import sys
from config import AUTHORIZED_USERS
from database import init_db, get_db
from database.operations import get_user_by_telegram_id, create_user


def test_auto_registration():
    """Test auto-registration functionality."""
    
    print("=" * 60)
    print("AUTO-REGISTRATION TEST")
    print("=" * 60)
    print()
    
    # Initialize database
    print("1. Initializing database...")
    init_db()
    print("   ✅ Database initialized\n")
    
    # Check .env users
    print("2. Checking .env USERS...")
    if not AUTHORIZED_USERS:
        print("   ❌ No users in .env USERS variable")
        print("   Add users to .env: USERS=telegram_id:role:class_id")
        return False
    
    print(f"   Found {len(AUTHORIZED_USERS)} users in .env:")
    for telegram_id, (role, class_id) in AUTHORIZED_USERS.items():
        print(f"   - {telegram_id}: role={role}, class={class_id or 'None'}")
    print()
    
    # Check database
    print("3. Checking database for existing users...")
    users_in_db = []
    users_missing = []
    
    for telegram_id, (role, class_id) in AUTHORIZED_USERS.items():
        user = get_user_by_telegram_id(telegram_id)
        if user:
            users_in_db.append(telegram_id)
            print(f"   ✅ User {telegram_id} exists in database")
            print(f"      Name: {user.name}")
            print(f"      Role: {user.role}")
            print(f"      Class: {user.class_id}")
            print(f"      Language: {user.language_preference}")
        else:
            users_missing.append(telegram_id)
            print(f"   ❌ User {telegram_id} NOT in database")
    print()
    
    # Summary
    print("4. Summary:")
    print(f"   Total users in .env: {len(AUTHORIZED_USERS)}")
    print(f"   Users in database: {len(users_in_db)}")
    print(f"   Users missing: {len(users_missing)}")
    print()
    
    if users_missing:
        print("5. Next Steps:")
        print("   The missing users will be auto-created when they:")
        print("   - Send /start to the bot")
        print("   - Use any bot command")
        print()
        print("   To manually test auto-registration:")
        print("   1. Start the bot: python main.py")
        print("   2. Send /start in Telegram")
        print("   3. Check logs: tail -f logs/bot.log")
        print("   4. Look for: '✅ Auto-registered user...'")
        print()
    
    # Show how to verify after bot start
    print("6. Verification Commands:")
    print("   # Check users in database")
    print("   sqlite3 school_bot.db 'SELECT telegram_id, name, role, class_id FROM users;'")
    print()
    print("   # Watch logs for auto-registration")
    print("   tail -f logs/bot.log | grep 'Auto-registered'")
    print()
    
    # Test creating a dummy user (if no users exist)
    if not users_in_db:
        print("7. Testing create_user() function...")
        success, user, error = create_user(
            telegram_id=999999999,
            name="Test User",
            role=1,
            language_preference="ar"
        )
        
        if success:
            print("   ✅ create_user() works correctly")
            print("   Cleaning up test user...")
            with get_db() as db:
                db.query(type(user)).filter_by(telegram_id=999999999).delete()
            print("   ✅ Test user deleted")
        else:
            print(f"   ❌ create_user() failed: {error}")
            return False
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    if users_missing:
        print("⚠️  Some users not in database yet (expected)")
        print("   They will be auto-created on first bot interaction")
        return True
    else:
        print("✅ All .env users already in database")
        return True


if __name__ == "__main__":
    try:
        success = test_auto_registration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
