from flask import Flask, render_template, request, redirect, url_for, session
import subprocess, os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'replace-with-a-secure-random-key'

SECRET_CODE = "blacklotus"
DEFAULT_CODE = """# Simple bug example: greet vs. greets
def greet(name):
    return f"Hello, {name}"

# Intentional typo below
print(greets("World"))
"""

# keep track of the current running process
running_proc = None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('code') == SECRET_CODE:
            return redirect(url_for('compiler'))
    return render_template('index.html')

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
FS = {
    "dir_a": {},
    "dir_b": {},
    "dir_c": {
        "secret.txt": "The ultimate secret is 42.\n"
    },
    "dir_d": {},
    # ... add as many dummy dirs as you like ...
}

def resolve_path(cwd):
    """Return the FS subtree at cwd."""
    node = FS
    for part in cwd:
        node = node.get(part, {})
    return node

@app.route('/terminal', methods=['GET', 'POST'])
def terminal():
    # init cwd and history
    if 'cwd' not in session:
        session['cwd'] = []
        session['history'] = []
    cwd = session['cwd']
    history = session['history']

    if request.method == 'POST':
        cmd = request.form.get('command', '').strip()
        parts = cmd.split()
        output = ''
        if parts[0] == 'ls':
            node = resolve_path(cwd)
            output = '  '.join(sorted(node.keys())) or ''
        elif parts[0] == 'cd':
            target = parts[1] if len(parts) > 1 else ''
            if target == '..':
                if cwd: cwd.pop()
            elif target in resolve_path(cwd):
                cwd.append(target)
            else:
                output = f"bash: cd: {target}: No such file or directory"
        elif parts[0] == 'cat':
            fname = parts[1] if len(parts) > 1 else ''
            node = resolve_path(cwd)
            if fname in node:
                output = node[fname]
            else:
                output = f"bash: cat: {fname}: No such file or directory"
        else:
            output = f"bash: {parts[0]}: command not found"
        history.append((cwd.copy(), cmd, output))
        session['cwd'] = cwd
        session['history'] = history

    prompt = '/' + '/'.join(cwd) if cwd else '/'

    return render_template('terminal.html',
                           history=history,
                           prompt=prompt)

if __name__ == '__main__':
    app.run(debug=True)