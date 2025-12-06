#!/usr/bin/env python3
"""
Manage Users Tool
Usage: python3 tools/manage_users.py [action] [args]

Actions:
  list                  List all users
  add_dev <id> <name>   Add a developer
  add_manager <id> <name> Add a manager
  get <id>              Get user details
  delete <id>           Delete a user
"""

import sys
import os
import argparse
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.operations import (
    create_user,
    get_user_by_telegram_id,
    get_all_users,
    delete_user,
    update_user
)
from config import ROLE_DEVELOPER, ROLE_MANAGER, ROLE_TEACHER, ROLE_LEADER, ROLE_STUDENT


def list_users():
    users = get_all_users()
    print(f"Found {len(users)} users:")
    for user in users:
        role_map = {1: 'Student', 2: 'Teacher', 3: 'Leader', 4: 'Manager', 5: 'Developer'}
        print(f"ID: {user.telegram_id} | Name: {user.name} | Role: {role_map.get(user.role, 'Unknown')} ({user.role})")


def add_user(telegram_id: int, name: str, role: int):
    print(f"Adding user {name} ({telegram_id}) with role {role}...")
    success, user, error = create_user(telegram_id, name, role)
    if success:
        print("✅ User created successfully.")
    else:
        print(f"❌ Error: {error}")


def get_user(telegram_id: int):
    user = get_user_by_telegram_id(telegram_id)
    if user:
        print(f"User Found:\n{user.__dict__}")
    else:
        print("User not found.")


def remove_user(telegram_id: int):
    print(f"Deleting user {telegram_id}...")
    success, error = delete_user(telegram_id)
    if success:
        print("✅ User deleted.")
    else:
        print(f"❌ Error: {error}")


def main():
    parser = argparse.ArgumentParser(description="Manage Telegram Bot Users (Redis)")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List
    parser_list = subparsers.add_parser("list", help="List all users")

    # Add Developer
    parser_add_dev = subparsers.add_parser("add_dev", help="Add a developer")
    parser_add_dev.add_argument("id", type=int, help="Telegram ID")
    parser_add_dev.add_argument("name", type=str, help="Name")

    # Add Manager
    parser_add_mgr = subparsers.add_parser("add_manager", help="Add a manager")
    parser_add_mgr.add_argument("id", type=int, help="Telegram ID")
    parser_add_mgr.add_argument("name", type=str, help="Name")

    # Get
    parser_get = subparsers.add_parser("get", help="Get user details")
    parser_get.add_argument("id", type=int, help="Telegram ID")

    # Delete
    parser_del = subparsers.add_parser("delete", help="Delete a user")
    parser_del.add_argument("id", type=int, help="Telegram ID")

    args = parser.parse_args()

    if args.command == "list":
        list_users()
    elif args.command == "add_dev":
        add_user(args.id, args.name, ROLE_DEVELOPER)
    elif args.command == "add_manager":
        add_user(args.id, args.name, ROLE_MANAGER)
    elif args.command == "get":
        get_user(args.id)
    elif args.command == "delete":
        remove_user(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    from database.connection import check_connection
    if check_connection():
        main()
    else:
        print("❌ Could not connect to Redis. Check credentials.")
