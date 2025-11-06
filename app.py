from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import subprocess
import os
from whitenoise import WhiteNoise  # <--- IMPORT IT HERE

app = Flask(__name__, static_folder='static', template_folder='templates')
# IMPORTANT: Change this secret key!
app.secret_key = 'your-very-secret-random-key-here'

# --- ADD THIS LINE ---
# This "wraps" your app and tells it how to serve files from the 'static' folder
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='static/')
# ---------------------

# --- SECRET FLAGS & PASSWORDS ---
# (You can change these to whatever you want)
LEVEL_1_MORSE_CODE = "Morse Code is Fun"
LEVEL_4_LOGIC_FLAG = "djfajdiu348d8r"
LEVEL_5_PASSWORD = "you_are_the_key_to_this_puzzle" # The password from the Level 5 Caesar shift
LEVEL_6_MEMORY_FLAG = "keep in mind that we will ask for these flags at the end: 10v3_Y0R$3lF" # Revealed after winning memory game
LEVEL_7_AUDIO_FLAG = "life_is_easy_do_not_compicate_it" # The flag hidden in the audio file
LEVEL_8_PCAP_FLAG = "Y0u_Re4lly_Came_Th1s_F4r_Y0u_Des3rve_A_Fl4g" # The flag found in the pcap file
# ---------------------------------


DEFAULT_CODE = """

encoded = "dSIifSFHPDxvI3RvfCN7Iic7ciByeydybnRyIDpxeDt5diRyPCJyIHp2e255"

decoded_bytes = base64.b64decode(encode)
rot_text = decoded_bytes.decode('utf-8')

def rot_n(s, n=13):
    out = []
    for ch in s:
        if 32 <= ord(ch) <= 126:
            out.append(chr((ord(ch) - 32 - n) % 95 + 32)) 
        else:
            out.append(ch)
    return ''.join(out)

flag = rot_(rot_text, 13)
print("FLAG:", fla)
"""

# keep track of the current running process
running_proc = None

# A dummy filesystem tree
FS = {}
# Create 40 dummy directories
for i in range(1, 41):
    dirname = f"dir_{i}"
    FS[dirname] = {}

# Inject the final clue in one random directory
FS["dir_27"]["secret96.txt"] = "you might want to go to the next level.?? visit  bugbounty.erenyeager-dk.live/logic_gate  "
FS ["dir_14"]["secret.txt"] = "You got fooled! Try harder."
FS["dir_16"]["secret2.txt"] = "You got fooled again! Try harderrr."
FS["dir_19"]["secret3.txt"] = "I would have given up if i were you lol."


# --- LEVEL 1: MORSE CODE ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('code', '').strip().lower() == LEVEL_1_MORSE_CODE.lower():
            return redirect(url_for('compiler'))
    return render_template('index.html')

# --- LEVEL 2: PYTHON DEBUGGING ---
@app.route('/compiler', methods=['GET', 'POST'])
def compiler():
    global running_proc
    code = DEFAULT_CODE
    output = ""
    if request.method == 'POST':
        action = request.form.get('action')
        code = request.form.get('code') or DEFAULT_CODE

        # write user code to a temp file
        tmp = os.path.join(os.getcwd(), 'temp_code.py')
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(code)

        if action == 'run':
            try:
                # launch process
                running_proc = subprocess.Popen(
                    ['python', tmp],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                out, _ = running_proc.communicate(timeout=5)
                output = out
            except subprocess.TimeoutExpired:
                if running_proc:
                    running_proc.kill()
                output = 'Error: Execution timed out.'
            except Exception as e:
                output = str(e)
        elif action == 'stop':
            if running_proc and running_proc.poll() is None:
                running_proc.kill()
                output = 'Process stopped by user.'
    return render_template('compiler.html', code=code, output=output)

# --- LEVEL 3: WEB TERMINAL ---
@app.route('/terminal', methods=['GET', 'POST'])
def terminal():
    if 'cwd' not in session:
        session['cwd'] = []
        session['history'] = []
    cwd = session['cwd']
    history = session['history']
    output = ""

    def resolve_path(cwd_list):
        node = FS
        for part in cwd_list:
            node = node.get(part, {})
        return node

    def tree(node, indent=0):
        lines = []
        for name, content in sorted(node.items()):
            lines.append("  " * indent + "|-- " + name)
            if isinstance(content, dict):
                lines.extend(tree(content, indent + 1))
        return lines

    if request.method == 'POST':
        cmd = request.form.get('command', '').strip()
        parts = cmd.split()
        if not parts:
            return redirect(url_for('terminal'))

        if 'rm' in parts[0]:
            output = "rm is disabled for safety. Try something less destructive 😅"
        elif parts[0] == 'ls':
            node = resolve_path(cwd)
            output = '  '.join(sorted(node.keys())) or ''
        elif parts[0] == 'cd':
            target = parts[1] if len(parts) > 1 else ''
            if target == '..':
                if cwd: cwd.pop()
            elif target in resolve_path(cwd):
                if isinstance(resolve_path(cwd)[target], dict):
                    cwd.append(target)
                else:
                    output = f"cd: not a directory: {target}"
            else:
                output = f"cd: no such file or directory: {target}"
        elif parts[0] == 'cat':
            fname = parts[1] if len(parts) > 1 else ''
            node = resolve_path(cwd)
            if fname in node and isinstance(node[fname], str):
                output = node[fname]
            else:
                output = f"cat: {fname}: No such file"
        elif parts[0] == 'nano':
            fname = parts[1] if len(parts) > 1 else ''
            node = resolve_path(cwd)
            node[fname] = "(You opened nano editor. Enter new text and save next time 😄)"
            output = f"Opened '{fname}' in nano (simulated)."
        elif parts[0] == 'tree':
            node = resolve_path(cwd)
            output = '\n'.join(tree(node))
        elif parts[0] == 'help':
            output = (
                "Supported commands:\n"
                "  ls      - List directory\n"
                "  cd DIR  - Change directory\n"
                "  cat FILE - View file contents\n"
                "  nano FILE - Simulate editing\n"
                "  tree    - View directory structure\n"
                "  help    - Show this help\n"
                "  (rm is disabled)"
            )
        else:
            output = f"{parts[0]}: command not found"

        history.append((cwd.copy(), cmd, output))
        session['cwd'] = cwd
        session['history'] = history

    prompt = '/' + '/'.join(cwd) if cwd else '/'
    return render_template('terminal.html', history=history, prompt=prompt)

# --- LEVEL 4: LOGIC QUIZ ---
@app.route('/logic_gate', methods=['GET', 'POST'])
def quiz():
    message = ""
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip()
        if answer == LEVEL_4_LOGIC_FLAG:
            # **MODIFIED**
            # Instead of redirecting, show the clue for the offline Level 5
            message = "🎉 Congratulations! CLUE: Find the QR code hidden in the room."
        else:
            message = "Incorrect answer. Try again!"

    return render_template('quiz.html', message=message)

# --- LEVEL 5 (GATE) -> LEVEL 6 (GAME) ---
# This is the page the Level 5 QR/Caesar clue redirects to.
@app.route('/level6_gate', methods=['GET', 'POST'])
def level6_gate():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == LEVEL_5_PASSWORD:
            session['level6_unlocked'] = True
            return redirect(url_for('level6_memory_game'))
        else:
            error = "Incorrect Password. Try again."
    return render_template('level5_gate.html', error=error)

@app.route('/level6_memory_game')
def level6_memory_game():
    # Ensure user passed the password gate
    if not session.get('level6_unlocked'):
        return redirect(url_for('level6_gate'))
    return render_template('level6_memory.html', flag=LEVEL_6_MEMORY_FLAG)

# --- LEVEL 7: AUDIO CHALLENGE ---
@app.route('/level7_audio', methods=['GET', 'POST'])
def level7_audio():
    message = ""
    if request.method == 'POST':
        if request.form.get('flag', '').strip() == LEVEL_7_AUDIO_FLAG:
            session['level7_unlocked'] = True
            return redirect(url_for('level8_pcap'))
        else:
            message = "Incorrect Flag. Analyze the audio again."
    return render_template('level7_audio.html', message=message)

# --- LEVEL 8: PCAP CHALLENGE ---
@app.route('/level8_pcap', methods=['GET', 'POST'])
def level8_pcap():
    message = ""
    if request.method == 'POST':
        if request.form.get('flag', '').strip() == LEVEL_8_PCAP_FLAG:
            session['level8_unlocked'] = True
            return redirect(url_for('final_round'))
        else:
            message = "Incorrect Flag. Check those packets again."
    return render_template('level8_pcap.html', message=message)

# --- FINAL ROUND ---
@app.route('/final_round')
def final_round():
    # Ensure user passed the final challenge
    if not session.get('level8_unlocked'):
        return redirect(url_for('level8_pcap'))
    return render_template('final_round.html')

# --- Route to serve challenge files ---
@app.route('/challenge_files/<filename>')
def challenge_files(filename):
    # This serves files from your 'static' folder
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        filename,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)