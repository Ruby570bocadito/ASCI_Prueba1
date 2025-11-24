// Configuración
const socket = io();
let currentMode = 'manual';
let currentSpeed = 80;

// Elementos DOM
const statusIndicator = document.getElementById('statusIndicator');
const connectionStatus = document.getElementById('connectionStatus');
const modeButtons = document.querySelectorAll('.mode-btn');
const controlButtons = document.querySelectorAll('.control-btn');
const speedSlider = document.getElementById('speedSlider');
const speedValue = document.getElementById('speedValue');
const currentModeText = document.getElementById('currentMode');
const robotStatus = document.getElementById('robotStatus');
const robotSpeed = document.getElementById('robotSpeed');
const manualControl = document.getElementById('manualControl');

// ===== CONEXIÓN WEBSOCKET =====
socket.on('connect', () => {
    console.log('Conectado al servidor');
    statusIndicator.classList.add('connected');
    connectionStatus.textContent = 'Conectado';
});

socket.on('disconnect', () => {
    console.log('Desconectado del servidor');
    statusIndicator.classList.remove('connected');
    connectionStatus.textContent = 'Desconectado';
});

socket.on('status', (data) => {
    updateStatus(data);
});

// ===== FUNCIONES DE CONTROL =====
function sendCommand(cmd) {
    socket.emit('comando', { cmd: cmd });
    console.log('Comando enviado:', cmd);
}

function updateStatus(data) {
    if (data.modo) {
        currentMode = data.modo;
        const modeNames = {
            'manual': 'Manual',
            'linea': 'Línea',
            'sumo': 'Sumo'
        };
        currentModeText.textContent = modeNames[data.modo] || data.modo;
        
        // Mostrar/ocultar controles manuales
        if (data.modo === 'manual') {
            manualControl.classList.remove('hidden');
            robotStatus.textContent = 'Detenido';
        } else {
            manualControl.classList.add('hidden');
            robotStatus.textContent = 'Autónomo';
        }
    }
    
    if (data.velocidad !== undefined) {
        currentSpeed = data.velocidad;
        speedSlider.value = data.velocidad;
        speedValue.textContent = data.velocidad;
        robotSpeed.textContent = data.velocidad + '%';
    }
}

// ===== EVENT LISTENERS - MODOS =====
modeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        
        // Actualizar UI
        modeButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Enviar comando
        sendCommand(mode);
    });
});

// ===== EVENT LISTENERS - CONTROLES =====
controlButtons.forEach(btn => {
    const cmd = btn.dataset.cmd;
    
    // Click/Touch Start
    btn.addEventListener('mousedown', () => {
        if (currentMode === 'manual') {
            sendCommand(cmd);
            btn.style.transform = 'scale(0.95)';
        }
    });
    
    btn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        if (currentMode === 'manual') {
            sendCommand(cmd);
            btn.style.transform = 'scale(0.95)';
        }
    });
    
    // Release - Solo detener si no es el botón STOP
    btn.addEventListener('mouseup', () => {
        btn.style.transform = '';
        if (currentMode === 'manual' && cmd !== 'S') {
            sendCommand('S');
        }
    });
    
    btn.addEventListener('touchend', (e) => {
        e.preventDefault();
        btn.style.transform = '';
        if (currentMode === 'manual' && cmd !== 'S') {
            sendCommand('S');
        }
    });
    
    // Cancelar si se sale del botón
    btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
        if (currentMode === 'manual' && cmd !== 'S') {
            sendCommand('S');
        }
    });
});

// ===== CONTROL DE VELOCIDAD =====
speedSlider.addEventListener('input', (e) => {
    const speed = e.target.value;
    speedValue.textContent = speed;
    robotSpeed.textContent = speed + '%';
});

speedSlider.addEventListener('change', (e) => {
    const speed = e.target.value;
    sendCommand('V' + speed);
});

// ===== CONTROL POR TECLADO =====
document.addEventListener('keydown', (e) => {
    if (currentMode !== 'manual') return;
    
    const keyMap = {
        'ArrowUp': 'F',
        'ArrowDown': 'B',
        'ArrowLeft': 'L',
        'ArrowRight': 'R',
        'w': 'F',
        'W': 'F',
        's': 'B',
        'S': 'B',
        'a': 'L',
        'A': 'L',
        'd': 'R',
        'D': 'R',
        ' ': 'S'
    };
    
    const cmd = keyMap[e.key];
    if (cmd) {
        e.preventDefault();
        sendCommand(cmd);
        
        // Efecto visual en el botón correspondiente
        const btn = document.querySelector(`[data-cmd="${cmd}"]`);
        if (btn) {
            btn.style.transform = 'scale(0.95)';
        }
    }
});

document.addEventListener('keyup', (e) => {
    if (currentMode !== 'manual') return;
    
    const keyMap = {
        'ArrowUp': 'F',
        'ArrowDown': 'B',
        'ArrowLeft': 'L',
        'ArrowRight': 'R',
        'w': 'F',
        'W': 'F',
        's': 'B',
        'S': 'B',
        'a': 'L',
        'A': 'L',
        'd': 'R',
        'D': 'R'
    };
    
    const cmd = keyMap[e.key];
    if (cmd) {
        e.preventDefault();
        sendCommand('S');
        
        // Restaurar botón
        const btn = document.querySelector(`[data-cmd="${cmd}"]`);
        if (btn) {
            btn.style.transform = '';
        }
    }
});

// ===== PREVENIR SCROLL EN MÓVIL =====
document.body.addEventListener('touchmove', (e) => {
    if (e.target.closest('.control-btn')) {
        e.preventDefault();
    }
}, { passive: false });

// ===== INICIALIZACIÓN =====
console.log('Robot Control Interface cargada');
console.log('Controles: Botones táctiles o teclado (WASD/Flechas)');
