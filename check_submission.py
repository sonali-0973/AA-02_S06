"""Read-only local AA-02 artefact checks. Does not execute submitted code."""
import argparse
import hashlib
import html
import re
import stat
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ARTEFACTS = {
    "frontend_root": "frontend", "backend_root": "backend",
    "database_root": "database", "config_root": "config",
    "integration_evidence": "evidence/integration-evidence.md",
    "testing_debugging_evidence": "evidence/testing-debugging-evidence.md",
    "contribution_evidence": "evidence/contribution-evidence.md",
}
HEADINGS = {
    "README.md": ["Project Overview", "Group Members", "Technology Stack", "Setup Instructions", "Run Instructions", "API Endpoints", "Known Limitations"],
    ARTEFACTS["integration_evidence"]: ["Integrated Workflow", "Frontend Evidence", "Backend API Evidence", "Database Evidence", "Success Case", "Error or Empty-Data Case"],
    ARTEFACTS["testing_debugging_evidence"]: ["API Request Evidence", "Browser or Network Evidence", "Log or Console Evidence", "Issue Found", "Fix Applied", "Retest Evidence"],
    ARTEFACTS["contribution_evidence"]: ["Contribution Summary", "Individual Contributions", "Research or Technology Decisions", "Academic Integrity and Source Acknowledgement"],
}
LABELS = ["C01 Manifest", "C02 README", "C03 Frontend source", "C04 Backend source", "C05 Database scripts or model", "C06 Setup configuration", "C07 Integration evidence", "C08 Testing and debugging evidence", "C09 Contribution evidence", "C10 Referenced evidence assets"]
SOURCE = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".html", ".css", ".vue", ".svelte", ".cs", ".java", ".go", ".rb", ".php", ".rs", ".c", ".cpp"}
DATA = SOURCE | {".sql", ".json", ".csv", ".prisma", ".db", ".sqlite", ".sqlite3"}
CONFIG = {".yml", ".yaml", ".toml", ".json", ".conf", ".ini", ".env", ".example", ".sh", ".ps1", ".bat"}
IGNORED = {"node_modules", ".venv", "venv", "__pycache__", ".git", "dist", "build"}
# Fingerprints of the distributed runnable bootstrap. These identify unchanged starter
# source; they do not judge the correctness of student implementations.
BOOTSTRAP = {
    "frontend/index.html": "53097c27930bce493476543dc94492d8f57fad18354fbbde37f8c4e48bfc982b",
    "frontend/nginx.conf": "640e98b5df5dc47c8d6dd8f876b0a6b197960fac4c355d8eeff05b080390bfe1",
    "frontend/scripts/action-queue.js": "c2bf3d972838f8d6afcd85ba9104485f6add3e4ba18858358a7441d569178954",
    "frontend/scripts/http.js": "666995defdf674f22622d22997868e7b362ee9fb029b829b08520fd9c0cac4f1",
    "frontend/scripts/index.js": "44545a05fde7fc597e4cdfe37e305a13d6cf1c429f8ee079b914b73357bc7ded",
    "frontend/assets/styles/main.css": "a5a19f43683081c3d1444295e2e19fb145ef344869e135e1b1d28be84f235a64",
    "backend/app/main.py": "fa93cbb04b65605205d2ed2f727d3d145fb59e109083149463b673e07d7a12bc",
    "backend/app/__init__.py": "bde85bfe7b39114b82e0600d41a9939ce6600296c4292748b7837deee50417b6",
    "backend/app/application/__init__.py": "bde85bfe7b39114b82e0600d41a9939ce6600296c4292748b7837deee50417b6",
    "backend/app/application/service.py": "479d8ad111be08d15e79c063052fc782e4789e3613d51c41e66470cc0c1e9b3e",
    "backend/app/domain/ports.py": "cc97486a1001d7c6f7f86fc674902d3d26cce6c017ac8168769439b66eab4eb1",
    "backend/app/domain/__init__.py": "bde85bfe7b39114b82e0600d41a9939ce6600296c4292748b7837deee50417b6",
    "backend/app/domain/scenario.py": "038dbfa1e5f82d9292c0af705e3b84a15defc0f4f8bf7090f68bc44a829e244e",
    "backend/app/infrastructure/postgres.py": "71a7ccc63345a3e1f6a98a313ce3b31bcb5424fc50eaf92d5cc833aeaa60c561",
    "backend/app/infrastructure/__init__.py": "bde85bfe7b39114b82e0600d41a9939ce6600296c4292748b7837deee50417b6",
    "backend/app/presentation/api.py": "c27a1c4897005d99653e780395bb5733b351a8088ec49e94282a8fc904d049f5",
    "backend/app/presentation/__init__.py": "bde85bfe7b39114b82e0600d41a9939ce6600296c4292748b7837deee50417b6",
    "database/001-schema.sql": "fbcf142a799dd68b55a96b0d5e7e8e9ae8efa232a99df52937bcbf01a9ff527e",
    "database/002-seed.sql": "a5c9063330a37c09ee2ae1ff8dda8e2657a44ba47f3462eb89f5f5608b500a02",
}
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|\bLorem ipsum\b|\bArtificial structural test content\b|\bTemplate only\b|\bRecord your actual work\b|\bReplace (?:every|this)\b", re.I)

class CheckError(Exception):
    pass


def clean_path(value):
    value = unquote(html.unescape(value)).replace("\\", "/")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise CheckError("Use a relative local path inside the submission: " + value)
    parts = []
    for part in value.split("/"):
        if part in {"", "."}: continue
        if part == "..":
            if not parts: raise CheckError("Path escapes submission: " + value)
            parts.pop()
        else: parts.append(part)
    return "/".join(parts)


class Submission:
    def __init__(self, target):
        self.target = target
        self.archive = None
        self.files = {}
        if target.is_dir():
            self.root = target.resolve()
            for path in self.root.rglob("*"):
                if path.is_file() and not any(part in IGNORED for part in path.relative_to(self.root).parts):
                    self.files[path.relative_to(self.root).as_posix()] = path
        else:
            if not target.is_file(): raise CheckError("Supply an existing project directory or .zip file.")
            if target.suffix.lower() != ".zip": raise CheckError("Archive must use .zip format.")
            self.archive = zipfile.ZipFile(target)
            members = self.archive.infolist()
            names = set()
            raw = {}
            for member in members:
                normal = clean_path(member.filename)
                if normal != member.filename.rstrip("/"):
                    raise CheckError("Archive contains a non-canonical or unsafe path: " + member.filename)
                if stat.S_ISLNK(member.external_attr >> 16): raise CheckError("Replace ZIP symbolic links with local files.")
                if not member.is_dir():
                    if normal in names: raise CheckError("Archive contains duplicate member: " + normal)
                    names.add(normal)
                    raw[normal] = member
            # Accept flat ZIPs or one wrapper project folder, as common repository exports.
            if "submission-manifest.yml" in raw:
                prefix = ""
            else:
                candidates = [name.rsplit("/", 1)[0] for name in raw if name.endswith("/submission-manifest.yml") and name.count("/") == 1]
                if len(candidates) != 1: raise CheckError("ZIP must contain the project files at its root or inside one project folder.")
                prefix = candidates[0] + "/"
                if any(not name.startswith(prefix) for name in raw): raise CheckError("Keep all ZIP files inside the single project folder.")
            self.files = {name[len(prefix):]: member for name, member in raw.items()}
            self.root = None

    def read(self, name):
        if name not in self.files: raise CheckError("Add required file: " + name)
        value = self.files[name]
        if self.archive:
            return self.archive.read(value)
        if not value.resolve().is_relative_to(self.root): raise CheckError("Local link escapes submission: " + name)
        return value.read_bytes()

    def text(self, name):
        try: return self.read(name).decode("utf-8-sig")
        except UnicodeError: raise CheckError("Save this text file as UTF-8: " + name)

    def close(self):
        if self.archive: self.archive.close()


def nonplaceholder(value, label):
    if not isinstance(value, str) or not value.strip(): raise CheckError("Fill a non-empty string for " + label)
    if re.search(r"\bTODO\b|Student Name|^GroupID$|Short contribution summary", value, re.I):
        raise CheckError("Replace placeholder for " + label)


def check_manifest(submission):
    try: import yaml
    except ImportError: raise CheckError("Install checker dependency: python -m pip install -r config/checker-requirements.txt")
    class UniqueLoader(yaml.SafeLoader):
        pass
    def mapping(loader, node):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node)
            if not isinstance(key, str): raise CheckError("Manifest mapping keys must be strings.")
            if key in result: raise CheckError("Remove duplicate YAML key: " + key)
            result[key] = loader.construct_object(value_node)
        return result
    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try: manifest = yaml.load(submission.text("submission-manifest.yml"), Loader=UniqueLoader)
    except yaml.YAMLError as error: raise CheckError("Repair manifest YAML: " + str(error).splitlines()[0])
    if not isinstance(manifest, dict): raise CheckError("Manifest root must be a mapping.")
    for section in ["assessment", "group", "project", "artefacts"]:
        if not isinstance(manifest.get(section), dict): raise CheckError("Add manifest mapping: " + section)
    assessment = manifest["assessment"]
    if assessment.get("id") != "additional-assessment-02": raise CheckError("Set assessment.id to additional-assessment-02.")
    if assessment.get("title") != "Integration, Containerisation, and Testing Readiness Demonstration": raise CheckError("Use the assessment title from the brief.")
    group = manifest["group"]
    nonplaceholder(group.get("id"), "group.id")
    if any(c in group["id"] for c in '/\\<>:"|?*') or group["id"].endswith((".", " ")):
        raise CheckError("Use a group.id that is safe in the required ZIP filename.")
    members = group.get("members")
    if not isinstance(members, list) or not members: raise CheckError("Add group.members records.")
    for index, member in enumerate(members, 1):
        if not isinstance(member, dict): raise CheckError("Each member must be a mapping.")
        for key in ["student_id", "name", "contribution_summary"]: nonplaceholder(member.get(key), f"group.members[{index}].{key}")
    for key in ["scenario", "frontend_start_command", "backend_start_command", "frontend_url", "backend_base_url"]:
        nonplaceholder(manifest["project"].get(key), "project." + key)
    for key in ["frontend_url", "backend_base_url"]:
        parsed = urlsplit(manifest["project"][key])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc: raise CheckError("Use an HTTP(S) URL for project." + key)
    for key, expected in ARTEFACTS.items():
        if manifest["artefacts"].get(key) != expected: raise CheckError(f"Set artefacts.{key} to {expected}.")
    return manifest


def sections(submission, filename, required=None):
    # Ignore fenced examples, including Windows CRLF files.
    found = {}
    fence = None
    current = None
    for line in submission.text(filename).splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            run = marker[1]
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence):
                fence = None
            continue
        if fence is not None: continue
        match = re.match(r"^ {0,3}#{1,6} +(.+?) *#* *$", line)
        if match:
            current = match[1].strip().strip("*_").strip()
            found.setdefault(current, [])
        elif current is not None:
            found[current].append(line)
    missing = [h for h in (required if required is not None else HEADINGS[filename]) if h not in found]
    if missing: raise CheckError("Add headings in " + filename + ": " + ", ".join(missing))
    return {heading: "\n".join(lines).strip() for heading, lines in found.items()}


def check_sections(submission, filename):
    found = sections(submission, filename)
    for heading in HEADINGS[filename]:
        body = found[heading]
        plain = re.sub(r"(?m)^\s*(?:[-*+]|\d+[.)])\s*", "", body)
        plain = re.sub(r"[`*_\[\]()|#>\-]", " ", plain)
        if not re.search(r"[^\W_]", plain, re.UNICODE) or PLACEHOLDER.search(body):
            raise CheckError(f"Complete {heading} in {filename} with substantive, non-placeholder details.")
    return found


def check_content(submission, folder, extensions):
    candidates = [name for name in submission.files if name.startswith(folder + "/") and not any(p in IGNORED for p in PurePosixPath(name).parts) and (PurePosixPath(name).suffix.lower() in extensions or (folder == "config" and PurePosixPath(name).name in {"Dockerfile", "Makefile", ".env"}))]
    populated = [name for name in candidates if submission.read(name).strip()]
    if not populated: raise CheckError("Add non-empty " + folder + " source/data/configuration files; documentation alone does not count.")
    if folder != "config" and all(hashlib.sha256(submission.read(name).replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest() == BOOTSTRAP.get(name) for name in populated):
        raise CheckError("Replace or extend the unchanged " + folder + " bootstrap for the assigned scenario.")
    if folder == "config":
        setup = sections(submission, "README.md", ["Setup Instructions"])["Setup Instructions"]
        if PLACEHOLDER.search(setup) or not re.search(r"\b(?:verified|checked|confirmed|tested|observed|passed|succeeded)\b", setup, re.I):
            raise CheckError("Document an actual setup/configuration verification result in README.md Setup Instructions.")


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in {"src", "href"} and value)


def asset_links(text):
    # Markdown inline and reference links, HTML attributes and code-formatted asset paths.
    links = re.findall(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", text)
    links += re.findall(r"(?m)^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", text)
    definitions = {value.casefold() for value in re.findall(r"(?m)^ {0,3}\[([^\]]+)\]:", text)}
    for label, reference in re.findall(r"!?\[([^\]]+)\]\[([^\]]*)\]", text):
        if (reference or label).casefold() not in definitions:
            raise CheckError("Add the Markdown reference definition for [" + (reference or label) + "].")
    parser = HTMLLinks()
    parser.feed(text)
    links += parser.links
    links += [value for value in re.findall(r"`([^`\n]+)`", text) if re.search(r"\.(?:png|jpe?g|gif|webp|svg|pdf|json|har|log|txt|csv|zip|xml)$", value, re.I) and not re.search(r"\s", value)]
    return links


def check_assets(submission):
    for filename in list(HEADINGS)[1:]:
        check_sections(submission, filename)
        for link in asset_links(submission.text(filename)):
            link = link.strip("<>")
            parsed = urlsplit(link)
            if parsed.scheme in {"http", "https", "mailto", "data"}: continue
            if parsed.scheme: raise CheckError("Use local relative evidence paths, not " + link)
            if not parsed.path: continue
            # Resolve links relative to the evidence document, as Markdown does.
            local_path = unquote(parsed.path)
            if local_path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", local_path):
                raise CheckError("Use a relative evidence asset path: " + link)
            name = clean_path(str(PurePosixPath(filename).parent) + "/" + local_path)
            if name not in submission.files: raise CheckError(f"Add referenced asset {name} or correct its link in {filename}.")
            submission.read(name)  # Checks local symlink containment / ZIP readability.


def report(label, operation):
    try:
        result = operation()
        print(label + ": TRUE")
        return True, result
    except Exception as error:
        message = str(error).replace("\n", " ") or error.__class__.__name__
        print(label + ": FALSE - " + message)
        return False, None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only AA-02 local readiness checks; TRUE does not prove functionality or authentic evidence.")
    parser.add_argument("target", nargs="?", default=".", help="project directory or ZIP archive (default: current directory)")
    args = parser.parse_args(argv)
    target = Path(args.target)
    try: submission = Submission(target)
    except Exception as error:
        for label in LABELS: print(label + ": FALSE - Cannot inspect submission: " + str(error).replace("\n", " "))
        if not target.is_dir():
            print("A01 ZIP format: FALSE - Supply a readable safe ZIP containing the submission.")
            print("A02 ZIP name: FALSE - Cannot check archive name without a readable submission manifest.")
        return 1
    results = []
    try:
        ok, manifest = report(LABELS[0], lambda: check_manifest(submission)); results.append(ok)
        jobs = [
            lambda: check_sections(submission, "README.md"),
            lambda: check_content(submission, "frontend", SOURCE),
            lambda: check_content(submission, "backend", SOURCE),
            lambda: check_content(submission, "database", DATA),
            lambda: check_content(submission, "config", CONFIG),
            lambda: check_sections(submission, ARTEFACTS["integration_evidence"]),
            lambda: check_sections(submission, ARTEFACTS["testing_debugging_evidence"]),
            lambda: check_sections(submission, ARTEFACTS["contribution_evidence"]),
            lambda: check_assets(submission),
        ]
        for label, job in zip(LABELS[1:], jobs): results.append(report(label, job)[0])
        if submission.archive:
            def archive_format():
                bad = submission.archive.testzip()
                if bad: raise CheckError("Repair corrupt ZIP member: " + bad)
            results.append(report("A01 ZIP format", archive_format)[0])
            def archive_name():
                if manifest is None: raise CheckError("Fix C01 before archive/group filename matching can be checked.")
                expected = "128-353-AA2-" + manifest["group"]["id"] + ".zip"
                if target.name != expected: raise CheckError("Rename archive to " + expected)
            results.append(report("A02 ZIP name", archive_name)[0])
    finally: submission.close()
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
