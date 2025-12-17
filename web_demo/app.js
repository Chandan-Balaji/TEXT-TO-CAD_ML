// Text to CAD - Web Demo
// Three.js scene setup and shape generation

let scene, camera, renderer, controls;
let shapes = [];

// Example commands - now with more variety!
const examples = [
    "A large red sphere",
    "A blue cube with size 2",
    "A green cylinder with radius 1 height 3",
    "A yellow torus",
    "A cone at position 2, 0, 0",
    "A huge orange ball",
    "A small white box at 1, 0, 1",
    "A pink donut",
    "Create a tall gray pillar"
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
    camera.position.set(5, 5, 5);
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
    const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Axes helper
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);

    // Handle window resize
    window.addEventListener('resize', onWindowResize);

    // Start animation loop
    animate();

    showStatus('Ready! Enter a shape description and click Generate.');
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

// Enhanced text parsing with better natural language understanding
function parseTextInput(text) {
    const originalText = text;
    text = text.toLowerCase().trim();

    // Initialize with smart defaults
    const params = {
        shape: null,  // Start with null to detect if no shape found
        color: 0x667eea,  // Default purple
        size: 1,
        position: { x: 0, y: 0, z: 0 },
        radius: 1,
        height: 2,
        radiusTop: 1,
        radiusBottom: 1,
        detected: []  // Track what was detected for debugging
    };

    // ============= SHAPE DETECTION (with aliases) =============
    const shapePatterns = {
        'sphere': ['sphere', 'ball', 'globe', 'orb', 'round'],
        'cube': ['cube', 'box', 'square', 'block', 'cuboid'],
        'cylinder': ['cylinder', 'tube', 'pipe', 'column', 'pillar'],
        'torus': ['torus', 'donut', 'doughnut', 'ring'],
        'cone': ['cone', 'pyramid', 'triangle', 'pointy']
    };

    // Check each shape pattern
    for (const [shape, patterns] of Object.entries(shapePatterns)) {
        if (patterns.some(pattern => text.includes(pattern))) {
            params.shape = shape;
            params.detected.push(`shape:${shape}`);
            break;
        }
    }

    // If no shape detected, throw helpful error
    if (!params.shape) {
        throw new Error(`No shape detected! Try: sphere, cube, cylinder, cone, or torus`);
    }

    // ============= COLOR DETECTION (with more variations) =============
    const colorMap = {
        'red': [0xff4444, ['red', 'crimson', 'scarlet']],
        'blue': [0x4444ff, ['blue', 'navy', 'azure']],
        'green': [0x44ff44, ['green', 'lime', 'emerald']],
        'yellow': [0xffff44, ['yellow', 'gold', 'golden']],
        'purple': [0xff44ff, ['purple', 'violet', 'magenta', 'pink']],
        'orange': [0xff8844, ['orange', 'amber']],
        'cyan': [0x44ffff, ['cyan', 'turquoise', 'aqua']],
        'white': [0xffffff, ['white', 'bright']],
        'black': [0x222222, ['black', 'dark']],
        'brown': [0x8b4513, ['brown', 'tan', 'beige']],
        'gray': [0x888888, ['gray', 'grey', 'silver']]
    };

    for (const [colorName, [hex, patterns]] of Object.entries(colorMap)) {
        if (patterns.some(pattern => text.includes(pattern))) {
            params.color = hex;
            params.detected.push(`color:${colorName}`);
            break;
        }
    }

    // ============= SIZE MODIFIERS =============
    if (text.match(/\b(large|big|huge|giant|massive)\b/)) {
        params.size = 2;
        params.detected.push('size:large');
    } else if (text.match(/\b(small|tiny|little|mini|micro)\b/)) {
        params.size = 0.5;
        params.detected.push('size:small');
    } else if (text.match(/\b(medium|normal|regular)\b/)) {
        params.size = 1;
        params.detected.push('size:medium');
    }

    // ============= EXTRACT NUMBERS =============

    // Size with various formats
    let sizeMatch = text.match(/size[:\s]+(\d+(?:\.\d+)?)/);
    if (!sizeMatch) sizeMatch = text.match(/sized?\s+(\d+(?:\.\d+)?)/);
    if (!sizeMatch) sizeMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:unit|m|cm|meter)/);
    if (sizeMatch) {
        params.size = parseFloat(sizeMatch[1]);
        params.detected.push(`size:${params.size}`);
    }

    // Radius
    let radiusMatch = text.match(/radius[:\s]+(\d+(?:\.\d+)?)/);
    if (!radiusMatch) radiusMatch = text.match(/r[=:\s]+(\d+(?:\.\d+)?)/);
    if (radiusMatch) {
        params.radius = parseFloat(radiusMatch[1]);
        params.detected.push(`radius:${params.radius}`);
    }

    // Height
    let heightMatch = text.match(/height[:\s]+(\d+(?:\.\d+)?)/);
    if (!heightMatch) heightMatch = text.match(/h[=:\s]+(\d+(?:\.\d+)?)/);
    if (!heightMatch) heightMatch = text.match(/tall\s+(\d+(?:\.\d+)?)/);
    if (heightMatch) {
        params.height = parseFloat(heightMatch[1]);
        params.detected.push(`height:${params.height}`);
    }

    // ============= POSITION EXTRACTION (multiple formats) =============

    // Format 1: "at x, y, z" or "at x y z"
    let posMatch = text.match(/(?:at|position)\s+(-?\d+(?:\.\d+)?)[,\s]+(-?\d+(?:\.\d+)?)[,\s]+(-?\d+(?:\.\d+)?)/);

    // Format 2: "at (x, y, z)"
    if (!posMatch) {
        posMatch = text.match(/at\s*\(\s*(-?\d+(?:\.\d+)?)[,\s]+(-?\d+(?:\.\d+)?)[,\s]+(-?\d+(?:\.\d+)?)\s*\)/);
    }

    // Format 3: "x:1 y:2 z:3"
    if (!posMatch) {
        const xMatch = text.match(/x[:\s=]+(-?\d+(?:\.\d+)?)/);
        const yMatch = text.match(/y[:\s=]+(-?\d+(?:\.\d+)?)/);
        const zMatch = text.match(/z[:\s=]+(-?\d+(?:\.\d+)?)/);
        if (xMatch || yMatch || zMatch) {
            posMatch = [null,
                xMatch ? xMatch[1] : '0',
                yMatch ? yMatch[1] : '0',
                zMatch ? zMatch[1] : '0'
            ];
        }
    }

    if (posMatch) {
        params.position = {
            x: parseFloat(posMatch[1]),
            y: parseFloat(posMatch[2]),
            z: parseFloat(posMatch[3])
        };
        params.detected.push(`position:(${params.position.x},${params.position.y},${params.position.z})`);
    }

    // ============= SMART DEFAULTS BASED ON SHAPE =============
    if (params.shape === 'cylinder' && !heightMatch) {
        params.height = 3;  // Taller default for cylinders
    }
    if (params.shape === 'cone' && !heightMatch) {
        params.height = 2.5;
    }
    if (params.shape === 'torus') {
        params.radius = params.radius * params.size;  // Make torus radius respect size
    }

    // Log what was detected (helpful for debugging)
    console.log('Parsed:', params.detected.join(', '));
    console.log('Full params:', params);

    return params;
}

// Generate 3D shape based on parameters
function createShape(params) {
    let geometry;

    switch (params.shape) {
        case 'sphere':
            geometry = new THREE.SphereGeometry(params.radius * params.size, 32, 32);
            break;
        case 'cube':
            geometry = new THREE.BoxGeometry(params.size, params.size, params.size);
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
        color: params.color,
        metalness: 0.3,
        roughness: 0.4
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(params.position.x, params.position.y, params.position.z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    return mesh;
}

// Main generate function with better error handling
function generateShape() {
    const textInput = document.getElementById('text-input').value.trim();

    if (!textInput) {
        showStatus('Please enter a shape description!', 'error');
        return;
    }

    try {
        const params = parseTextInput(textInput);
        const shape = createShape(params);
        scene.add(shape);
        shapes.push(shape);

        // Show what was created
        const detectedInfo = params.detected.join(', ');
        showStatus(`✓ Generated ${params.shape}! (${detectedInfo})`);
        console.log(`Created ${params.shape} at position (${params.position.x}, ${params.position.y}, ${params.position.z})`);
    } catch (error) {
        // Show specific error message
        let errorMsg = error.message;

        // Add helpful suggestions
        if (errorMsg.includes('No shape detected')) {
            errorMsg += '\n\nTry: "a red sphere", "blue cube", "green cylinder", etc.';
        }

        showStatus(errorMsg, 'error');
        console.error('Parsing error:', error);
    }
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
    showStatus('Example loaded! Click Generate to create the shape.');
}

// Show status message
function showStatus(message, type = 'success') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status show';

    if (type === 'error') {
        status.style.background = 'rgba(255, 68, 68, 0.9)';
    } else {
        status.style.background = 'rgba(0, 0, 0, 0.8)';
    }

    setTimeout(() => {
        status.classList.remove('show');
    }, 3000);
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', init);
