#!/usr/bin/env python3
"""MTMIS Loop Tool — local bridge (stdlib only).

The standalone HTML page (mtmis-loop-tool.html) cannot call the MTMIS
endpoint directly from file:// — the browser blocks it (CORS). This tiny
bridge runs on your own PC and forwards the lookup to MTMIS, so the page
works without the Chrome extension.

Usage:
  1. Put this file next to mtmis-loop-tool.html (same folder).
  2. Run:  python mtmis-bridge.py
     (or:  python3 mtmis-bridge.py)
  3. Open:  http://127.0.0.1:8766/
     — the tool page loads from here, and lookups go through the bridge.
  Or double-click mtmis-loop-tool.html directly — the page tries the
  MTMIS site first and falls back to this bridge on its own.

Routes:
  GET  /              -> serves mtmis-loop-tool.html (if next to this script)
  GET  /api/ping      -> {"ok": true}
  POST /api/vehicle   -> JSON {endpoint, registrationNo, registrationDate,
                        dntCaptchaInputText, dntCaptchaToken, dntCaptchaText}
                        forwarded to the MTMIS endpoint as multipart/form-data;
                        the MTMIS JSON reply is returned as-is.
  POST /api/captcha   -> JSON {"action": "captcha"}; fetches a fresh captcha
                        from MTMIS GetCaptcha and returns it as
                        {"ok": true, "captchaUrl": ..., "raw": ...}.
                        (Captcha token ki expiry hoti hai — purana payload
                        expire ho jata hai, is liye fresh chahiye hota hai.)

Nothing is saved or sent anywhere else. Stop with Ctrl+C.
"""

import json
import os
import uuid
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8766
PAGE = "mtmis-loop-tool.html"
CAPTCHA_URLS = [
    "https://mtmis.excise.punjab.gov.pk/gtw/Public/Mtmis/GetCaptcha",
    "https://mtmis.excise.punjab.gov.pk/gtw/Public/Home/GetCaptcha",
]
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def multipart_body(fields):
    boundary = "----mtmisbridge" + uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        parts.append(
            "--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
            % (boundary, name, value)
        )
    body = "".join(parts) + "--%s--\r\n" % boundary
    return body.encode("utf-8"), "multipart/form-data; boundary=" + boundary


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")

    def _json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path in ("/api/ping", "/api/ping/"):
            self._json({"ok": True})
            return
        if self.path in ("/", "/index.html"):
            here = os.path.dirname(os.path.abspath(__file__))
            page = os.path.join(here, PAGE)
            if os.path.exists(page):
                data = open(page, "rb").read()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self._json({"ok": False, "error": PAGE + " not found next to the bridge"}, 404)
            return
        self._json({"ok": False, "error": "unknown route"}, 404)

    def do_POST(self):
        if self.path in ("/api/captcha", "/api/captcha/"):
            # Fresh captcha — MTMIS GetCaptcha se naya captcha lao.
            tried = []
            for url in CAPTCHA_URLS:
                try:
                    req = urllib.request.Request(url, method="GET")
                    req.add_header("Accept", "application/json, text/plain, */*")
                    req.add_header("User-Agent", UA)
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        body = resp.read().decode("utf-8", "replace")
                        self._json({"ok": True, "captchaUrl": url, "raw": body})
                        return
                except urllib.error.HTTPError as e:
                    tried.append("%s -> HTTP %s" % (url, e.code))
                except Exception as e:
                    tried.append("%s -> %s" % (url, e))
            self._json(
                {"ok": False, "error": "MTMIS se naya captcha nahi mila", "tried": tried},
                502,
            )
            return
        if self.path not in ("/api/vehicle", "/api/vehicle/"):
            self._json({"ok": False, "error": "unknown route"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception as e:
            self._json({"ok": False, "error": "bad JSON: %s" % e}, 400)
            return
        endpoint = (payload.get("endpoint") or "").strip()
        if not endpoint.startswith("https://mtmis.excise.punjab.gov.pk/"):
            self._json({"ok": False, "error": "endpoint not allowed"}, 400)
            return
        fields = {
            "registrationNo": payload.get("registrationNo", ""),
            "registrationDate": payload.get("registrationDate", ""),
            "dntCaptchaInputText": payload.get("dntCaptchaInputText", ""),
            "dntCaptchaToken": payload.get("dntCaptchaToken", ""),
            "dntCaptchaText": payload.get("dntCaptchaText", ""),
        }
        body, ctype = multipart_body(fields)
        req = urllib.request.Request(endpoint, data=body, method="POST")
        req.add_header("Content-Type", ctype)
        req.add_header("Accept", "application/json, text/plain, */*")
        req.add_header(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                out = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", resp.headers.get_content_type() or "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)
        except urllib.error.HTTPError as e:
            out = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)
        except Exception as e:
            self._json({"ok": False, "error": str(e)}, 502)


if __name__ == "__main__":
    print("MTMIS bridge chal raha hai: http://%s:%d/  (band karne ke liye Ctrl+C)" % (HOST, PORT))
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
