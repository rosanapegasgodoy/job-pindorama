"""Painel local (tools/painel.py): dados, segurança do servidor e da página."""

import base64
import http.client
import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import painel  # noqa: E402
import painel_perfil  # noqa: E402

RESULTS = {
    "meta": {"date": "2026-10-22"},
    "new": [
        {"title": "Product Manager", "company": "Zeta", "url": "https://zeta.gupy.io/jobs/1", "date": "2026-10-20",
         "portal": "gupy-search", "signals": {"verdict": "posting_signals: none"}},
        {"title": "Product Owner", "company": "Omega", "url": "https://remotar.com.br/job/2", "date": "2026-10-19",
         "portal": "remotar-search", "signals": {"verdict": "posting_signals: none"}},
    ],
}


class Data(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.seen = self.dir / "seen_jobs.json"
        self.tracker = self.dir / "tracker.csv"

    def tearDown(self):
        self.tmp.cleanup()

    def test_mark_uses_the_search_file_not_the_browser(self):
        out = painel.mark(RESULTS, ["https://zeta.gupy.io/jobs/1", "https://evil.example/x"], "interesse", self.seen)
        self.assertEqual((out["added"], out["missing"]), (1, ["https://evil.example/x"]))
        entry = next(iter(json.loads(self.seen.read_text(encoding="utf-8"))["seen"].values()))
        self.assertEqual((entry["title"], entry["fit"], entry["status"], entry["source"]),
                         ("Product Manager", "medium", "new", "painel"))

    def test_discard_is_low_and_skipped(self):
        painel.mark(RESULTS, ["https://remotar.com.br/job/2"], "descartar", self.seen)
        entry = next(iter(json.loads(self.seen.read_text(encoding="utf-8"))["seen"].values()))
        self.assertEqual((entry["fit"], entry["status"]), ("low", "skipped"))

    def test_unknown_decision(self):
        with self.assertRaises(ValueError):
            painel.mark(RESULTS, [], "candidatar", self.seen)

    def test_marked_jobs_leave_the_list_and_only_interest_is_saved(self):
        painel.mark(RESULTS, ["https://zeta.gupy.io/jobs/1"], "interesse", self.seen)
        painel.mark(RESULTS, ["https://remotar.com.br/job/2"], "descartar", self.seen)
        self.assertEqual(painel.unseen(RESULTS, self.seen, self.tracker)["new"], [])
        self.assertEqual([s["title"] for s in painel.saved(self.seen)], ["Product Manager"])
        self.assertEqual(painel.unseen(None, self.seen, self.tracker), {"meta": None, "new": []})

    def test_applications_read_the_tracker(self):
        self.tracker.write_text("date,company,role,status\n2026-10-01,Zeta,PM,applied\n", encoding="utf-8")
        self.assertEqual(painel.applications(self.tracker), [{"date": "2026-10-01", "company": "Zeta", "role": "PM", "status": "applied"}])
        self.assertEqual(painel.applications(self.dir / "nao-existe.csv"), [])

    def test_priorities_skip_template_placeholders(self):
        q = self.dir / "q.md"
        q.write_text("### Prioridade 1: X\n```\ngupy-search: -q \"pm\"\nvagas-search: -q \"pm\"\n```\n"
                     "### Prioridade 2: Y\n```\ngupy-search: -q \"[YOUR_ROLE]\"\n```\n", encoding="utf-8")
        self.assertEqual(painel.priorities(q), [{"priority": 1, "queries": 2, "portals": 2}])

    def test_search_file_lives_outside_the_repo(self):
        self.assertFalse(str(painel.results_path().resolve()).startswith(str(ROOT.resolve())))

    def test_claude_drafting_needs_a_saved_evaluation(self):
        url = "https://zeta.gupy.io/jobs/1?a=1&b=2"
        prompt = painel.claude_prompt(url, "avaliar", self.dir)
        self.assertIn(url, prompt)
        self.assertIn(f"`{painel.PYTHON} tools/posting_guard.py", prompt)
        self.assertNotIn("{python}", prompt)
        with self.assertRaises(ValueError):
            painel.claude_prompt(url, "redigir", self.dir)
        with self.assertRaises(ValueError):
            painel.claude_prompt(url, "apagar", self.dir)
        painel.claude_file(url, "avaliar", self.dir).write_text("## Avaliação\nNota 63", encoding="utf-8")
        drafting = painel.claude_prompt(url, "redigir", self.dir)
        self.assertIn("<AVALIACAO>\n## Avaliação\nNota 63\n</AVALIACAO>", drafting)
        self.assertIn(f"`{painel.PYTHON} tools/compile_doc.py", drafting)
        self.assertNotIn("{python}", drafting)
        self.assertEqual(painel.claude_answers(url, self.dir), {"avaliar": "## Avaliação\nNota 63", "redigir": None})

    def test_profile_prompt_needs_a_document_and_carries_the_form_as_data(self):
        docs, answers = self.dir / "documents", self.dir / "respostas.json"
        with self.assertRaises(ValueError):
            painel.claude_prompt(painel.PERFIL_KEY, "perfil", self.dir, answers, docs)
        painel_perfil.save_upload("cv", "cv.pdf", base64.b64encode(b"%PDF-1.4 x").decode(), docs)
        self.assertIn("(formulário em branco)", painel.claude_prompt(painel.PERFIL_KEY, "perfil", self.dir, answers, docs))
        painel_perfil.save_answers({"genero": "neutro", "cargos": "PM\nPO"}, answers)
        prompt = painel.claude_prompt(painel.PERFIL_KEY, "perfil", self.dir, answers, docs)
        self.assertIn("<FORMULARIO>\nNos textos em português, escrever no: neutro\nCargos a buscar, um por linha: PM; PO\n</FORMULARIO>", prompt)
        self.assertIn("/setup pelo Caminho A", prompt)
        self.assertIn("Não grave nos arquivos do perfil", prompt)
        self.assertIn("documents/perfil/proposta/claude/skills/job-application-assistant/01-candidate-profile.md", prompt)

    def test_claude_answer_files_are_named_by_hash_inside_the_folder(self):
        f = painel.claude_file("https://x/../../etc", "avaliar", self.dir)
        self.assertEqual(f.parent, self.dir)
        self.assertRegex(f.name, r"^[0-9a-f]{16}_avaliacao\.md$")

    def test_claude_command_keeps_the_prompt_off_the_command_line(self):
        cmd = painel.claude_command("claude", "avaliar")
        self.assertEqual(cmd[:2], ["claude", "-p"])
        self.assertTrue(all("http" not in part for part in cmd))
        self.assertIn(str(painel.CLAUDE_SETTINGS_PERFIL), painel.claude_command("claude", "perfil"))
        settings = json.loads(painel.CLAUDE_SETTINGS.read_text(encoding="utf-8"))
        bash = [r for r in settings["permissions"]["allow"] if r.startswith("Bash")]
        self.assertTrue(bash)
        self.assertTrue(all("tools/compile_doc.py:*)" in r for r in bash), bash)


class Server(unittest.TestCase):
    """O servidor de verdade, numa porta livre; nenhum pedido aqui grava nada."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.token = "t0k3n"
        job = painel.SearchJob(Path(cls.tmp.name) / "busca.json")
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), None)
        cls.port = cls.server.server_address[1]
        tmp = Path(cls.tmp.name)
        cls.documents = tmp / "documents"
        cls.profile_root = tmp / "repo"
        (cls.profile_root / "cv").mkdir(parents=True)
        (cls.profile_root / "cv" / "main_example.tex").write_text("velho\n", encoding="utf-8")
        claude = painel.ClaudeJob(tmp / "claude", claude_bin="claude-que-nao-roda",
                                  documents=cls.documents, answers=tmp / "respostas.json",
                                  staging=tmp / "proposta", profile_root=cls.profile_root)
        # Sem rede nos testes: a checagem de privacidade de verdade chama o `gh`, que no CI
        # pode demorar mais que o tempo de resposta que o teste espera.
        cls.server.RequestHandlerClass = painel.make_handler(cls.token, job, {f"127.0.0.1:{cls.port}"}, claude,
                                                             privacy_check=lambda: {"status": "local", "repo": None})
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request(method, path, body=json.dumps(body) if body is not None else None, headers=headers or {})
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        conn.close()
        return res.status, data, res

    def test_page_carries_the_token_and_a_csp(self):
        status, html, res = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn('content="t0k3n"', html)
        self.assertIn("frame-ancestors 'none'", res.getheader("Content-Security-Policy"))

    def test_writes_need_the_token(self):
        status, _, _ = self.request("POST", "/api/mark", {"urls": [], "decision": "interesse"})
        self.assertEqual(status, 403)
        status, _, _ = self.request("POST", "/api/search", {"priorities": [1]}, {"X-Painel-Token": "errado"})
        self.assertEqual(status, 403)

    def test_other_host_names_are_refused(self):
        status, _, _ = self.request("GET", "/api/status", headers={"Host": "evil.example:80"})
        self.assertEqual(status, 403)

    def test_bad_search_requests(self):
        h = {"X-Painel-Token": self.token, "Content-Type": "application/json"}
        self.assertEqual(self.request("POST", "/api/search", {"priorities": []}, h)[0], 400)
        self.assertEqual(self.request("POST", "/api/search", {"priorities": [1], "jobage": 999}, h)[0], 400)
        self.assertEqual(self.request("POST", "/api/mark", {"urls": [], "decision": "x"}, h)[0], 400)
        self.assertEqual(self.request("POST", "/api/mark", ["não", "é", "objeto"], h)[0], 400)

    def test_claude_only_for_jobs_marked_here(self):
        h = {"X-Painel-Token": self.token, "Content-Type": "application/json"}
        status, data, _ = self.request("POST", "/api/claude", {"url": "https://evil.example/x", "step": "avaliar"}, h)
        self.assertEqual(status, 400)
        self.assertIn("Me interessam", json.loads(data)["error"])
        self.assertEqual(self.request("POST", "/api/claude", {"url": "x", "step": "avaliar"})[0], 403)

    def test_profile_upload_and_form(self):
        h = {"X-Painel-Token": self.token, "Content-Type": "application/json"}
        pdf = {"kind": "cv", "name": "cv.pdf", "data": base64.b64encode(b"%PDF-1.4 x").decode()}
        self.assertEqual(self.request("POST", "/api/upload", pdf)[0], 403)
        status, data, _ = self.request("POST", "/api/upload", pdf, h)
        self.assertEqual((status, json.loads(data)["saved"]), (200, "cv.pdf"))
        self.assertTrue((self.documents / "cv" / "cv.pdf").is_file())
        self.assertEqual(self.request("POST", "/api/upload", {**pdf, "name": "cv.exe"}, h)[0], 400)
        status, data, _ = self.request("POST", "/api/profile", {"genero": "neutro", "extra": "x"}, h)
        self.assertEqual((status, json.loads(data)["answers"]), (200, {"genero": "neutro"}))
        status, data, _ = self.request("GET", "/api/profile")
        profile = json.loads(data)
        self.assertEqual(profile["answers"], {"genero": "neutro"})
        self.assertEqual([f["name"] for f in profile["files"]["cv"]], ["cv.pdf"])
        self.assertEqual(profile["privacy"], {"status": "local", "repo": None})

    def test_profile_proposal_is_applied_only_on_request(self):
        h = {"X-Painel-Token": self.token, "Content-Type": "application/json"}
        staged = Path(self.tmp.name) / "proposta" / "cv" / "main_example.tex"
        staged.parent.mkdir(parents=True)
        staged.write_text("novo\n", encoding="utf-8")
        files = json.loads(self.request("GET", "/api/profile")[1])["proposal"]["files"]
        self.assertEqual([(f["path"], f["added"], f["removed"]) for f in files], [("cv/main_example.tex", 1, 1)])
        self.assertEqual(self.request("POST", "/api/profile-apply", {})[0], 403)
        self.assertEqual(self.request("POST", "/api/profile-apply", {"paths": "tudo"}, h)[0], 400)
        status, data, _ = self.request("POST", "/api/profile-apply", {}, h)
        self.assertEqual((status, json.loads(data)["applied"]), (200, ["cv/main_example.tex"]))
        self.assertEqual((self.profile_root / "cv" / "main_example.tex").read_text(encoding="utf-8"), "novo\n")

    def test_only_uploads_get_the_big_body_limit(self):
        self.assertEqual(painel.body_limit("/api/upload"), painel.MAX_UPLOAD_BODY)
        self.assertEqual(painel.body_limit("/api/upload?x=1"), painel.MAX_UPLOAD_BODY)
        for path in ("/api/profile", "/api/claude", "/api/uploadX"):
            self.assertEqual(painel.body_limit(path), painel.MAX_BODY)

    def test_results_empty_before_a_search(self):
        status, data, _ = self.request("GET", "/api/results")
        self.assertEqual((status, json.loads(data)), (200, {"meta": None, "new": []}))


class Page(unittest.TestCase):
    def test_job_data_is_never_inserted_as_html(self):
        page = painel.PAGE.read_text(encoding="utf-8")
        for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            self.assertNotIn(sink, page)
        self.assertIn('rel: "noopener noreferrer"', page)


if __name__ == "__main__":
    unittest.main()
