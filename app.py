from flask import Flask, render_template, request, redirect, url_for, session
import subprocess, os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'replace-with-a-secure-random-key'

SECRET_CODE = "Morse Code is Fun"
DEFAULT_CODE = """
encoded_str = "aHR0cDovLzU0LjE5Ny4xNi4xNjMvdGVybWluYWw="

# Decode it
decoded_bytes = base64.b64decode(encoded_str)
decoded_str = decoded_bytes.decode('utf-8')

print("Secret:", decoded_str)

"""

# keep track of the current running process
running_proc = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('code', '').strip().lower() == SECRET_CODE.lower():
            return redirect(url_for('compiler'))
    return render_template('index.html')

@app.route('/quiz', methods=['GET'])
def quiz():
    return render_template('quiz.html')


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
                running_proc.kill()
                output = 'Error: Execution timed out.'
        elif action == 'stop':
            if running_proc and running_proc.poll() is None:
                running_proc.kill()
                output = 'Process stopped by user.'
    return render_template('compiler.html', code=code, output=output)


# A dummy filesystem tree
FS = {}

# Create 40 dummy directories
for i in range(1, 41):
    dirname = f"dir_{i}"
    FS[dirname] = {}

# Inject the final clue in one random directory
FS["dir_27"]["final_round.txt"] = "Go to final round through this url: http://54.197.16.163/quiz"
FS ["dir_14"]["secret.txt"] = "You got fooled! Try harder."
FS["dir_16"]["secret2.txt"] = "You got fooled again! Try harderrr."
FS["dir_19"]["secret3.txt"] = "I would have given up if i were you lol."

def resolve_path(cwd):
    """Return the FS subtree at cwd."""
    node = FS
    for part in cwd:
        node = node.get(part, {})
    return node

@app.route('/terminal', methods=['GET', 'POST'])
def terminal():
    if 'cwd' not in session:
        session['cwd'] = []
        session['history'] = []
    cwd = session['cwd']
    history = session['history']
    output = ""

    def resolve_path(cwd):
        node = FS
        for part in cwd:
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


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=80)