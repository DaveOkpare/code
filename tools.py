import shlex
import subprocess


def _run_process_streaming(command, cwd="."):
    """
    Runs a command and streams output in real-time to the console,
    while capturing it to return to the LLM.
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
        )

        captured_stdout = []

        # Read stdout line by line as it is generated
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(f"[Stream]: {output.strip()}")  # Show user immediately
                captured_stdout.append(output)

        # Get any remaining stderr
        stderr = process.stderr.read()

        # Combine for the LLM
        full_output = "".join(captured_stdout)

        if process.returncode == 0:
            return f"STDOUT:\n{full_output}"
        else:
            return f"STDERR:\n{stderr}\nPARTIAL STDOUT:\n{full_output}"

    except Exception as e:
        return f"EXECUTION ERROR: {str(e)}"


def read_file(filepath: str):
    """Reads a file"""
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return str(e)


def grep_search(pattern: str, filepath: str, flags: str = "-n"):
    """Searches for a pattern in a file.
    Flags: -n (line numbers), -i (ignore case), -r (recursive)
    """
    safe_pattern = shlex.quote(pattern)
    safe_path = shlex.quote(filepath)
    cmd = f"grep {flags} {safe_pattern} {safe_path}"
    return _run_process_streaming(cmd)


def edit_file(find: str, replace: str, filepath: str):
    """Replace text in a file using sed."""
    safe_find = find.replace("/", "\\/")
    safe_replace = replace.replace("/", "\\/")
    safe_path = shlex.quote(filepath)

    cmd = f"sed -i 's/{safe_find}/{safe_replace}/g' {safe_path}"
    return _run_process_streaming(cmd)


def write(content: str, filepath: str):
    """Writes content to a file (overwrites if exists)."""
    try:
        with open(filepath, "w") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def execute(command: str):
    """Executes a raw bash command."""
    return _run_process_streaming(command)
