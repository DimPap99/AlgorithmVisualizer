// The same engine is used by the browser worker and the Node/WASM integration tests.
export async function createEngine({ loadPyodide, indexURL, sourceURL, fetcher = fetch }) {
    const sourcesPromise = fetcher(sourceURL, { cache: 'no-cache' }).then(response => {
        if (!response.ok) throw new Error(`Could not load the algorithm source (${response.status}).`);
        return response.json();
    });
    // The Node loader expects a filesystem path; browser workers use HTTP URLs.
    const runtimeIndex = String(indexURL || '').startsWith('file:')
        ? decodeURIComponent(new URL(indexURL).pathname).replace(/^\/([A-Za-z]:\/)/, '$1')
        : indexURL;
    const [python, sources] = await Promise.all([loadPyodide({ indexURL: runtimeIndex }), sourcesPromise]);
    python.FS.mkdirTree('/visualizer/Algorithms');
    for (const [filename, source] of Object.entries(sources)) {
        if (!/^(?:Algorithms\/)?[A-Za-z_][A-Za-z0-9_]*\.py$/.test(filename)) {
            throw new Error('Unexpected filename in the algorithm source bundle.');
        }
        python.FS.writeFile(`/visualizer/${filename}`, source, { encoding: 'utf8' });
    }
    python.runPython(`
import sys
import json
sys.path.insert(0, '/visualizer')
from visualizer_api import dispatch
`);
    return {
        run(action, data) {
            python.globals.set('_visualizer_request', JSON.stringify({ action, data }));
            try {
                return JSON.parse(python.runPython(`
_request = json.loads(_visualizer_request)
json.dumps(dispatch(_request['action'], _request['data']), allow_nan=False)
`));
            } catch (error) {
                const message = String(error.message).trim().split('\n').at(-1);
                throw new Error(message.replace(/^ValueError: /, ''));
            } finally {
                python.globals.delete('_visualizer_request');
            }
        },
    };
}
