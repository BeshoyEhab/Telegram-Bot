import os
import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler
from telegram import Update
from main import create_application
import config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize application
# We do this at module level to potential caching by Vercel's warm containers
# However, asyncio loop management is tricky in serverless
application = create_application()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request (Telegram updates)."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            json_string = post_data.decode('utf-8')
            
            # Parse update
            update_data = json.loads(json_string)
            
            # Process update in an async loop
            # We create a new loop for each request to avoid loop closed errors
            # in the ephemeral environment if reused improperly
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def process():
                # Verify DB connection (important for serverless cold start)
                # Note: main.py init_db() handles the table creation if needed
                # Ideally, we assume DB is ready or handled by lightweight check
                
                # Initialize bot
                if not application.running:
                     await application.initialize()
                
                # Create update object
                update = Update.de_json(update_data, application.bot)
                
                # Process
                await application.process_update(update)
                
                # Cleanup (optional, but good for serverless if not reused)
                # await application.shutdown() 
            
            loop.run_until_complete(process())
            loop.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}", exc_info=True)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"status": "error"}')

    def do_GET(self):
        """Simple health check."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Telegram Bot Webhook is running!")
