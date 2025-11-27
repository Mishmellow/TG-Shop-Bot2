import os
import json
from aiohttp import web

__app_id = os.environ.get("CANVAS_APP_ID", "default-app-id")
__firebase_config = os.environ.get("CANVAS_FIREBASE_CONFIG", "{}")
__initial_auth_token = os.environ.get("CANVAS_AUTH_TOKEN", "null")


class WebAppHandler(web.View):
    async def get(self):
        try:
            with open('web_app.html', 'r', encoding='utf-8') as f:
                html_content = f.read()

            script_variables = f"""
                <script>
                    const __app_id = '{__app_id}';
                    const __firebase_config = '{__firebase_config}';
                    const __initial_auth_token = '{__initial_auth_token}';
                </script>
            """
            html_content = html_content.replace(
                '<script type="module">',
                script_variables + '\n<script type="module">',
                1
            )

            return web.Response(
                text=html_content,
                content_type='text/html',
                headers={'Cache-Control': 'no-cache, no-store, must-revalidate'}
            )
        except FileNotFoundError:
            print("ERROR: web_app.html file not found in the root directory.")
            return web.Response(text="Error: web_app.html not found on the server.", status=500)
        except Exception as e:
            print(f"Server error in WebAppHandler: {e}")
            return web.Response(text=f"Server error: {e}", status=500)