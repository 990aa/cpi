from __future__ import annotations

import json
import mimetypes
import threading
import urllib.parse
import uuid
from email import policy
from email.parser import BytesParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
WEB = ROOT / "web"
DATA = ROOT.parent.parent / "data"
UPLOADS = DATA / "uploads"
STORE_FILE = DATA / "skillswap.json"


def seeded_data() -> dict[str, Any]:
    return {
        "profiles": {
            "dheeraj": {
                "id": "dheeraj", "name": "Dheeraj", "email": "dheeraj@campus.edu",
                "password": "demo", "initials": "DS", "branch": "Computer Science",
                "year": "3rd year", "campus": "IIT Campus", "phone": "",
                "bio": "Building useful things and happy to make Python feel less intimidating.",
                "teach": ["Python", "React", "DSA"], "learn": ["UI/UX Design", "Figma"],
                "id_file": "id.pdf", "id_status": "verified", "projects": [{"name": "Python study group", "file": ""}],
            },
            "aisha": {
                "id": "aisha", "name": "Aisha Khan", "email": "aisha@campus.edu",
                "password": "demo", "initials": "AK", "branch": "Electronics",
                "year": "2nd year", "campus": "IIT Campus", "phone": "",
                "bio": "Designing small robots and documenting the process.",
                "teach": ["Arduino", "Photography"], "learn": ["Python", "UI/UX Design"],
                "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Line following robot", "file": ""}],
            },
            "arjun": {
                "id": "arjun", "name": "Arjun Rao", "email": "arjun@campus.edu",
                "password": "demo", "initials": "AR", "branch": "Mechanical Engineering",
                "year": "4th year", "campus": "IIT Campus", "phone": "",
                "bio": "Maker, CAD enthusiast, and patient workshop buddy.",
                "teach": ["CAD", "3D Printing"], "learn": ["Video Editing", "Python"],
                "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Open source desk lamp", "file": ""}],
            },
            "kavya": {
                "id": "kavya", "name": "Kavya Menon", "email": "kavya@campus.edu",
                "password": "demo", "initials": "KM", "branch": "Computer Science",
                "year": "2nd year", "campus": "IIT Campus", "phone": "",
                "bio": "Learning in public through tiny web experiments.",
                "teach": ["HTML/CSS", "JavaScript"], "learn": ["React", "Figma"],
                "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Study planner web app", "file": ""}],
            },
            "rohan": {
                "id": "rohan", "name": "Rohan Das", "email": "rohan@campus.edu",
                "password": "demo", "initials": "RD", "branch": "Business",
                "year": "3rd year", "campus": "IIT Campus", "phone": "",
                "bio": "I enjoy turning observations into clear stories and decks.",
                "teach": ["Public Speaking", "Presentation Design"], "learn": ["DSA", "Photography"],
                "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Campus venture pitch", "file": ""}],
            },
            "zoya": {
                "id": "zoya", "name": "Zoya Ali", "email": "zoya@campus.edu",
                "password": "demo", "initials": "ZA", "branch": "Media Studies",
                "year": "1st year", "campus": "IIT Campus", "phone": "",
                "bio": "Collecting campus stories through sound and moving images.",
                "teach": ["Video Editing", "Illustration"], "learn": ["Public Speaking", "React"],
                "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Campus stories reel", "file": ""}],
            },
            "neel": {
                "id": "neel", "name": "Neel Joshi", "email": "neel@campus.edu",
                "password": "demo", "initials": "NJ", "branch": "Mathematics",
                "year": "3rd year", "campus": "IIT Campus", "phone": "",
                "bio": "Making difficult ideas visual and approachable.",
                "teach": ["Data Visualisation", "DSA"], "learn": ["Public Speaking", "Figma"],
                "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Campus data dashboard", "file": ""}],
            },
            "tara": {
                "id": "tara", "name": "Tara Iyer", "email": "tara@campus.edu",
                "password": "demo", "initials": "TI", "branch": "Architecture",
                "year": "4th year", "campus": "IIT Campus", "phone": "",
                "bio": "Sketching spaces, interfaces, and ideas that welcome people in.",
                "teach": ["Sketching", "Illustration"], "learn": ["CAD", "Figma"],
                "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Wayfinding concept", "file": ""}],
            },
            "swara": {
                "id": "swara", "name": "Swara", "email": "swara@campus.edu",
                "password": "demo", "initials": "S", "branch": "Design",
                "year": "2nd year", "campus": "IIT Campus", "phone": "",
                "bio": "I turn rough ideas into clear, friendly interfaces.",
                "teach": ["UI/UX Design", "Figma"], "learn": ["Python", "React"],
                "id_file": "id.pdf", "id_status": "verified", "projects": [{"name": "Campus events app", "file": ""}],
            },
            "manikarnika": {
                "id": "manikarnika", "name": "Mani Karnica", "email": "mani@campus.edu",
                "password": "demo", "initials": "MK", "branch": "Information Technology",
                "year": "3rd year", "campus": "IIT Campus", "phone": "",
                "bio": "Curious about creative technology, storytelling, and better presentations.",
                "teach": ["Video Editing", "Public Speaking"],
                "learn": ["Python", "UI/UX Design"], "id_file": "id.pdf", "id_status": "verified",
                "projects": [{"name": "Student documentary", "file": ""}],
            },
        },
        "connections": [
            {"id": 1, "from": "dheeraj", "to": "swara", "status": "accepted"},
        ],
        "next_connection_id": 2,
    }


class DemoStore:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        DATA.mkdir(exist_ok=True)
        UPLOADS.mkdir(exist_ok=True)
        if STORE_FILE.exists():
            self.data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        else:
            self.data = seeded_data()
            self.save()
        self.migrate_profiles()
        self.ensure_demo_projects()

    @property
    def profiles(self) -> dict[str, dict[str, Any]]:
        return self.data["profiles"]

    def save(self) -> None:
        STORE_FILE.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def migrate_profiles(self) -> None:
        changed = False
        if len(self.profiles) < 10:
            for profile_id, profile in seeded_data()["profiles"].items():
                if profile_id not in self.profiles:
                    self.profiles[profile_id] = profile
                    changed = True
        for profile in self.profiles.values():
            if "id_status" not in profile:
                profile["id_status"] = "verified" if profile.get("id_file") else "missing"
                changed = True
            projects = profile.get("projects", [])
            if any(isinstance(project, str) for project in projects):
                profile["projects"] = [{"name": project, "file": ""} for project in projects]
                changed = True
        if changed:
            self.save()

    def ensure_demo_projects(self) -> None:
        changed = False
        for profile in self.profiles.values():
            for project in profile.get("projects", []):
                if project.get("file"):
                    continue
                slug = "".join(character.lower() if character.isalnum() else "-" for character in project["name"]).strip("-")
                filename = f"{profile['id']}_demo_{slug}.html"
                project["file"] = filename
                (UPLOADS / filename).write_text(
                    f"<h1>{project['name']}</h1><p>Demo portfolio preview by {profile['name']}.</p>"
                    f"<p>This sample work represents the kind of project they can share during a SkillSwap session.</p>",
                    encoding="utf-8",
                )
                changed = True
        if changed:
            self.save()

    def public_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        public = {
            key: value for key, value in profile.items()
            if key not in {"password", "id_file"}
        }
        public["id_uploaded"] = bool(profile.get("id_file"))
        return public

    def authenticate(self, email: str, password: str) -> dict[str, Any]:
        for profile in self.profiles.values():
            if profile["email"].lower() == email.lower() and profile["password"] == password:
                return self.public_profile(profile)
        raise ValueError("Email or password is incorrect")

    def register(self, data: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            email = data["email"].strip().lower()
            if any(profile["email"].lower() == email for profile in self.profiles.values()):
                raise ValueError("An account with this email already exists")
            profile_id = uuid.uuid4().hex[:10]
            name = data["name"].strip()
            profile = {
                "id": profile_id, "name": name, "email": email, "password": data["password"],
                "initials": "".join(part[0] for part in name.split()[:2]).upper(),
                "branch": data.get("branch", "").strip(), "year": data.get("year", "").strip(),
                "campus": data.get("campus", "IIT Campus").strip(), "phone": data.get("phone", "").strip(),
                "bio": data.get("bio", "").strip(), "teach": data.get("teach", []),
                "learn": data.get("learn", []), "id_file": "", "id_status": "missing", "projects": [],
            }
            self.profiles[profile_id] = profile
            self.save()
            return self.public_profile(profile)

    def snapshot(self, user_id: str) -> dict[str, Any]:
        with self.lock:
            user = self.profiles[user_id]
            people = []
            for profile in self.profiles.values():
                if profile["id"] == user_id:
                    continue
                shared = sorted(
                    (set(profile["teach"]) & set(user["learn"]))
                    | (set(profile["learn"]) & set(user["teach"]))
                )
                people.append({
                    **self.public_profile(profile),
                    "shared": shared,
                    "connection": self.connection_for(user_id, profile["id"]),
                })
            incoming = [
                {**connection, "person": self.public_profile(self.profiles[connection["from"]])}
                for connection in self.data["connections"] if connection["to"] == user_id
            ]
            outgoing = [
                {**connection, "person": self.public_profile(self.profiles[connection["to"]])}
                for connection in self.data["connections"] if connection["from"] == user_id
            ]
            return {"user": self.public_profile(user), "people": people, "incoming": incoming, "outgoing": outgoing}

    def connection_for(self, first: str, second: str) -> dict[str, Any] | None:
        for connection in self.data["connections"]:
            if {connection["from"], connection["to"]} == {first, second}:
                return {"id": connection["id"], "status": connection["status"]}
        return None

    def connect(self, user_id: str, target_id: str) -> dict[str, Any]:
        with self.lock:
            if not self.profiles[user_id].get("id_file") or not self.profiles[user_id].get("projects"):
                raise ValueError("Upload a student ID and at least one project before connecting")
            existing = self.connection_for(user_id, target_id)
            if existing:
                return existing
            connection = {
                "id": self.data["next_connection_id"], "from": user_id,
                "to": target_id, "status": "pending",
            }
            self.data["next_connection_id"] += 1
            self.data["connections"].append(connection)
            self.save()
            return connection

    def respond(self, user_id: str, connection_id: int, status: str) -> None:
        with self.lock:
            for connection in self.data["connections"]:
                if connection["id"] == connection_id and connection["to"] == user_id:
                    connection["status"] = status
                    self.save()
                    return
            raise ValueError("Connection request not found")

    def save_profile(self, user_id: str, data: dict[str, Any]) -> None:
        with self.lock:
            profile = self.profiles[user_id]
            for field in ("bio", "branch", "year", "campus", "phone", "teach", "learn"):
                if field in data:
                    profile[field] = data[field]
            self.save()


STORE = DemoStore()


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def read_upload(self) -> tuple[dict[str, str], dict[str, bytes]]:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        content_type = self.headers.get("Content-Type", "")
        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
        )
        fields: dict[str, str] = {}
        files: dict[str, bytes] = {}
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if not name:
                continue
            content = part.get_payload(decode=True) or b""
            filename = part.get_filename()
            if filename:
                files[name] = content
                fields[f"{name}_filename"] = Path(filename).name
            else:
                fields[name] = content.decode("utf-8")
        return fields, files

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/state":
            user_id = urllib.parse.parse_qs(parsed.query).get("user", [""])[0]
            if user_id not in STORE.profiles:
                self.send_json({"error": "Please sign in first"}, HTTPStatus.UNAUTHORIZED)
                return
            self.send_json(STORE.snapshot(user_id))
            return
        if parsed.path.startswith("/api/projects/"):
            parts = parsed.path.split("/")
            if len(parts) != 5:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            user_id, stored_name = parts[3], urllib.parse.unquote(parts[4])
            if user_id not in STORE.profiles or Path(stored_name).name != stored_name:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            profile = STORE.profiles[user_id]
            project = next((item for item in profile.get("projects", []) if item.get("file") == stored_name), None)
            path = UPLOADS / stored_name
            if not project or not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        path = WEB / ("index.html" if parsed.path == "/" else parsed.path.lstrip("/"))
        if not path.is_file() or WEB not in path.parents:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/login":
                result = STORE.authenticate(**self.read_json())
            elif parsed.path == "/api/register":
                result = STORE.register(self.read_json())
            elif parsed.path == "/api/connect":
                data = self.read_json()
                result = STORE.connect(data["user"], data["target"])
            elif parsed.path == "/api/respond":
                data = self.read_json()
                STORE.respond(data["user"], int(data["connectionId"]), data["status"])
                result = {"ok": True}
            elif parsed.path == "/api/profile":
                data = self.read_json()
                STORE.save_profile(data["user"], data)
                result = {"ok": True}
            elif parsed.path == "/api/upload":
                fields, files = self.read_upload()
                user_id = fields["user"]
                profile = STORE.profiles[user_id]
                for field in ("id_file", "project_file"):
                    if field in files and files[field]:
                        original_name = fields.get(field + "_filename", "upload")
                        filename = f"{user_id}_{field}_{Path(original_name).name}"
                        (UPLOADS / filename).write_bytes(files[field])
                        if field == "id_file":
                            profile["id_file"] = original_name
                            profile["id_status"] = (
                                "verified" if Path(original_name).stem.lower() == "id"
                                and Path(original_name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
                                else "pending"
                            )
                        else:
                            profile.setdefault("projects", []).append({
                                "name": original_name,
                                "file": filename,
                            })
                STORE.save()
                result = {"ok": True}
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            self.send_json(result)
        except (KeyError, ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[skillswap] {format % args}")


def main() -> None:
    port = 8000
    print(f"SkillSwap demo running at http://localhost:{port}")
    print("Forward port 8000 in VS Code to share this demo.")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
