import assert from 'node:assert/strict';
import { test } from 'node:test';
import { PythonWorkerClient } from '../static/Javascript/runtime-client.mjs';

class FakeWorker {
    static instances = [];
    constructor() { FakeWorker.instances.push(this); }
    postMessage(data) { this.request = data; }
    emit(data) { this.onmessage({ data }); }
    terminate() { this.terminated = true; }
}

test('requests wait for startup and return their matching result', async () => {
    const client = new PythonWorkerClient('worker.mjs', { WorkerClass: FakeWorker });
    try {
        const worker = client.worker;
        const result = client.request('/SortArray', { array: [2, 1] });
        assert.equal(worker.request, undefined);
        worker.emit({ type: 'ready' });
        await Promise.resolve();
        worker.emit({ type: 'result', id: worker.request.id, result: { swaps: [[0, 1]] } });
        assert.deepEqual(await result, { swaps: [[0, 1]] });
    } finally { client.dispose(); }
});

test('stop terminates computation, rejects the old request, and starts a new worker', async () => {
    const client = new PythonWorkerClient('worker.mjs', { WorkerClass: FakeWorker });
    try {
        const oldWorker = client.worker;
        oldWorker.emit({ type: 'ready' });
        const result = client.request('/runAlgo', {});
        await Promise.resolve();
        client.cancel();
        await assert.rejects(result, /cancelled/);
        assert.equal(oldWorker.terminated, true);
        assert.notEqual(client.worker, oldWorker);
        oldWorker.emit({ type: 'ready' });
        client.worker.emit({ type: 'ready' });
        await client.ready;
    } finally { client.dispose(); }
});

test('startup failures can be retried', async () => {
    const client = new PythonWorkerClient('worker.mjs', { WorkerClass: FakeWorker });
    try {
        client.worker.emit({ type: 'fatal', error: 'Source download failed' });
        await assert.rejects(client.ready, /Source download failed/);
        client.restart();
        client.worker.emit({ type: 'ready' });
        await client.ready;
    } finally { client.dispose(); }
});

test('startup timeouts clean up the worker', async () => {
    const client = new PythonWorkerClient('worker.mjs', { WorkerClass: FakeWorker, timeout: 10 });
    const worker = client.worker;
    await assert.rejects(client.ready, /timed out/);
    assert.equal(worker.terminated, true);
});
