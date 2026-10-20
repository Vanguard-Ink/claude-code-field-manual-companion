#!/usr/bin/env python3
"""Remove personal data from every file under a folder, in place.

    python3 tools/scrub-email.py <folder> <email> [--user NAME] [--host NAME]

Text files (anything that decodes as UTF-8, whatever its name):
- the email, case-insensitively, plain and JSON-escaped, and its local part
  when it is distinctive (agents have used it as a git user.name);
- with --user, the login name in home paths (/home/NAME, C:\\Users\\NAME)
  and in git's fallback identity (NAME@HOST);
- with --host, the machine's host name;
- OpenTelemetry account identifiers (user.account_uuid, user.account_id,
  organization.id) wherever they appear as attribute values.
Binary files: the same email and home path are overwritten byte for byte
with a same-length mask, so file sizes and offsets don't change.
Prints each file it changed and a total; exit 0. Run it on a COPY
(pack-results.sh does).
"""
import re
import sys
from pathlib import Path

OTEL_ID = re.compile(r'("key": ?"(?:user\.account_uuid|user\.account_id|organization\.id)",'
                     r' ?"value": ?\{"stringValue": ?")[^"]*(")')


def main() -> int:
    root, email = Path(sys.argv[1]), sys.argv[2]
    user = sys.argv[sys.argv.index("--user") + 1] if "--user" in sys.argv else ""
    rx = re.compile(re.escape(email).replace("@", "(?:@|\\\\u0040)"), re.IGNORECASE)
    lp = email.split("@")[0]
    # Only a distinctive local part: a short one would hit ordinary words.
    local = re.compile(r"\b" + re.escape(lp) + r"\b", re.IGNORECASE) if len(lp) >= 6 else None
    host = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else ""
    homes = re.compile(r"(/home/|Users[\\/]{1,2})" + re.escape(user) + r"\b") if user else None
    ident = re.compile(r"\b" + re.escape(user) + r"@") if user else None
    hostrx = re.compile(re.escape(host), re.IGNORECASE) if len(host) >= 4 else None
    brx = re.compile(re.escape(email.encode()), re.IGNORECASE)
    blp = re.compile(re.escape(lp.encode()), re.IGNORECASE) if local else None
    bhome = re.compile(rb"(/home/|Users[\\/]{1,2})" + re.escape(user.encode())) if user else None
    total = 0
    for f in root.rglob("*"):
        if not f.is_file() or f.is_symlink():
            continue
        raw = f.read_bytes()
        try:
            s = raw.decode("utf-8")
        except UnicodeDecodeError:
            s = None
        if s is not None:
            new, n = rx.subn("user@example.invalid", s)
            if local:
                new, k = local.subn("lab-user", new); n += k
            new, k = OTEL_ID.subn(r"\1redacted\2", new); n += k
            if homes:
                new, k = homes.subn(r"\1user", new); n += k
            if ident:
                new, k = ident.subn("user@", new); n += k
            if hostrx:
                new, k = hostrx.subn("lab-host", new); n += k
            if n:
                f.write_text(new, encoding="utf-8")
        else:  # binary: same-length masks only
            n = 0
            new_b, k = brx.subn(lambda m: b"x" * len(m.group(0)), raw); n += k
            if blp:
                new_b, k = blp.subn(lambda m: b"x" * len(m.group(0)), new_b); n += k
            if bhome:
                new_b, k = bhome.subn(lambda m: m.group(1) + b"u" * len(user.encode()), new_b)
                n += k
            if user:
                new_b, k = re.subn(re.escape(user.encode()) + rb"@",
                                   lambda m: b"u" * (len(m.group(0)) - 1) + b"@", new_b)
                n += k
            if hostrx:
                new_b, k = re.subn(re.escape(host.encode()),
                                   lambda m: b"h" * len(m.group(0)), new_b, flags=re.IGNORECASE)
                n += k
            if n:
                f.write_bytes(new_b)
        if n:
            print(f"{n:5d}  {f}")
            total += n
    print(f"scrubbed {total} occurrence(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
