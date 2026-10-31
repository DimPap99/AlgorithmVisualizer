import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { test } from 'node:test';
import { Worker } from 'node:worker_threads';
import { loadPyodide } from 'pyodide';
import { createEngine } from '../static/Javascript/python-engine.mjs';

test('exported Python algorithms run through the real WebAssembly runtime', { timeout: 60000 }, async t => {
    const engine = await createEngine({
        loadPyodide,
        sourceURL: new URL('../dist/python/sources.json', import.meta.url),
        fetcher: async url => new Response(await readFile(url)),
    });
    const original = [7, -2, 3, 3, 0, 11, 1.5, -2];
    for (const algorithm of ['Insertion Sort', 'Quick Sort', 'Bubble Sort', 'Selection Sort', 'Merge Sort', 'Heap Sort', 'Shell Sort', 'Cocktail Shaker Sort', 'Comb Sort']) {
        const array = [...original];
        const { swaps } = engine.run('/SortArray', { algorithm, array });
        for (const [left, right] of swaps) [array[left], array[right]] = [array[right], array[left]];
        assert.deepEqual(array, [...original].sort((a, b) => a - b), algorithm);
    }
    await t.test('weighted shortest paths agree', () => {
        for (const algorithm of ['Dijkstra', 'A* Search', 'Bidirectional Dijkstra', 'Bellman-Ford']) {
            const result = engine.run('/runAlgo', { algorithm, start: '0-0', end: '0-2', weights: { '0-1': 50 } });
            assert.equal(result.paths[0].cost, 4, algorithm);
        }
    });
    await t.test('multiple paths and unweighted searches work', () => {
        const result = engine.run('/runAlgo', { algorithm: "Yen's K Shortest Paths", start: '0-0', end: '2-3', params: { paths: 3 } });
        assert.equal(result.paths.length, 3);
        assert.ok(result.paths.every((path, index) => index === 0 || path.cost >= result.paths[index - 1].cost));
        for (const algorithm of ['Greedy Best-First Search', 'Breadth-First Search', 'Depth-First Search']) {
            assert.ok(engine.run('/runAlgo', { algorithm, start: '0-0', end: '2-3' }).paths.length);
        }
    });
    await t.test('negative cycles, distributions, errors, and repeated calls work', () => {
        const result = engine.run('/runAlgo', { algorithm: 'Bellman-Ford', start: '0-0', end: '0-2', weights: { '0-1': -3 } });
        assert.ok(result.cycle.cost < 0);
        for (const distribution of ['Uniform', 'Gaussian', 'Exponential', 'Bernoulli']) {
            const { weights } = engine.run('/generateWeights', { distribution });
            assert.equal(Object.keys(weights).length, 1500);
            assert.ok(Object.values(weights).every(weight => weight >= 1 && weight <= 99));
        }
        assert.throws(() => engine.run('/SortArray', { algorithm: 'Unknown', array: [] }), /Unknown sort algorithm/);
        assert.equal(engine.run('/runAlgo', { algorithm: 'Dijkstra', start: '0-0', end: '0-2' }).paths[0].cost, 2);
    });
});

test('the packaged worker loads its local runtime and answers a request', { timeout: 60000 }, async () => {
    const worker = new Worker(new URL('./worker-harness.mjs', import.meta.url));
    try {
        await new Promise((resolve, reject) => {
            worker.on('error', reject);
            worker.on('message', data => {
                if (data.type === 'fatal' || data.error) return reject(new Error(data.error));
                if (data.type === 'ready') worker.postMessage({ id: 1, action: '/SortArray', data: { algorithm: 'Heap Sort', array: [3, 1, 2] } });
                if (data.type === 'result') {
                    assert.equal(data.id, 1);
                    assert.ok(data.result.swaps.length);
                    resolve();
                }
            });
        });
    } finally {
        await worker.terminate();
    }
});
