// AI-Powered Text to CAD - Enhanced Frontend
// Connects to Flask ML Backend with multi-object support

let scene, camera, renderer, controls;
let shapes = [];
const API_URL = 'http://localhost:5000';

// Enhanced examples with multi-object scenarios
const examples = [
    "A large red sphere",
    "A blue cube with size 2",
    "3 green cylinders",
    "A house",
    "stack 3 cubes",
    "A table",
    "A snowman",
    "sphere and cube",
    "4 orange balls"
];

// Initialize Three.js scene
function init() {
    const container = document.getElementById('canvas-container');

    // Scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a202c);

    // Camera
    camera = new THREE.PerspectiveCamera(
        75,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(8, 8, 8);
    camera.lookAt(0, 0, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    // Orbit Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Grid helper
    const gridHelper = new THREE.GridHelper(30, 30, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Axes helper
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);

    // Handle window resize
    window.addEventListener('resize', onWindowResize);

    // Start animation loop
    animate();

    showStatus('🤖 AI Ready! Enter ANY text description.');
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// Generate 3D shape based on parameters
function createShape(params) {
    let geometry;

    switch (params.shape) {
        case 'sphere':
            geometry = new THREE.SphereGeometry(params.radius * params.size, 32, 32);
            break;
        case 'cube':
            const size = params.size;
            geometry = new THREE.BoxGeometry(size, size, size);
            break;
        case 'cylinder':
            geometry = new THREE.CylinderGeometry(
                params.radius,
                params.radius,
                params.height,
                32
            );
            break;
        case 'torus':
            geometry = new THREE.TorusGeometry(params.radius * params.size, 0.4, 16, 100);
            break;
        case 'cone':
            geometry = new THREE.ConeGeometry(params.radius * params.size, params.height, 32);
            break;
        default:
            geometry = new THREE.SphereGeometry(params.radius * params.size, 32, 32);
    }

    const material = new THREE.MeshStandardMaterial({
        color: params.color || 0x667eea,
        metalness: 0.3,
        roughness: 0.4
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(params.position.x, params.position.y, params.position.z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    return mesh;
}

// Main generate function - calls ML backend
async function generateShape() {
    const textInput = document.getElementById('text-input').value.trim();

    if (!textInput) {
        showStatus('Please enter a description!', 'error');
        return;
    }

    try {
        showStatus('🤖 AI is thinking...', 'info');

        // Call ML backend API
        const response = await fetch(`${API_URL}/parse-text`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: textInput })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Generate all objects from ML response
        const objects = data.objects || [];
        let generated = 0;

        for (const params of objects) {
            const shape = createShape(params);
            scene.add(shape);
            shapes.push(shape);
            generated++;
        }

        // Show success message
        const confidence = objects[0]?.confidence || 0;
        const confidencePercent = Math.round(confidence * 100);
        const mlPowered = data.ml_powered ? '🧠 ML' : '📐 Rule-based';

        showStatus(`✅ Generated ${generated} object(s)! ${mlPowered} (${confidencePercent}% confidence)`, 'success');
        console.log('API Response:', data);

    } catch (error) {
        // Fallback to local parsing if backend is down
        console.warn('Backend unavailable, using local parsing:', error);
        showStatus('⚠️ Backend offline - using basic parsing', 'warning');

        try {
            const params = parseTextInputLocal(textInput);
            const shape = createShape(params);
            scene.add(shape);
            shapes.push(shape);
            showStatus(`Generated ${params.shape} (offline mode)`, 'success');
        } catch (localError) {
            showStatus('Error: ' + localError.message, 'error');
        }
    }
}

// Fallback local parsing (if backend is down)
function parseTextInputLocal(text) {
    text = text.toLowerCase().trim();

    const params = {
        shape: 'sphere',
        color: 0x667eea,
        size: 1,
        position: { x: 0, y: 0, z: 0 },
        radius: 1,
        height: 2
    };

    // Basic shape detection
    if (text.includes('sphere') || text.includes('ball')) params.shape = 'sphere';
    else if (text.includes('cube') || text.includes('box')) params.shape = 'cube';
    else if (text.includes('cylinder') || text.includes('tube')) params.shape = 'cylinder';
    else if (text.includes('torus') || text.includes('donut')) params.shape = 'torus';
    else if (text.includes('cone') || text.includes('pyramid')) params.shape = 'cone';

    // Basic color detection
    const colorMap = {
        'red': 0xff4444, 'blue': 0x4444ff, 'green': 0x44ff44,
        'yellow': 0xffff44, 'purple': 0xff44ff, 'orange': 0xff8844,
        'cyan': 0x44ffff, 'white': 0xffffff, 'black': 0x222222
    };

    for (const [color, hex] of Object.entries(colorMap)) {
        if (text.includes(color)) {
            params.color = hex;
            break;
        }
    }

    // Basic size detection
    if (text.match(/\b(large|big|huge)\b/)) params.size = 2;
    else if (text.match(/\b(small|tiny)\b/)) params.size = 0.5;

    return params;
}

// Clear all shapes from scene
function clearScene() {
    shapes.forEach(shape => {
        scene.remove(shape);
        shape.geometry.dispose();
        shape.material.dispose();
    });
    shapes = [];
    showStatus('Scene cleared!');
}

// Load example command
function loadExample(index) {
    document.getElementById('text-input').value = examples[index];
    showStatus('Example loaded! Click Generate.');
}

// Show status message
function showStatus(message, type = 'success') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status show';

    const colors = {
        'success': 'rgba(68, 255, 68, 0.9)',
        'error': 'rgba(255, 68, 68, 0.9)',
        'warning': 'rgba(255, 200, 68, 0.9)',
        'info': 'rgba(102, 126, 234, 0.9)'
    };

    status.style.background = colors[type] || colors.success;

    setTimeout(() => {
        status.classList.remove('show');
    }, 3000);
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', init);
