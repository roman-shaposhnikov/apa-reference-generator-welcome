// Confetti popper for the hero. Vanilla canvas, no libraries.
// The page renders fine without this script - the canvas simply stays empty.

(function () {
    'use strict';

    var canvas = document.getElementById('confetti');
    if (!canvas || !canvas.getContext) return;

    var ctx = canvas.getContext('2d');
    var COLORS = ['#ff4d6d', '#ffb703', '#2ec4b6', '#4361ee', '#b5179e', '#70e000', '#ff7b00'];

    var pieces = [];
    var width = 0;
    var height = 0;
    var running = false;
    var startedAt = 0;

    var LIFETIME = 4200; // ms until the burst has fully faded
    var FADE_FROM = 2600; // ms after which pieces start fading

    function resize() {
        var ratio = Math.min(window.devicePixelRatio || 1, 2);
        var rect = canvas.getBoundingClientRect();

        width = rect.width;
        height = rect.height;
        canvas.width = Math.round(width * ratio);
        canvas.height = Math.round(height * ratio);
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    }

    function rand(min, max) {
        return min + Math.random() * (max - min);
    }

    // One popper: a cone of pieces fired from (x, y) towards `angle`.
    function fire(x, y, angle, count, cone) {
        for (var i = 0; i < count; i++) {
            var spread = rand(-cone, cone);
            var speed = rand(1.5, 8.5);
            var direction = angle + spread;

            pieces.push({
                x: x,
                y: y,
                vx: Math.cos(direction) * speed,
                vy: Math.sin(direction) * speed,
                w: rand(6, 11),
                h: rand(9, 16),
                color: COLORS[(Math.random() * COLORS.length) | 0],
                spin: rand(-0.24, 0.24),
                angle: rand(0, Math.PI * 2),
                wobble: rand(0, Math.PI * 2)
            });
        }
    }

    function burst() {
        pieces = [];
        // One pop in the middle of the hero, thrown in every direction, so the
        // confetti stays a single bunch centred on the headline instead of a
        // fountain that leaves the frame in a second.
        fire(width * 0.5, height * 0.52, -Math.PI / 2, 170, Math.PI);
    }

    function draw(now) {
        var elapsed = now - startedAt;
        ctx.clearRect(0, 0, width, height);

        var fade = elapsed < FADE_FROM
            ? 1
            : Math.max(0, 1 - (elapsed - FADE_FROM) / (LIFETIME - FADE_FROM));

        for (var i = 0; i < pieces.length; i++) {
            var p = pieces[i];

            p.vy += 0.17;          // gravity
            p.vx *= 0.992;         // drag
            p.vy *= 0.992;
            p.x += p.vx;
            p.y += p.vy;
            p.wobble += 0.09;
            p.x += Math.sin(p.wobble) * 0.4;
            p.angle += p.spin;

            ctx.save();
            ctx.globalAlpha = fade;
            ctx.translate(p.x, p.y);
            ctx.rotate(p.angle);
            ctx.fillStyle = p.color;
            // Squash on the vertical axis so pieces read as spinning ribbons.
            ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h * Math.abs(Math.cos(p.wobble)));
            ctx.restore();
        }

        if (elapsed < LIFETIME) {
            requestAnimationFrame(draw);
        } else {
            ctx.clearRect(0, 0, width, height);
            running = false;
        }
    }

    // Reduced motion: draw a single static scatter instead of animating.
    function staticScatter() {
        burst();
        for (var step = 0; step < 34; step++) {
            for (var i = 0; i < pieces.length; i++) {
                var p = pieces[i];
                p.vy += 0.17;
                p.x += p.vx;
                p.y += p.vy;
                p.vx *= 0.992;
                p.vy *= 0.992;
                p.angle += p.spin;
            }
        }

        ctx.clearRect(0, 0, width, height);
        for (var j = 0; j < pieces.length; j++) {
            var q = pieces[j];
            ctx.save();
            ctx.translate(q.x, q.y);
            ctx.rotate(q.angle);
            ctx.fillStyle = q.color;
            ctx.fillRect(-q.w / 2, -q.h / 2, q.w, q.h);
            ctx.restore();
        }
    }

    function start() {
        resize();
        if (!width || !height) return;

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            staticScatter();
            return;
        }

        burst();
        startedAt = performance.now();
        if (!running) {
            running = true;
            requestAnimationFrame(draw);
        }
    }

    window.addEventListener('resize', function () {
        // Only re-fit the canvas; re-firing on every resize would be noisy.
        if (!running) resize();
    });

    if (document.readyState === 'complete') {
        start();
    } else {
        window.addEventListener('load', start);
    }
})();
