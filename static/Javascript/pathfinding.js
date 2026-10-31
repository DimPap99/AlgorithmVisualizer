// Path finding page: pick a start and an end point, draw walls, then send the grid to Flask
// and animate the nodes the chosen algorithm visited followed by the path it found.

let mode = null;            // what pressing on a cell does: 'start', 'end', 'wall' or nothing
let startCellID = null;
let endCellID = null;
let walls = new Set();
let mouseDown = false;
let paintWalls = true;      // while dragging: true adds walls, false erases them

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

// removes the drawn result of the last run, keeping the start/end points and the walls
function clearPath() {
    stopAnimation();
    $('.cell').removeClass('neighbor path');
    setStatus('');
}

function clearGraph() {
    clearPath();
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

// In wall mode pressing on a cell and dragging across the grid adds walls,
// or erases them if the first cell was already a wall.
$(document).on('mousedown', '.cell', function (event) {
    event.preventDefault();
    if (mode === 'start' || mode === 'end') {
        placePoint(this.id);
    } else if (mode === 'wall') {
        clearPath();
        mouseDown = true;
        paintWalls = !walls.has(this.id);
        setWall(this.id, paintWalls);
    }
});

$(document).on('mouseover', '.cell', function () {
    if (mouseDown && mode === 'wall') setWall(this.id, paintWalls);
});

$(document).on('mouseup', function () {
    mouseDown = false;
});

function findPath() {
    if (!startCellID || !endCellID) {
        setStatus('Choose a start and an end point first!');
        return;
    }
    clearPath();
    let data ={algorithm: $('#algorithm').val(), start: startCellID, end: endCellID, walls: Array.from(walls)};
    let isPoint = id => id === startCellID || id === endCellID;

    postJson('/runAlgo', data, function (result) {
        animate(result.visited.filter(id => !isPoint(id)), id => cell(id).classList.add('neighbor'), function () {
            if (!result.path.length) {
                setStatus("The end point can't be reached! Visited " + result.visited.length + " nodes.");
                return;
            }
            animate(result.path.filter(id => !isPoint(id)), id => cell(id).classList.add('path'), function () {
                setStatus('Path length: ' + (result.path.length - 1) + ', visited nodes: ' + result.visited.length);
            });
        });
    }, setStatus);
}
