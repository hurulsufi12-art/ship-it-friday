"""Ship It Friday — entry program.

Writes one git commit message (1-159 chars), a single line from an AI coding
agent right before it breaks production on a Friday, to /output/entry.txt.
Stdlib only, deterministic.
"""
import os

TEXT = ("feat: deploy to prod Friday 4:59pm, tests deleted for speed, "
        "rollback plan is vibes and a prayer")

# Gate bound from RULES.txt (sealed scorer): 1-159 chars.
MAX_CHARS = 159


def main():
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-159 chars, one line,
    # not whitespace-only, no leading/trailing space. Fail loudly instead of
    # writing an invalid entry.
    if (
        not 1 <= len(TEXT) <= MAX_CHARS
        or "\n" in TEXT
        or "\r" in TEXT
        or not TEXT.strip()
        or TEXT != TEXT.strip()
    ):
        raise SystemExit("entry text violates the 1-159 char single-line gate")
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    # No trailing newline: the file bytes must equal TEXT exactly, so the
    # entry stays at 96 bytes (smaller text wins an exact-tie tie-break).
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
