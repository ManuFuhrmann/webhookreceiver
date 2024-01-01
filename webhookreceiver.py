import os
import sys
import subprocess
import configparser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

def load_config_variables():
  config = configparser.ConfigParser()
  config.read('config.ini')

  # Get the values of the variables
  global PORT
  PORT = int(config.get('Variables', 'PORT'))

  global HOME_DIR
  HOME_DIR = config.get('Variables', 'HOME_DIR')

class RequestHandler(BaseHTTPRequestHandler):
  def do_POST(self):
    self.send_response(200)
    self.end_headers()

    query = parse_qs(urlparse(self.path).query)
    repo_name = query['repo_name'][0]
    branch_name = query['branch_name'][0]

    repo_path = f"{HOME_DIR}{repo_name}/{branch_name}"
    os.chdir(repo_path)

    # Check if the repository folder exists and is a git repository
    if not os.path.exists(repo_path):
      self.wfile.write(f"Repository folder not found: {repo_path}".encode())
      return
  
    try:
      subprocess.check_output(['git', 'rev-parse', '--is-inside-work-tree'])
    except subprocess.CalledProcessError as e:
      self.wfile.write(f"Error: {repo_path} is not a git repository: {str(e)}".encode())
      return
  
    try:
      subprocess.check_output(['git', 'pull'])
      if os.path.exists('post.sh'):
        subprocess.check_output(['bash', 'post.sh'])
    except subprocess.CalledProcessError as e:
      self.wfile.write(f"Error occurred while pulling changes or executing post.sh script: {str(e)}".encode())

if __name__ == '__main__':
  load_config_variables()
  server_address = ('', PORT)
  httpd = HTTPServer(server_address, RequestHandler)
  print(f"Serving on {server_address[0]}:{server_address[1]}")
  httpd.serve_forever()
