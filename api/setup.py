from http.server import BaseHTTPRequestHandler
import os
import json
import urllib.request
from urllib.error import URLError

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request to setup webhook."""
        
        # Get configuration
        bot_token = os.environ.get('BOT_API')
        webhook_url = os.environ.get('WEBHOOK_URL')
        
        # Validate config
        if not bot_token:
            self.send_error(500, "BOT_API environment variable not set")
            return
            
        if not webhook_url:
            self.send_error(500, "WEBHOOK_URL environment variable not set")
            return
            
        # Construct webhook URL
        # Ensure webhook_url doesn't have trailing slash and api path fits
        base_url = webhook_url.rstrip('/')
        target_url = f"{base_url}/api/webhook"
        
        # Telegram API URL
        telegram_api = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={target_url}"
        
        try:
            # Send request to Telegram
            with urllib.request.urlopen(telegram_api) as response:
                result = response.read().decode('utf-8')
                
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(result.encode('utf-8'))
            
        except URLError as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = json.dumps({"error": str(e), "url": target_url})
            self.wfile.write(error_msg.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = json.dumps({"error": str(e)})
            self.wfile.write(error_msg.encode('utf-8'))
