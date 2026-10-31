// Shared by the visualizer pages: the animation speed slider and a cancellable step by step animation.

// the speed slider goes from MIN_SPEED to MAX_SPEED steps per second
const MIN_SPEED = 1, MAX_SPEED = 3000;

$(function () {
    $('#speed').on('input', function () {
        let speed = animationSpeed();
        $('#speed-label').text((speed < 10 ? speed.toFixed(1) : Math.round(speed)) + ' steps/s');
    }).trigger('input');
});

// steps per second for the slider position, on a log scale so that every bit of the slider changes the speed
// by the same factor
function animationSpeed() {
    return MIN_SPEED * Math.pow(MAX_SPEED / MIN_SPEED, $('#speed').val() / 100);
}

// Calls drawStep(step) for every step at animationSpeed() steps per second, and then onDone(). Every frame draws
// the steps that are due by then, so the speed isn't limited by the frame rate and changes as the slider moves.
// Starting another animation or calling stopAnimation() cancels the running one.
let animationId = 0;

function animate(steps, drawStep, onDone) {
    const id = ++animationId;
    let i = 0;
    let due = 1;            // steps due to be drawn, the first one is drawn right away
    let last_frame = null;

    function frame(now) {
        if (id !== animationId) return;
        // capped so that coming back to a background tab doesn't draw everything at once
        if (last_frame !== null) due += Math.min(now - last_frame, 100) / 1000 * animationSpeed();
        last_frame = now;
        for (; due >= 1 && i < steps.length; due--) {
            drawStep(steps[i++]);
        }
        if (i < steps.length) {
            requestAnimationFrame(frame);
        } else if (onDone) {
            onDone();
        }
    }
    requestAnimationFrame(frame);
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
