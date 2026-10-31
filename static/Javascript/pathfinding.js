// Edit a grid and animate the results returned by the selected Python algorithm.

// colors of the weight gradient: from weight 1 (the normal cell color) up to the max weight on the grid,
// and from weight 1 down to the min weight for the weights below 1 (which only some algorithms allow)
const WEIGHT_COLORS = ['#c0ede7', '#6da7ec', '#256abf', '#0d366b'];
const LOW_WEIGHT_COLORS = ['#c0ede7', '#f4b6ae', '#e34948', '#8a1616'];

let mode = null;            // what pressing on a cell does: 'start', 'end', 'wall', 'weight' or nothing
let startCellID = null;
let endCellID = null;
let walls = new Set();
let weights = new Map();    // id -> cost of moving into that cell, for the cells that don't cost 1
let minWeight = 1;
let maxWeight = 1;
let mouseDown = false;
let paintValue = null;      // while dragging: what the cells become, a boolean in wall mode and a weight in weight mode

$(function () {
    showParams('distribution');
    algorithmChanged();
});

function cell(id) {
    return document.getElementById(id);
}

function setMode(new_mode) {
    mode = new_mode;
    $('[data-mode]').removeClass('active');
    $('[data-mode="' + new_mode + '"]').addClass('active');
}

function setStatus(message) {
    $('#status').text(message);
}

// removes the drawn result of the last run, keeping the start/end points, the walls and the weights
function clearPath() {
    stopAnimation();
    $('.cell').removeClass('neighbor path alt-path cycle');
    setStatus('');
}

function clearGraph() {
    clearPath();
    replaceWeights({});
    $('.cell').attr('class', 'cell');
    startCellID = endCellID = null;
    walls.clear();
    setMode(null);
}

function placePoint(id) {
    // start and end must be different cells
    if (id === (mode === 'start' ? endCellID : startCellID)) return;
    clearPath();
    setWall(id, false);
    if (mode === 'start') {
        if (startCellID) cell(startCellID).classList.remove('start');
        startCellID = id;
    } else {
        if (endCellID) cell(endCellID).classList.remove('end');
        endCellID = id;
    }
    cell(id).classList.add(mode);
    setMode(null);
}

function setWall(id, is_wall) {
    if (is_wall && (id === startCellID || id === endCellID)) return;
    if (is_wall) walls.add(id); else walls.delete(id);
    cell(id).classList.toggle('wall', is_wall);
}

function setWeight(id, weight) {
    if (weight !== 1) weights.set(id, weight); else weights.delete(id);
    let values = Array.from(weights.values());
    if (Math.min(1, ...values) !== minWeight || Math.max(1, ...values) !== maxWeight) drawWeights();
    drawWeight(id);
}

// replaces all the weights with new_weights (id -> weight)
function replaceWeights(new_weights) {
    let old_ids = Array.from(weights.keys());
    weights = new Map(Object.entries(new_weights).filter(([id, weight]) => weight !== 1));
    drawWeights();
    old_ids.filter(id => !weights.has(id)).forEach(drawWeight);
}

// recolors every weighted cell and the legend for the current min and max weight
function drawWeights() {
    let values = Array.from(weights.values());
    minWeight = Math.min(1, ...values);
    maxWeight = Math.max(1, ...values);
    weights.forEach((weight, id) => drawWeight(id));
    $('#weight-min').text(minWeight);
    $('#weight-max').text(maxWeight);
    $('#weight-legend-bar').css('background', legendGradient());
    $('.weight-legend').toggleClass('invisible', !weights.size);
}

function drawWeight(id) {
    let weight = weights.has(id) ? weights.get(id) : 1;
    let element = cell(id);
    element.classList.toggle('weighted', weight !== 1);
    element.style.setProperty('--weight-color', weight !== 1 ? weightColor(weight) : '');
    element.title = weight !== 1 ? 'Weight: ' + weight : '';
}

function weightColor(weight) {
    return weight > 1 ? rampColor(WEIGHT_COLORS, (weight - 1) / (maxWeight - 1))
                      : rampColor(LOW_WEIGHT_COLORS, (1 - weight) / (1 - minWeight));
}

// the color at position (0 to 1) along colors
function rampColor(colors, position) {
    position *= colors.length - 1;
    let i = Math.min(Math.floor(position), colors.length - 2);
    let from = hexToRgb(colors[i]), to = hexToRgb(colors[i + 1]);
    return 'rgb(' + from.map((value, k) => Math.round(value + (to[k] - value) * (position - i))).join(',') + ')';
}

function hexToRgb(hex) {
    return [1, 3, 5].map(i => parseInt(hex.substr(i, 2), 16));
}

// the legend goes from the min to the max weight, with weight 1 (the normal cell color) where it falls in between
function legendGradient() {
    if (!weights.size) return '';
    let one = (1 - minWeight) / (maxWeight - minWeight);
    let stops = [];
    if (minWeight < 1) {
        LOW_WEIGHT_COLORS.forEach((color, k) => stops.push([one * (1 - k / (LOW_WEIGHT_COLORS.length - 1)), color]));
    }
    if (maxWeight > 1) {
        WEIGHT_COLORS.forEach((color, k) => stops.push([one + (1 - one) * k / (WEIGHT_COLORS.length - 1), color]));
    }
    stops.sort((a, b) => a[0] - b[0]);
    return 'linear-gradient(to right, ' + stops.map(([position, color]) => color + ' ' + 100 * position + '%').join(', ') + ')';
}

// the custom weight input, rounded and clamped to its min/max
function customWeight() {
    let input = $('#weight-value');
    let weight = Math.round(parseFloat(input.val()));
    if (!Number.isFinite(weight)) weight = 1;
    weight = Math.min(+input.attr('max'), Math.max(+input.attr('min'), weight));
    input.val(weight);
    return weight;
}

function algorithmChanged() {
    clearPath();
    showParams('algorithm');
    // the custom weight and the generated weights only go below 1 for the algorithms that allow it
    let input = $('#weight-value');
    input.attr('min', $('#algorithm option:selected').data('min-weight'));
    $('#weight-range').text('(' + input.attr('min') + ' to ' + input.attr('max') + ')');
    customWeight();
}

// the group of parameter inputs of the option selected in the select_id select
function selectedParams(select_id) {
    let option = $('#' + select_id).val();
    return $('[data-params="' + select_id + '"]').filter((i, element) => element.dataset.option === option);
}

function showParams(select_id) {
    $('[data-params="' + select_id + '"]').addClass('d-none');
    selectedParams(select_id).removeClass('d-none');
}

function readParams(select_id) {
    let params = {};
    selectedParams(select_id).find('input').each(function () {
        params[this.name] = this.value === '' ? null : +this.value;
    });
    return params;
}

function generateWeights() {
    clearPath();
    let data = {distribution: $('#distribution').val(), params: readParams('distribution'),
                min_weight: +$('#weight-value').attr('min')};
    postJson('/generateWeights', data, result => replaceWeights(result.weights), setStatus);
}

function clearWeights() {
    clearPath();
    replaceWeights({});
}

function paint(id) {
    if (mode === 'wall') setWall(id, paintValue); else setWeight(id, paintValue);
}

// In wall/weight mode pressing on a cell and dragging across the grid adds walls/the custom weight,
// or erases them if the first cell already was a wall/had the custom weight.
$(document).on('pointerdown', '.cell', function (event) {
    if (event.button !== 0) return;
    event.preventDefault();
    focusCell(this);
    if (mode === 'start' || mode === 'end') {
        placePoint(this.id);
    } else if (mode === 'wall' || mode === 'weight') {
        clearPath();
        mouseDown = true;
        if (mode === 'wall') paintValue = !walls.has(this.id);
        else paintValue = weights.get(this.id) === customWeight() ? 1 : customWeight();
        paint(this.id);
    }
});

$(document).on('pointerover', '.cell', function () {
    if (mouseDown) paint(this.id);
});

$(document).on('pointermove', function (event) {
    if (!mouseDown) return;
    const target = document.elementFromPoint(event.clientX, event.clientY);
    if (target?.classList.contains('cell')) paint(target.id);
});

$(document).on('pointerup pointercancel', function () {
    mouseDown = false;
});

function focusCell(element) {
    $('.cell[tabindex="0"]').attr('tabindex', '-1');
    element.tabIndex = 0;
    element.focus({preventScroll: true});
}

$(document).on('keydown', '.cell', function (event) {
    const [row, column] = this.id.split('-').map(Number);
    const moves = {ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1]};
    if (moves[event.key]) {
        event.preventDefault();
        const [dr, dc] = moves[event.key];
        const target = cell((row + dr) + '-' + (column + dc));
        if (target) { focusCell(target); target.scrollIntoView({block: 'nearest', inline: 'nearest'}); }
    } else if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        $(this).trigger($.Event('pointerdown', {button: 0}));
        mouseDown = false;
    }
});

// a node visited again (Bellman-Ford updates nodes several times) replays its animation
function markVisited(id) {
    let element = cell(id);
    if (element.classList.contains('neighbor')) {
        element.getAnimations().forEach(animation => animation.currentTime = 0);
    } else {
        element.classList.add('neighbor');
    }
}

// draws the cheapest path, then the other paths where they leave the paths drawn before them
function drawPaths(paths, onDone) {
    let drawn = new Set([startCellID, endCellID]);
    let steps = [];
    paths.forEach((path, rank) => path.path.forEach(function (id) {
        if (!drawn.has(id)) {
            drawn.add(id);
            steps.push([id, rank === 0 ? 'path' : 'alt-path']);
        }
    }));
    animate(steps, ([id, type]) => cell(id).classList.add(type), onDone);
}

function findPath() {
    if (!startCellID || !endCellID) {
        setStatus('Choose a start and an end point first.');
        return;
    }
    clearPath();
    setStatus('Running…');
    let data = {algorithm: $('#algorithm').val(), params: readParams('algorithm'), start: startCellID, end: endCellID,
                walls: Array.from(walls), weights: Object.fromEntries(weights)};
    let isPoint = id => id === startCellID || id === endCellID;

    postJson('/runAlgo', data, function (result) {
        let visits = 'node visits: ' + result.visited.length;
        animate(result.visited.filter(id => !isPoint(id)), markVisited, function () {
            if (result.cycle) {
                setStatus('Negative cycle. Going around the highlighted cells changes the cost by ' + result.cycle.cost +
                          ' each time, so there is no cheapest path, ' + visits);
                animate(result.cycle.nodes.filter(id => !isPoint(id)), id => cell(id).classList.add('cycle'));
            } else if (!result.paths.length) {
                setStatus("The end point can't be reached. Node visits: " + result.visited.length);
            } else {
                drawPaths(result.paths, function () {
                    let best = result.paths[0];
                    setStatus((result.paths.length > 1 ?
                               result.paths.length + ' paths, costs: ' + result.paths.map(path => path.cost).join(', ') :
                               'Path cost: ' + best.cost + ' (' + (best.path.length - 1) + ' steps)') + ', ' + visits);
                });
            }
        });
    }, setStatus);
}
