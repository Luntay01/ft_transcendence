//import * as THREE from 'three'; better off importing but getting error because not using a bundler
//
//export function initPong() {
//   console.log("Initializing Pong...");
//
//   const container = document.getElementById('pongContainer');
//   if (!container) {
//       console.error("Pong container not found!");
//       return;
//   }
//
//   const scene = new THREE.Scene();
//   const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
//   const renderer = new THREE.WebGLRenderer();
//   renderer.setSize(window.innerWidth, window.innerHeight);
//   
//   // Add renderer to the container div
//   container.appendChild(renderer.domElement);
//
//   const geometry = new THREE.BoxGeometry();
//   const material = new THREE.MeshBasicMaterial({color: 0x00ff00});
//   const cube = new THREE.Mesh(geometry, material);
//   scene.add(cube);
//
//   camera.position.z = 5;
//
//   function animate() {
//       requestAnimationFrame(animate);
//       cube.rotation.x += 0.01;
//       cube.rotation.y += 0.01;
//       renderer.render(scene, camera);
//   }
//
//   animate();
//}
//

export function initPong() {
    console.log("Initializing Pong...");

    const container = document.getElementById('pongContainer');
    if (!container) {
        console.error("Pong container not found!");
        return;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);

    container.appendChild(renderer.domElement);

    // Create paddles (left, right, top, bottom)
    const paddleGeometry = new THREE.BoxGeometry(1, 5, 1);
    const paddleMaterial = new THREE.MeshBasicMaterial({color: 0x00ff00});

    const leftPaddle = new THREE.Mesh(paddleGeometry, paddleMaterial);
    const rightPaddle = new THREE.Mesh(paddleGeometry, paddleMaterial);

    // Rotate top and bottom paddles to be horizontal
    const horizontalPaddleGeometry = new THREE.BoxGeometry(5, 1, 1);
    const topPaddle = new THREE.Mesh(horizontalPaddleGeometry, paddleMaterial);
    const bottomPaddle = new THREE.Mesh(horizontalPaddleGeometry, paddleMaterial);

    // Position paddles
    leftPaddle.position.x = -10;
    rightPaddle.position.x = 10;
    topPaddle.position.y = 7;  // Top of the screen
    bottomPaddle.position.y = -7;  // Bottom of the screen

    scene.add(leftPaddle);
    scene.add(rightPaddle);
    scene.add(topPaddle);
    scene.add(bottomPaddle);

    // Create ball
    const ballGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const ballMaterial = new THREE.MeshBasicMaterial({color: 0xff0000});
    const ball = new THREE.Mesh(ballGeometry, ballMaterial);
    ball.position.set(0, 0, 0);
    scene.add(ball);

    camera.position.z = 20;

    let ballVelocity = {x: 0.1, y: 0.1};
    const paddleSpeed = 0.2;

    // Handle player input (Move paddles)
    const keyState = {};
    window.addEventListener('keydown', (e) => keyState[e.key] = true);
    window.addEventListener('keyup', (e) => keyState[e.key] = false);

    function updatePaddles() {
        // Left Paddle (W, S)
        if (keyState['w']) leftPaddle.position.y += paddleSpeed;
        if (keyState['s']) leftPaddle.position.y -= paddleSpeed;

        // Right Paddle (Up Arrow, Down Arrow)
        if (keyState['ArrowUp']) rightPaddle.position.y += paddleSpeed;
        if (keyState['ArrowDown']) rightPaddle.position.y -= paddleSpeed;

        // Top Paddle (A, D)
        if (keyState['a']) topPaddle.position.x -= paddleSpeed;
        if (keyState['d']) topPaddle.position.x += paddleSpeed;

        // Bottom Paddle (Left Arrow, Right Arrow)
        if (keyState['ArrowLeft']) bottomPaddle.position.x -= paddleSpeed;
        if (keyState['ArrowRight']) bottomPaddle.position.x += paddleSpeed;
    }

    // Ball Movement
    function updateBall() {
        ball.position.x += ballVelocity.x;
        ball.position.y += ballVelocity.y;

        // Ball collisions with top/bottom
        if (ball.position.y > 7 || ball.position.y < -7) {
            ballVelocity.y = -ballVelocity.y;
        }

        // Ball collisions with left/right paddles
        if ((ball.position.x < -9.5 && ball.position.y < leftPaddle.position.y + 2.5 && ball.position.y > leftPaddle.position.y - 2.5) ||
            (ball.position.x > 9.5 && ball.position.y < rightPaddle.position.y + 2.5 && ball.position.y > rightPaddle.position.y - 2.5)) {
            ballVelocity.x = -ballVelocity.x;
        }

        // Ball collisions with top/bottom paddles
        if ((ball.position.y > 6.5 && ball.position.x < topPaddle.position.x + 2.5 && ball.position.x > topPaddle.position.x - 2.5) ||
            (ball.position.y < -6.5 && ball.position.x < bottomPaddle.position.x + 2.5 && ball.position.x > bottomPaddle.position.x - 2.5)) {
            ballVelocity.y = -ballVelocity.y;
        }

        // Reset ball if out of bounds (scored)
        if (ball.position.x > 12 || ball.position.x < -12) {
            ball.position.set(0, 0, 0);
            ballVelocity = {x: (Math.random() > 0.5 ? 0.1 : -0.1), y: (Math.random() > 0.5 ? 0.1 : -0.1)};
        }
    }

    // Game loop
    function animate() {
        requestAnimationFrame(animate);

        updatePaddles();
        updateBall();

        renderer.render(scene, camera);
    }

    animate();
}