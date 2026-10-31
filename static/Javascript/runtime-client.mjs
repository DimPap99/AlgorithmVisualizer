export class PythonWorkerClient {
    constructor(url, { WorkerClass = globalThis.Worker, timeout = 60000, onState = () => {} } = {}) {
        this.url = url;
        this.WorkerClass = WorkerClass;
        this.timeout = timeout;
        this.onState = onState;
        this.pending = new Map();
        this.nextId = 0;
        this.start();
    }

    start() {
        this.ready = new Promise((resolve, reject) => {
            this.resolveReady = resolve;
            this.rejectReady = reject;
        });
        // An initial load can fail before any operation is requested.
        this.ready.catch(() => {});
        this.onState('loading');
        this.startupTimer = setTimeout(() => this.fail(new Error('Loading Python timed out. Retry to load it again.')), this.timeout);
        try {
            const worker = this.worker = new this.WorkerClass(this.url, { type: 'module' });
            worker.onmessage = ({ data }) => {
                if (this.worker !== worker) return;
                if (data.type === 'ready') {
                    clearTimeout(this.startupTimer);
                    this.resolveReady();
                    this.onState('ready');
                } else if (data.type === 'fatal') {
                    this.fail(new Error(data.error));
                } else if (data.type === 'result') {
                    const pending = this.pending.get(data.id);
                    if (!pending) return;
                    clearTimeout(pending.timer);
                    this.pending.delete(data.id);
                    this.onState(this.pending.size ? 'running' : 'ready');
                    if (data.error) pending.reject(new Error(data.error));
                    else pending.resolve(data.result);
                }
            };
            worker.onerror = event => {
                event.preventDefault?.();
                if (this.worker === worker) this.fail(new Error('Python could not start. Retry, or reload the page.'));
            };
            worker.onmessageerror = () => {
                if (this.worker === worker) this.fail(new Error('Could not read a response from Python.'));
            };
        } catch (error) {
            this.fail(error);
        }
    }

    async request(action, data) {
        await this.ready;
        const id = ++this.nextId;
        this.onState('running');
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => this.fail(new Error('The algorithm took too long. Retry with a simpler input.')), this.timeout);
            this.pending.set(id, { resolve, reject, timer });
            try {
                this.worker.postMessage({ id, action, data });
            } catch (error) {
                this.fail(error);
            }
        });
    }

    fail(error) {
        clearTimeout(this.startupTimer);
        this.worker?.terminate();
        this.worker = null;
        this.rejectReady(error);
        for (const pending of this.pending.values()) {
            clearTimeout(pending.timer);
            pending.reject(error);
        }
        this.pending.clear();
        this.onState('error', error.message);
    }

    cancel() {
        if (!this.pending.size) return;
        this.fail(new Error('Operation cancelled.'));
        this.start();
    }

    restart() {
        this.fail(new Error('Python restarted.'));
        this.start();
    }

    dispose() {
        this.fail(new Error('Python stopped.'));
    }
}

if (typeof document !== 'undefined' && document.documentElement.dataset.runtime === 'browser') {
    const status = document.getElementById('runtime-status');
    const retry = document.getElementById('runtime-retry');
    const controls = document.querySelectorAll('[data-runtime-action]');
    window.visualizerRuntime = new PythonWorkerClient(new URL('./pyodide-worker.mjs', import.meta.url), {
        onState(state, error) {
            status.textContent = { loading: 'Loading Python…', ready: 'Ready', running: 'Running…', error }[state];
            status.dataset.state = state;
            retry.hidden = state !== 'error';
            controls.forEach(button => { button.disabled = state !== 'ready'; });
        },
    });
    retry.addEventListener('click', () => window.visualizerRuntime.restart());
}
