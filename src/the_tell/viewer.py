"""A local web page for watching a run: every invoice the model has answered, live.

Reads runs/<run>/results.jsonl as the run writes it, so it can be opened mid-run. Only
listens on this machine (127.0.0.1); nothing is reachable from the network.

Run:  uv run python -m the_tell.viewer --run qwen3-4b-full
Then open http://127.0.0.1:8765
"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from the_tell.generate import read_jsonl
from the_tell.prompt import user_message

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Tell: run viewer</title>
<style>
:root { --bg:#fbfaf8; --fg:#1d1d1b; --muted:#6b6b66; --line:#e4e2dd; --card:#ffffff; --ok:#2f7d4f; --bad:#b3261e; --accent:#2b5fab; }
@media (prefers-color-scheme: dark) { :root { --bg:#161615; --fg:#ecebe7; --muted:#9b9a94; --line:#33322f; --card:#1f1f1d; --ok:#5fbf86; --bad:#f0857c; --accent:#7fa8e8; } }
* { box-sizing:border-box; }
body { margin:0; font:14px/1.45 -apple-system, system-ui, sans-serif; background:var(--bg); color:var(--fg); }
header { padding:16px 20px; border-bottom:1px solid var(--line); }
h1 { margin:0 0 4px; font-size:18px; }
.sub { color:var(--muted); }
.stats { display:flex; flex-wrap:wrap; gap:24px; margin-top:12px; }
.stat b { display:block; font-size:22px; }
.bar { height:6px; background:var(--line); border-radius:3px; margin-top:12px; overflow:hidden; }
.bar div { height:100%; background:var(--accent); }
main { display:grid; grid-template-columns: minmax(0,1.1fr) minmax(0,1fr); gap:0; height:calc(100vh - 150px); }
@media (max-width: 900px) { main { grid-template-columns:1fr; height:auto; } }
.list, .detail { overflow:auto; padding:12px 20px; }
.list { border-right:1px solid var(--line); }
table { width:100%; border-collapse:collapse; }
th, td { text-align:left; padding:5px 6px; border-bottom:1px solid var(--line); white-space:nowrap; }
th { color:var(--muted); font-weight:500; position:sticky; top:0; background:var(--bg); }
tr.row { cursor:pointer; } tr.row:hover { background:var(--card); } tr.sel { outline:2px solid var(--accent); }
.ok { color:var(--ok); } .bad { color:var(--bad); font-weight:600; }
.controls { margin-bottom:8px; display:flex; gap:12px; align-items:center; color:var(--muted); }
pre { white-space:pre-wrap; background:var(--card); border:1px solid var(--line); padding:10px; border-radius:6px; font-size:12px; }
.why { color:var(--muted); font-size:12px; }
</style></head><body>
<header>
  <h1>The Tell: run viewer</h1>
  <div class="sub" id="meta">loading...</div>
  <div class="stats">
    <div class="stat"><b id="done">-</b>answered</div>
    <div class="stat"><b id="acc">-</b>right</div>
    <div class="stat"><b id="wrong">-</b>wrong</div>
    <div class="stat"><b id="conf">-</b>wrong but stated confidence 100</div>
    <div class="stat"><b id="eta">-</b>time left</div>
  </div>
  <div class="bar"><div id="prog" style="width:0"></div></div>
</header>
<main>
  <section class="list">
    <div class="controls"><label><input type="checkbox" id="onlyWrong"> only wrong answers</label><span id="count"></span></div>
    <table><thead><tr><th>case</th><th>scenario</th><th>correct</th><th>model said</th><th></th><th>stated conf.</th><th title="How sure the model was of its answer, in nines: 3 means 99.9%, 6 means 99.9999%">certainty</th></tr></thead>
    <tbody id="rows"></tbody></table>
  </section>
  <section class="detail" id="detail"><p class="sub">Click a case to see exactly what the model read and wrote.</p></section>
</main>
<script>
let state = {results: [], meta: {}}, selected = null;
const $ = id => document.getElementById(id);
// Certainty in "nines": p = 0.999 is 3 nines. Works on log-probabilities so 0.9999999 is not rounded to 1.
const nines = lp => { const doubt = -Math.expm1(lp); return doubt <= 0 ? 16 : -Math.log10(doubt); };
const best = r => Object.entries(r.outcome_logprobs).sort((a, b) => b[1] - a[1])[0];
function cell(tr, text, cls) { const td = document.createElement('td'); td.textContent = text; if (cls) td.className = cls; tr.appendChild(td); }

async function refresh() {
  state = await (await fetch('/api/state')).json();
  const rs = state.results, m = state.meta, n = rs.length, total = m.total_cases || n;
  const wrong = rs.filter(r => r.predicted !== r.label);
  $('meta').textContent = `${m.model_id || ''}  |  run: ${state.run}  |  ${total} invoices`;
  $('done').textContent = `${n} / ${total}`;
  $('acc').textContent = n ? `${(100 * (n - wrong.length) / n).toFixed(1)}%` : '-';
  $('wrong').textContent = wrong.length;
  $('conf').textContent = wrong.filter(r => r.confidence === 100).length;
  const secs = rs.map(r => r.seconds).sort((a, b) => a - b)[Math.floor(n / 2)] || 0;
  const left = (total - n) * secs;
  $('eta').textContent = n >= total ? 'finished' : `${Math.floor(left / 3600)}h ${Math.round(left % 3600 / 60)}m`;
  $('prog').style.width = `${100 * n / total}%`;
  draw();
}

function draw() {
  const only = $('onlyWrong').checked;
  const rs = state.results.filter(r => !only || r.predicted !== r.label).slice().reverse();
  $('count').textContent = `${rs.length} shown, newest first`;
  const body = $('rows'); body.replaceChildren();
  for (const r of rs) {
    const tr = document.createElement('tr'); tr.className = 'row' + (r.case_id === selected ? ' sel' : '');
    const right = r.predicted === r.label;
    cell(tr, r.case_id); cell(tr, r.scenario); cell(tr, r.label); cell(tr, r.predicted ?? '(unreadable)');
    cell(tr, right ? 'right' : 'WRONG', right ? 'ok' : 'bad');
    cell(tr, r.confidence ?? '-'); cell(tr, nines(best(r)[1]).toFixed(1));
    tr.onclick = () => show(r.case_id);
    body.appendChild(tr);
  }
}

async function show(id) {
  selected = id; draw();
  const d = await (await fetch('/api/case/' + encodeURIComponent(id))).json();
  const r = d.result, right = r.predicted === r.label;
  const box = $('detail'); box.replaceChildren();
  const h = document.createElement('h2'); h.textContent = `${id}: ${right ? 'right' : 'WRONG'}`; h.className = right ? 'ok' : 'bad'; box.appendChild(h);
  const p = document.createElement('p'); p.textContent = `Correct: ${r.label} (${r.scenario}, ${r.difficulty}).  Model said: ${r.predicted ?? '(unreadable)'}.  ${r.prompt_tokens} prompt tokens, ${r.seconds}s.`; box.appendChild(p);
  const h3 = document.createElement('h3'); h3.textContent = 'How likely the model thought each outcome was'; box.appendChild(h3);
  const t = document.createElement('table');
  const head = document.createElement('tr'); ['outcome', 'probability', 'log-probability'].forEach(x => { const th = document.createElement('th'); th.textContent = x; head.appendChild(th); }); t.appendChild(head);
  for (const [k, lp] of Object.entries(r.outcome_logprobs).sort((a, b) => b[1] - a[1])) {
    const tr = document.createElement('tr');
    cell(tr, k + (k === r.label ? '  (correct)' : ''), k === r.label ? 'ok' : '');
    cell(tr, Math.exp(lp).toExponential(2)); cell(tr, lp.toFixed(3)); t.appendChild(tr);
  }
  box.appendChild(t);
  const w = document.createElement('p'); w.className = 'why'; w.textContent = 'Read just before the model wrote its answer. The probe in step 4 reads the model’s internal state at the same moment.'; box.appendChild(w);
  for (const [title, text] of [['Model reply', r.raw], ['What the model read (after the fixed system prompt)', d.user_message]]) {
    const h = document.createElement('h3'); h.textContent = title; box.appendChild(h);
    const pre = document.createElement('pre'); pre.textContent = text; box.appendChild(pre);
  }
}

$('onlyWrong').onchange = draw;
refresh(); setInterval(refresh, 4000);
</script></body></html>
"""


def make_handler(run_dir: Path, cases_by_id: dict):
    results_path = run_dir / "results.jsonl"
    meta_path = run_dir / "metadata.json"

    def load_results() -> list[dict]:
        if not results_path.exists():
            return []
        return [json.loads(l) for l in results_path.read_text().splitlines() if l.strip()]

    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, kind: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, status: int = 200) -> None:
            self._send(json.dumps(obj).encode(), "application/json", status)

        def do_GET(self) -> None:
            if self.path == "/":
                self._send(PAGE.encode(), "text/html; charset=utf-8")
            elif self.path == "/api/state":
                meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
                results = [{k: v for k, v in r.items() if k != "raw"} for r in load_results()]
                self._json({"run": run_dir.name, "meta": meta, "results": results})
            elif self.path.startswith("/api/case/"):
                case_id = self.path.removeprefix("/api/case/")
                result = next((r for r in load_results() if r["case_id"] == case_id), None)
                if result is None or case_id not in cases_by_id:
                    self._json({"error": "unknown case"}, 404)
                else:
                    self._json({"result": result, "user_message": user_message(cases_by_id[case_id])})
            else:
                self._json({"error": "not found"}, 404)

        def log_message(self, *args) -> None:  # keep the terminal quiet
            pass

    return Handler


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--cases", type=Path, default=Path("data/generated/cases.jsonl"))
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    cases_by_id = {c.case_id: c for c in read_jsonl(args.cases)}
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(Path("runs") / args.run, cases_by_id))
    print(f"Watching runs/{args.run}. Open http://127.0.0.1:{args.port}  (Ctrl+C to stop)", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
