#!/usr/bin/env python3
import os, sys, time, random, string, json, datetime as dt
import requests

API = os.environ.get("API", "http://127.0.0.1:5005")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def _ok(msg): print(f"{GREEN}✔ {msg}{RESET}")
def _fail(msg): print(f"{RED}✘ {msg}{RESET}")

def uniq_user(prefix="u"):
    sfx = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{sfx}", f"{prefix}_{sfx}@example.com", "pw12345!"

class Tester:
    def __init__(self, base):
        self.base = base.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"Content-Type": "application/json"})
        self.pass_count = 0
        self.fail_count = 0
        self.context = {}

    # ---------- HTTP helpers ----------
    def _url(self, path): return f"{self.base}{path}"

    def _req(self, method, path, expected=None, allow=None, **kwargs):
        url = self._url(path)
        r = self.s.request(method, url, timeout=10, **kwargs)
        if expected is not None:
            ok = (r.status_code == expected)
        elif allow is not None:
            ok = (r.status_code in allow)
        else:
            ok = r.ok

        try:
            data = None if r.status_code == 204 else r.json()
        except Exception:
            data = None

        return ok, r, data

    def expect(self, desc, method, path, expected=None, allow=None, **kwargs):
        ok, r, data = self._req(method, path, expected=expected, allow=allow, **kwargs)
        if ok:
            self.pass_count += 1
            _ok(f"{desc}  ({r.status_code})")
        else:
            self.fail_count += 1
            _fail(f"{desc}  (got {r.status_code})")
            if data:
                print(YELLOW + "  response: " + json.dumps(data, indent=2) + RESET)
            else:
                print(YELLOW + f"  raw: {r.text[:400]}" + RESET)
        return r, data

    # ---------- Scenario ----------
    def run(self):
        print(f"Running E2E against {self.base}\n")

        # Signup user A (or fallback to login if already exists)
        uname, email, pw = uniq_user("userA")
        r, d = self.expect("signup A", "POST", "/auth/signup", expected=201,
                           json={"username": uname, "email": email, "password": pw})
        if r.status_code == 400 and d and "already" in (d.get("error","")+d.get("message","")).lower():
            _, _ = self.expect("login A", "POST", "/auth/login", expected=200,
                               json={"email": email, "password": pw})

        # cookie set?
        set_cookie = r.headers.get("Set-Cookie", "")
        if "session" in set_cookie.lower():
            self.pass_count += 1; _ok("session cookie set on signup/login")
        else:
            self.fail_count += 1; _fail("no Set-Cookie header on signup/login")

        # /auth/me
        _, d = self.expect("auth me (after login)", "GET", "/auth/me", expected=200)
        if d and d.get("authenticated") and d.get("user",{}).get("username"):
            self.pass_count += 1; _ok("authenticated true after login")
        else:
            self.fail_count += 1; _fail("/auth/me not authenticated")

        # Create project
        r, d = self.expect("create project", "POST", "/projects", expected=201,
                           json={"title": "P1", "description": "From E2E"})
        proj_id = (d or {}).get("id")
        self.context["proj_id"] = proj_id

        # List projects contains proj
        _, arr = self.expect("list projects", "GET", "/projects", expected=200)
        if isinstance(arr, list) and any(p.get("id")==proj_id for p in arr):
            self.pass_count += 1; _ok("created project appears in list")
        else:
            self.fail_count += 1; _fail("created project missing from list")

        # Get one project
        _ , _ = self.expect("get project by id", "GET", f"/projects/{proj_id}", expected=200)

        # Create tasks (13 mixed)
        statuses = ["todo", "in_progress", "done"]
        priorities = ["low","normal","high"]
        created_task_ids = []
        base_date = dt.date.today()
        for i in range(13):
            payload = {
                "project_id": proj_id,
                "title": f"T{i+1}",
                "priority": priorities[i % 3],
                "status": statuses[i % 3],
                "due_date": str(base_date + dt.timedelta(days=i)) if i % 2 == 0 else None
            }
            r, d = self.expect(f"create task {i+1}", "POST", "/tasks", expected=201, json=payload)
            if d and "id" in d: created_task_ids.append(d["id"])

        # Paginate tasks
        _, page1 = self.expect("tasks page 1", "GET",
                               f"/tasks?project_id={proj_id}&page=1&per_page=10&status=all&sort=due_date",
                               expected=200)
        _, page2 = self.expect("tasks page 2", "GET",
                               f"/tasks?project_id={proj_id}&page=2&per_page=10&status=all&sort=due_date",
                               expected=200)

        def _check_page(payload, expected_len):
            ok = isinstance(payload, dict) and isinstance(payload.get("data"), list) and \
                 payload.get("meta",{}).get("per_page") in (10, expected_len) and \
                 len(payload["data"]) == expected_len
            if ok: self.pass_count += 1; _ok(f"pagination length {expected_len} correct")
            else: self.fail_count += 1; _fail(f"pagination length {expected_len} wrong")

        if page1: _check_page(page1, 10)
        if page2: _check_page(page2, 3)

        # Filter by status
        for s in ["todo","in_progress","done"]:
            _, resp = self.expect(f"filter status={s}", "GET",
                                  f"/tasks?project_id={proj_id}&page=1&per_page=50&status={s}&sort=due_date",
                                  expected=200)
            ok = all(t.get("status")==s for t in (resp or {}).get("data",[]))
            if ok: self.pass_count += 1; _ok(f"filter {s} returned only {s}")
            else: self.fail_count += 1; _fail(f"filter {s} returned mixed statuses")

        # Update first task 
        if created_task_ids:
            t_id = created_task_ids[0]
            _, d = self.expect("update task fields", "PATCH", f"/tasks/{t_id}", expected=200,
                               json={"title":"T1 updated","status":"in_progress","priority":"high"})
            ok = d and d.get("title")=="T1 updated" and d.get("status")=="in_progress" and d.get("priority")=="high"
            if ok: self.pass_count += 1; _ok("task updated reflected in response")
            else: self.fail_count += 1; _fail("task update not reflected")

            # Subtasks CRUD
            _, s1 = self.expect("create subtask 1", "POST", "/subtasks", expected=201,
                                json={"task_id": t_id, "title":"S1"})
            _, s2 = self.expect("create subtask 2", "POST", "/subtasks", expected=201,
                                json={"task_id": t_id, "title":"S2"})
            _, lst = self.expect("list subtasks", "GET", f"/subtasks?task_id={t_id}", expected=200)
            ids = [x.get("id") for x in (lst or [])]
            if len(ids) >= 2: self.pass_count += 1; _ok("subtasks listed")
            else: self.fail_count += 1; _fail("subtasks list incomplete")

            # toggle + delete
            if ids:
                _, _ = self.expect("toggle subtask", "PATCH", f"/subtasks/{ids[0]}", expected=200,
                                   json={"status":"done"})
                _ , _ = self.expect("delete subtask", "DELETE", f"/subtasks/{ids[0]}", expected=204)
                _, lst2 = self.expect("list subtasks (post-delete)", "GET", f"/subtasks?task_id={t_id}", expected=200)
                if all(x.get("id") != ids[0] for x in (lst2 or [])):
                    self.pass_count += 1; _ok("subtask removed")
                else:
                    self.fail_count += 1; _fail("subtask still present after delete")

        # Ownership checks: new user B cannot access A's project
        s2 = Tester(self.base)  # separate session
        unameB, emailB, pwB = uniq_user("userB")
        s2.expect("signup B", "POST", "/auth/signup", expected=201,
                  json={"username":unameB,"email":emailB,"password":pwB})
        # forbidden/404 accepted
        s2.expect("B cannot view A's project", "GET", f"/projects/{proj_id}", allow=[401,403,404])
        s2.expect("B cannot create task for A's project", "POST", "/tasks", allow=[401,403,404],
                  json={"project_id":proj_id,"title":"bad"})

        # Delete a task + confirm
        if created_task_ids:
            victim = created_task_ids[-1]
            self.expect("delete task", "DELETE", f"/tasks/{victim}", expected=204)
            _, resp = self.expect("list tasks after delete", "GET",
                                  f"/tasks?project_id={proj_id}&page=1&per_page=50&status=all&sort=due_date",
                                  expected=200)
            ids_now = {t["id"] for t in (resp or {}).get("data",[])}
            if victim not in ids_now:
                self.pass_count += 1; _ok("task removed from listing")
            else:
                self.fail_count += 1; _fail("task still present after delete")

        # Logout + ensure protected endpoints now blocked
        self.expect("logout", "POST", "/auth/logout", expected=204)
        _, me = self.expect("auth me (after logout)", "GET", "/auth/me", expected=200)
        if me and not me.get("authenticated"):
            self.pass_count += 1; _ok("authenticated false after logout")
        else:
            self.fail_count += 1; _fail("/auth/me still authenticated after logout")
        self.expect("projects blocked when logged out", "GET", "/projects", allow=[401,403])

        # Summary
        print("\n==== SUMMARY ====")
        print(f"{GREEN}{self.pass_count} passed{RESET}, {RED}{self.fail_count} failed{RESET}")
        return 0 if self.fail_count == 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(Tester(API).run())
    except requests.exceptions.ConnectionError as e:
        _fail(f"Cannot connect to {API}. Is the Flask server running?")
        sys.exit(2)