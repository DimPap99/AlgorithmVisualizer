// Generate an array, run the selected Python algorithm, and animate its swaps.

let num_array = [];

$(function () {
    generateArray(1, 150, 50);
});

function Clear() {
    stopAnimation();
    num_array = [];
    $('#array').empty();
    setStatus('');
}

// fills the array with elements_number unique random numbers between min and max (both included)
function generateArray(min, max, elements_number) {
    stopAnimation();
    elements_number = Math.min(elements_number, max - min + 1);
    num_array = [];
    while (num_array.length < elements_number) {
        let num = randomIntFromInterval(min, max);
        if (!num_array.includes(num)) num_array.push(num);
    }
    $('#array').html(num_array.map(() => "<div class='bar'></div>").join(''));
    num_array.forEach((num, index) => drawBar(index));
    setStatus('');
}

function sortArray() {
    if (!num_array.length) {
        setStatus('Generate an array first.');
        return;
    }
    setStatus('Running…');
    postJson('/SortArray', {algorithm: $('#algorithm').val(), array: num_array}, function (data) {
        animate(data.swaps, function ([index1, index2]) {
            [num_array[index1], num_array[index2]] = [num_array[index2], num_array[index1]];
            $('.bar.active').removeClass('active');
            drawBar(index1).classList.add('active');
            drawBar(index2).classList.add('active');
        }, function () {
            $('.bar.active').removeClass('active');
            setStatus('Sorted with ' + data.swaps.length + ' swaps.');
        });
    }, setStatus);
}

// updates the bar at index to show num_array[index]
function drawBar(index) {
    let num = num_array[index];
    let bar = document.getElementById('array').children[index];
    bar.style.height = (num + 40) + 'px';
    bar.style.backgroundColor = 'hsl(96, 28%, ' + (40 + num / 10) + '%)';
    bar.textContent = num;
    return bar;
}

function setStatus(message) {
    $('#status').text(message);
}

function randomIntFromInterval(min, max) {
    // min and max included
    return Math.floor(Math.random() * (max - min + 1) + min);
}
