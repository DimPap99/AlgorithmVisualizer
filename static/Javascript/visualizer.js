// Shared by the visualizer pages: the animation speed slider and a cancellable step by step animation.

$(function () {
    $('#myRange').on('input', function () {
        $('#demo').text(this.value);
    }).trigger('input');
});

// delay between two animation steps in ms (the slider goes from 1 = slowest to 150 = fastest)
function animationDelay() {
    return 150 - $('#myRange').val();
}

// Calls drawStep(step) for every step, waiting animationDelay() in between, and then onDone().
// Starting another animation or calling stopAnimation() cancels the running one.
let animationId = 0;

function animate(steps, drawStep, onDone) {
    const id = ++animationId;
    let i = 0;

    function next() {
        if (id !== animationId) return;
        if (i < steps.length) {
            drawStep(steps[i++]);
            setTimeout(next, animationDelay());
        } else if (onDone) {
            onDone();
        }
    }
    next();
}

function stopAnimation() {
    animationId++;
}

// POSTs data as JSON and calls onSuccess(response) unless an animation was started or stopped in the meantime
function postJson(url, data, onSuccess, onError) {
    const id = ++animationId;
    $.ajax({
        type: 'POST',
        url: url,
        contentType: 'application/json;charset=utf-8',
        data: JSON.stringify(data),
        dataType: 'json'
    }).done(function (response) {
        if (id === animationId) onSuccess(response);
    }).fail(function (xhr) {
        if (id === animationId) onError(xhr.responseJSON ? xhr.responseJSON.error : 'Request failed!');
    });
}
