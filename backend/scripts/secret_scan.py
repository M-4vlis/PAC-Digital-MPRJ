import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATTERNS = [
    re.compile("BEGIN " + "(?:RSA|OPENSSH|EC) PRIVATE KEY"),
    re.compile("PAC_DEMO_" + "PASSWORD\\s*="),
    re.compile("SEI_SERVICE_" + "KEY\\s*=\\s*[^\\s$][^\\s]*"),
    re.compile("PNCP_API_" + "TOKEN\\s*=\\s*[^\\s$][^\\s]*"),
]


def main():
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    findings = []
    for relative in filter(None, tracked):
        path = ROOT / relative
        try: content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        for number, line in enumerate(content.splitlines(), 1):
            if any(pattern.search(line) for pattern in PATTERNS): findings.append(f"{relative}:{number}")
    if findings:
        raise SystemExit("Possíveis segredos versionados:\n" + "\n".join(findings))
    print(f"secret_scan=passed tracked_files={len(tracked) - 1}")


if __name__ == "__main__": main()
