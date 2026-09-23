"""Explicitly authorized local Python execution. This runner is NOT a sandbox."""
from __future__ import annotations
import os
import platform
import subprocess
import sys
from .model import identifier, make_node, node_payload, now, pretty, require, WorkspaceError
from .store import Store, atomic_write, file_hash, safe_path


def run_method(store: Store, method_id: str, actor: str, *, allow_exec: bool = False, timeout: int = 60) -> dict:
    require(allow_exec, 'Read the script first; --allow-exec executes local code outside a sandbox.')
    require(1 <= timeout <= 3600, 'Timeout must be 1–3600 seconds.')
    method = store.node(method_id)
    require(method['kind'] == 'method' and method['status'] == 'confirmed', 'Run a confirmed method node.')
    data = method['data']
    script = data.get('script', '')
    require(script.startswith('workspace/methods/') and script.endswith('.py'), 'Method script must be a local workspace/methods/*.py file.')
    script_path = safe_path(store.root, script)
    require(script_path.is_file(), 'Script missing.')
    inputs, outputs, args = data.get('inputs', []), data.get('outputs', []), data.get('args', [])
    require(isinstance(inputs, list) and inputs and all(isinstance(p, str) for p in inputs), 'Declare input paths.')
    require(isinstance(outputs, list) and outputs and all(isinstance(p, str) for p in outputs), 'Declare output paths.')
    require(len(outputs) == len(set(outputs)) and len(inputs) == len(set(inputs)), 'Duplicate input/output paths.')
    require(isinstance(args, list) and all(isinstance(a, str) for a in args), 'args must be strings.')
    before = {}
    for path in inputs:
        target = safe_path(store.root, path)
        require(path.startswith('workspace/') and target.is_file(), 'Input is missing or outside workspace: ' + path)
        before[path] = file_hash(target)
    for path in outputs:
        require(path.startswith(('workspace/results/', 'manuscript/figures/', 'manuscript/supplementary/')), 'Output must be in results, manuscript figures, or supplementary.')
        target = safe_path(store.root, path)
        require(not target.exists(), 'Output already exists; use fresh/versioned paths so stale artifacts cannot masquerade as a new result.')
        target.parent.mkdir(parents=True, exist_ok=True)
    code = {script: file_hash(script_path)}
    env = {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'SYSTEMROOT', 'TEMP', 'TMP', 'LANG')}
    env.update(PYTHONHASHSEED=str(data.get('seed', 0)), PYTHONIOENCODING='utf-8')
    started = now()
    try:
        process = subprocess.run([sys.executable, str(script_path), *args], cwd=store.root, env=env,
                                 capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise WorkspaceError('Method timed out. No successful result recorded; inspect any partial files before retrying.') from exc
    run_id = identifier('RUN')
    log_path = 'workspace/reports/' + run_id + '-execution.json'
    atomic_write(safe_path(store.root, log_path), pretty({'started': started, 'exit_code': process.returncode,
                 'stdout_tail': process.stdout[-16000:], 'stderr_tail': process.stderr[-16000:], 'code': code, 'inputs': before}))
    require(process.returncode == 0, 'Method failed; inspect ' + log_path + '. No successful result recorded.')
    require(all(file_hash(safe_path(store.root, p)) == h for p, h in {**before, **code}.items()), 'Inputs/code changed while running; result not accepted.')
    after = {path: file_hash(safe_path(store.root, path)) for path in outputs}
    require(all(after.values()), 'Declared output missing; no successful result recorded.')
    result = make_node(run_id, 'result', 'Executed: ' + method['title'], {
        'method': method_id, 'method_hash': node_payload(method), 'inputs': before, 'outputs': after, 'code': code,
        'python': sys.version.split()[0], 'platform': platform.platform(), 'seed': data.get('seed'), 'args': args,
        'started_at': started, 'finished_at': now(), 'exit_code': 0, 'log': log_path,
        'boundary': 'Local execution receipt; scientific design and statistical interpretation still need review.'
    }, [method_id], 'confirmed')
    store.state['nodes'][run_id] = result
    store.event('method.executed', actor, {'id': run_id, 'method': method_id, 'result_hash': node_payload(result)})
    store.commit()
    return result
