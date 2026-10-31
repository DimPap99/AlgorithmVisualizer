// Load the same algorithm descriptions on both the Flask and static pages.
(() => {
    const sourceURL = new URL('../data/algorithm-guides.json', document.currentScript.src);

    async function initializeGuide() {
        const panel = document.getElementById('algorithm-guide');
        const select = document.getElementById('algorithm');
        if (!panel || !select) return;
        const name = document.getElementById('guide-name');
        const time = document.getElementById('guide-time');
        const notation = document.getElementById('guide-notation');
        const note = document.getElementById('guide-note');
        const pseudocode = document.getElementById('guide-pseudocode');

        try {
            const response = await fetch(sourceURL);
            if (!response.ok) throw new Error('Algorithm notes could not load.');
            const guides = await response.json();
            function showSelectedAlgorithm() {
                const selected = guides.algorithms[select.value];
                name.textContent = select.value;
                time.textContent = selected?.time || 'Unavailable';
                notation.textContent = selected ? guides.notation[selected.group] : '';
                note.textContent = selected?.note || 'No notes are available for this algorithm.';
                pseudocode.textContent = selected?.pseudocode.join('\n') || '';
            }
            select.addEventListener('change', showSelectedAlgorithm);
            showSelectedAlgorithm();
        } catch (error) {
            time.textContent = 'Unavailable';
            note.textContent = 'Algorithm notes could not load. Reload the page to try again.';
        } finally {
            panel.setAttribute('aria-busy', 'false');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeGuide, { once: true });
    } else {
        initializeGuide();
    }
})();
