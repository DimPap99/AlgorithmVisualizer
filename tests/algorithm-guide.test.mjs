import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import vm from 'node:vm';
import { test } from 'node:test';

const script = await readFile(new URL('../static/Javascript/algorithm-guide.js', import.meta.url), 'utf8');
const guides = JSON.parse(await readFile(new URL('../static/data/algorithm-guides.json', import.meta.url), 'utf8'));

function page(fetcher) {
    const nodes = Object.fromEntries(['algorithm-guide', 'algorithm', 'guide-name', 'guide-time', 'guide-notation', 'guide-note', 'guide-pseudocode'].map(id => [id, {
        textContent: '', value: 'Insertion Sort', attributes: {}, listeners: {},
        setAttribute(name, value) { this.attributes[name] = value; },
        addEventListener(event, callback) { this.listeners[event] = callback; },
    }]));
    vm.runInNewContext(script, {
        URL, fetch: fetcher,
        document: {
            currentScript: { src: 'https://example.test/AlgorithmVisualizer/static/Javascript/algorithm-guide.js' },
            readyState: 'complete', getElementById: id => nodes[id],
        },
    });
    return nodes;
}

test('the guide updates pseudocode and complexity when the selected algorithm changes', async () => {
    let source;
    const nodes = page(async url => { source = String(url); return { ok: true, json: async () => guides }; });
    await new Promise(setImmediate);
    assert.equal(source, 'https://example.test/AlgorithmVisualizer/static/data/algorithm-guides.json');
    assert.equal(nodes['guide-name'].textContent, 'Insertion Sort');
    assert.equal(nodes['guide-time'].textContent, 'O(n²)');
    nodes.algorithm.value = 'Heap Sort';
    nodes.algorithm.listeners.change();
    assert.equal(nodes['guide-name'].textContent, 'Heap Sort');
    assert.equal(nodes['guide-time'].textContent, 'O(n log n)');
    assert.match(nodes['guide-pseudocode'].textContent, /SIFT_DOWN/);
    assert.equal(nodes['algorithm-guide'].attributes['aria-busy'], 'false');
});

test('failed guide downloads show a message without disabling the algorithm selector', async () => {
    const nodes = page(async () => ({ ok: false }));
    await new Promise(setImmediate);
    assert.match(nodes['guide-note'].textContent, /could not load/);
    assert.equal(nodes['algorithm-guide'].attributes['aria-busy'], 'false');
    assert.equal(nodes.algorithm.value, 'Insertion Sort');
});
