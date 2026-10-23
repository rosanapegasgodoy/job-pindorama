"""A aba "Meu perfil" do painel (tools/painel_perfil.py): formulário, documentos e privacidade."""

import base64
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import painel_perfil  # noqa: E402

PDF = base64.b64encode(b"%PDF-1.7\n...").decode()


class Form(unittest.TestCase):
    def test_only_known_fields_in_the_right_shape(self):
        got = painel_perfil.clean_answers({
            "genero": "feminino", "cidade": "  Recife - PE ", "cargos": "PM\n\n PO \n",
            "senioridade": ["senior", "inventado", "pleno"], "regimes": "CLT", "idioma_cv": "alemão",
            "desconhecido": "x", "motivacao": "", "idiomas": ["Inglês - fluente", 3],
        })
        self.assertEqual(got, {"genero": "feminino", "cidade": "Recife - PE", "cargos": ["PM", "PO"],
                               "senioridade": ["pleno", "senior"], "regimes": ["CLT"], "idiomas": ["Inglês - fluente"]})

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "perfil" / "respostas.json"
            painel_perfil.save_answers({"modelo": ["remoto"], "pretensao_clt": "R$ 9 mil"}, path)
            self.assertEqual(painel_perfil.load_answers(path), {"modelo": ["remoto"], "pretensao_clt": "R$ 9 mil"})
            self.assertEqual(painel_perfil.load_answers(Path(tmp) / "nao-existe.json"), {})

    def test_format_follows_the_form_order(self):
        text = painel_perfil.format_answers({"regimes": ["CLT", "PJ"], "cidade": "Natal - RN"})
        self.assertEqual(text, "Cidade e UF: Natal - RN\nRegimes aceitos: CLT; PJ")

    def test_answers_file_is_ignored_by_git(self):
        self.assertIn("documents/perfil/**", (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines())


class Documents(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_name_is_only_a_pdf_basename(self):
        self.assertEqual(painel_perfil.safe_name("C:\\Users\\x\\Currículo Ana.PDF"), "Currículo Ana.pdf")
        self.assertEqual(painel_perfil.safe_name("../../etc/cv;rm.pdf"), "cv_rm.pdf")
        for bad in ("cv.docx", ".pdf", "cv", "../"):
            with self.assertRaises(ValueError, msg=bad):
                painel_perfil.safe_name(bad)

    def test_upload_lands_in_its_folder_and_must_be_a_pdf(self):
        self.assertEqual(painel_perfil.save_upload("cv", "../cv.pdf", PDF, self.base), "cv.pdf")
        self.assertTrue((self.base / "cv" / "cv.pdf").is_file())
        for kind, data in (("cv", base64.b64encode(b"MZ executable").decode()), ("cv", "não-é-base64"),
                           ("diplomas", PDF)):
            with self.assertRaises(ValueError, msg=kind):
                painel_perfil.save_upload(kind, "x.pdf", data, self.base)
        self.assertTrue(painel_perfil.has_documents(self.base))

    def test_too_big_is_refused(self):
        big = base64.b64encode(b"%PDF-" + b"0" * painel_perfil.MAX_UPLOAD).decode()
        with self.assertRaises(ValueError):
            painel_perfil.save_upload("cv", "cv.pdf", big, self.base)

    def test_remove_only_listed_files(self):
        painel_perfil.save_upload("linkedin", "perfil.pdf", PDF, self.base)
        (self.base / "segredo.txt").write_text("x", encoding="utf-8")
        for name in ("../segredo.txt", "outro.pdf"):
            with self.assertRaises(ValueError):
                painel_perfil.remove_upload("linkedin", name, self.base)
        painel_perfil.remove_upload("linkedin", "perfil.pdf", self.base)
        self.assertEqual(painel_perfil.list_uploads(self.base), {"cv": [], "linkedin": []})
        self.assertFalse(painel_perfil.has_documents(self.base))


class Privacy(unittest.TestCase):
    def test_github_remotes(self):
        for url in ("https://github.com/ana/minha-busca.git", "git@github.com:ana/minha-busca.git",
                    "https://github.com/ana/minha-busca", "ssh://git@github.com/ana/minha-busca.git"):
            self.assertEqual(painel_perfil.github_repo(url), "ana/minha-busca", url)
        for url in ("https://gitlab.com/ana/x.git", "https://github.com.evil.com/ana/x", "https://evil.com/github.com/ana/x"):
            self.assertIsNone(painel_perfil.github_repo(url), url)

    def test_public_or_unknown_needs_confirmation(self):
        self.assertTrue(painel_perfil.needs_confirmation({"status": "publico"}))
        self.assertTrue(painel_perfil.needs_confirmation({"status": "desconhecido"}))
        for status in ("privado", "local", "outro"):
            self.assertFalse(painel_perfil.needs_confirmation({"status": status}))

    def test_profile_ready_reads_the_template_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / "CLAUDE.md"
            md.write_text("# Assistente de candidaturas de [YOUR_NAME]\n", encoding="utf-8")
            self.assertFalse(painel_perfil.profile_ready(md))
            md.write_text("# Assistente de candidaturas de Ana\n", encoding="utf-8")
            self.assertTrue(painel_perfil.profile_ready(md))
            self.assertFalse(painel_perfil.profile_ready(Path(tmp) / "nao-existe.md"))


class Proposal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "repo"
        self.staging = self.root / "documents" / "perfil" / "proposta"
        skills = self.root / ".claude" / "skills" / "job-application-assistant"
        skills.mkdir(parents=True)
        (self.root / "CLAUDE.md").write_bytes(b"# Perfil\r\nNome: [YOUR_NAME]\r\n")
        (skills / "01-candidate-profile.md").write_text("# Perfil\nsem nada\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def stage(self, rel, text):
        path = self.staging / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_dot_claude_becomes_claude_and_back(self):
        rel = ".claude/skills/job-application-assistant/01-candidate-profile.md"
        self.assertEqual(painel_perfil.staging_name(rel), "claude/skills/job-application-assistant/01-candidate-profile.md")
        self.assertEqual(painel_perfil.target_name(painel_perfil.staging_name(rel)), rel)
        self.assertEqual(painel_perfil.staging_name("CLAUDE.md"), "CLAUDE.md")

    def test_diff_ignores_line_endings_and_files_outside_the_profile(self):
        self.stage("CLAUDE.md", "# Perfil\nNome: Ana\n")
        self.stage("claude/skills/job-application-assistant/01-candidate-profile.md", "# Perfil\nsem nada\n")
        self.stage("claude/settings.json", "{}")
        self.stage("tools/painel.py", "x")
        got = painel_perfil.proposal(self.root, self.staging)
        self.assertEqual([f["path"] for f in got["files"]], ["CLAUDE.md"])
        self.assertEqual((got["files"][0]["added"], got["files"][0]["removed"]), (1, 1))
        self.assertIn("+Nome: Ana", got["files"][0]["diff"])
        self.assertEqual(sorted(got["ignored"]), ["claude/settings.json", "tools/painel.py"])

    def test_apply_keeps_crlf_and_clears_the_proposal(self):
        self.stage("CLAUDE.md", "# Perfil\nNome: Ana\n")
        self.stage("claude/skills/job-scraper/search-queries.md", "### Prioridade 1\n")
        applied = painel_perfil.apply_proposal(None, self.root, self.staging)
        self.assertEqual(sorted(applied), [".claude/skills/job-scraper/search-queries.md", "CLAUDE.md"])
        self.assertEqual((self.root / "CLAUDE.md").read_bytes(), b"# Perfil\r\nNome: Ana\r\n")
        self.assertTrue((self.root / ".claude" / "skills" / "job-scraper" / "search-queries.md").is_file())
        self.assertFalse(self.staging.exists())

    def test_apply_only_the_chosen_files(self):
        self.stage("CLAUDE.md", "# Perfil\nNome: Ana\n")
        self.stage("cv/main_example.tex", "novo")
        self.assertEqual(painel_perfil.apply_proposal(["cv/main_example.tex"], self.root, self.staging),
                         ["cv/main_example.tex"])
        self.assertEqual([f["path"] for f in painel_perfil.proposal(self.root, self.staging)["files"]], ["CLAUDE.md"])
        painel_perfil.discard_proposal(self.staging)
        self.assertEqual(painel_perfil.proposal(self.root, self.staging), {"files": [], "ignored": []})
        self.assertIn(b"[YOUR_NAME]", (self.root / "CLAUDE.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
