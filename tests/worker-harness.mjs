// Supply the Web Worker messaging API in Node to exercise the actual exported worker.
import { parentPort } from 'node:worker_threads';
import { readFile } from 'node:fs/promises';

const networkFetch = globalThis.fetch;
globalThis.fetch = async (url, options) => {
    if (String(url).startsWith('file:')) return new Response(await readFile(new URL(url)));
    return networkFetch(url, options);
};
globalThis.self = { postMessage: message => parentPort.postMessage(message) };
await import('../dist/static/Javascript/pyodide-worker.mjs');
parentPort.on('message', data => self.onmessage({ data }));
