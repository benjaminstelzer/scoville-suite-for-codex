#!/usr/bin/env python3
"""Read the current Codex model catalog through the documented stdio protocol."""
from __future__ import annotations

import argparse
import json
import math
import queue
import subprocess
import sys
import threading
import time


def list_models(command=None, timeout=30):
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError(f'--timeout={type(timeout).__name__} must be a positive finite number of seconds; use a value such as 30')
    process = subprocess.Popen(command or ['codex', 'app-server'], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
    messages = queue.Queue()
    def read():
        try:
            for line in process.stdout:
                messages.put(json.loads(line))
        except (ValueError, OSError) as error:
            messages.put(error)
        finally:
            messages.put(None)
    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    deadline = time.monotonic() + timeout
    def send(value):
        process.stdin.write(json.dumps(value) + '\n')
        process.stdin.flush()
    def rpc(identifier, method, params):
        send({'id': identifier, 'method': method, 'params': params})
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('model/list deadline exceeded')
            try:
                value = messages.get(timeout=remaining)
            except queue.Empty as error:
                raise TimeoutError('model/list deadline exceeded') from error
            if value is None:
                raise ValueError(f'app-server closed before {method} completed; start the command supplied with --command or use the Codex app-server')
            if isinstance(value, Exception):
                raise ValueError(f'app-server returned invalid JSON before {method} completed: {value}; correct the app-server response')
            if not isinstance(value, dict):
                raise ValueError(f'app-server {method} response must be a JSON object with id and result fields')
            if value.get('id') != identifier:
                continue
            if 'error' in value:
                raise ValueError(f'{method} failed: {value["error"]}')
            result = value.get('result')
            if not isinstance(result, dict):
                raise ValueError(f'{method} returned no result object')
            return result
    try:
        rpc(0, 'initialize', {'clientInfo': {'name': 'scoville_ask', 'version': '1.0.0'}})
        send({'method': 'initialized', 'params': {}})
        rows, cursors, cursor, identifier = [], set(), None, 1
        while True:
            result = rpc(identifier, 'model/list', {'limit': 100, 'includeHidden': False, 'cursor': cursor})
            data = result.get('data')
            if not isinstance(data, list):
                raise ValueError(f'model/list result.data={type(data).__name__} must be an array of model objects; check the app-server response')
            rows.extend(data)
            cursor = result.get('nextCursor')
            if cursor is None:
                break
            if not isinstance(cursor, str) or not cursor or cursor in cursors:
                raise ValueError(f'model/list result.nextCursor={type(cursor).__name__} must be a new nonempty string or null; correct the pagination cursor')
            cursors.add(cursor)
            identifier += 1
        return normalize_models(rows)
    finally:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        reader.join(timeout=1)
        process.stdin.close()
        process.stdout.close()


def normalize_models(rows):
    models = []
    seen = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f'model/list data[{index}] must be an object; correct the app-server model entry')
        model = row.get('model')
        efforts = row.get('supportedReasoningEfforts')
        if not isinstance(model, str) or not model:
            raise ValueError(f'model/list data[{index}].model must be nonempty text; correct the app-server entry')
        if model in seen:
            raise ValueError(f'model/list data[{index}].model={type(model).__name__} is duplicated; return each model once')
        if not isinstance(efforts, list):
            raise ValueError(f'model/list data[{index}].supportedReasoningEfforts must be an array; correct the app-server entry')
        values = [item.get('reasoningEffort') if isinstance(item, dict) else None for item in efforts]
        if not values or any(not isinstance(item, str) or not item for item in values):
            raise ValueError(f'model/list data[{index}].supportedReasoningEfforts must be a nonempty array of objects with nonempty reasoningEffort strings')
        seen.add(model)
        models.append({'model': model, 'efforts': values, 'default_effort': row.get('defaultReasoningEffort')})
    if not models:
        raise ValueError('model/list result.data returned no selectable models; configure at least one visible model with supported reasoning efforts')
    return {'source': 'model/list', 'models': models}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--command', nargs='+', help='explicit Codex app-server executable and arguments')
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args()
    try:
        print(json.dumps({'ok': True, **list_models(args.command, args.timeout)}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, TimeoutError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='strict')
    raise SystemExit(main())
