import webview
import os

# Get the absolute path of the HTML file to load 
current_directory = os.path.dirname(os.path.abspath(__file__))
html_file = f"file://{os.path.join(current_directory, 'landingScreen.html')}"

# Create a resizable window with specific dimensions
window = webview.create_window('Main Page', url=html_file, width=1200, height=800, resizable=True)
webview.start(http_server=True, private_mode=False) #loads the application, http_server is enabled to ensure commincation between server and client can occur and private_mode enables the exisistence of cookies) 

