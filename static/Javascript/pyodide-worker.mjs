import { loadPyodide } from '../../runtime/pyodide.mjs';
import { createEngine } from './python-engine.mjs';

const engine = createEngine({
    loadPyodide,
    indexURL: new URL('../../runtime/', import.meta.url).href,
    sourceURL: new URL('../../python/sources.json', import.meta.url).href,
});

engine.then(() => self.postMessage({ type: 'ready' })).catch(error => {
    self.postMessage({ type: 'fatal', error: error.message });
});

self.onmessage = async ({ data: { id, action, data } }) => {
    try {
        const runtime = await engine;
        self.postMessage({ type: 'result', id, result: runtime.run(action, data) });
    } catch (error) {
        self.postMessage({ type: 'result', id, error: error.message });
    }
};
