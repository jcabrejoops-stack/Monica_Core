
// MÓNICA's Tetris Game

const canvas = document.getElementById('tetrisCanvas');
const context = canvas.getContext('2d');
const scoreDisplay = document.getElementById('scoreDisplay');

const ROW = 20;
const COL = 10;
const SQ = 20; // Tamaño de cada cuadro en píxeles
const VACANT = "BLACK"; // Color de un cuadro vacío

// Tetrominoes (piezas de Tetris y sus rotaciones)
const Z = [
    [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
    ],
    [
        [0, 1, 0],
        [1, 1, 0],
        [1, 0, 0]
    ],
    [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
    ],
    [
        [0, 1, 0],
        [1, 1, 0],
        [1, 0, 0]
    ]
];

const S = [
    [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ],
    [
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0]
    ],
    [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ],
    [
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0]
    ]
];

const T = [
    [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    [
        [0, 1, 0],
        [0, 1, 1],
        [0, 1, 0]
    ],
    [
        [0, 0, 0],
        [1, 1, 1],
        [0, 1, 0]
    ],
    [
        [0, 1, 0],
        [1, 1, 0],
        [0, 1, 0]
    ]
];

const O = [
    [
        [1, 1],
        [1, 1]
    ],
    [
        [1, 1],
        [1, 1]
    ],
    [
        [1, 1],
        [1, 1]
    ],
    [
        [1, 1],
        [1, 1]
    ]
];

const L = [
    [
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0]
    ],
    [
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 1]
    ],
    [
        [0, 0, 0],
        [1, 1, 1],
        [1, 0, 0]
    ],
    [
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 0]
    ]
];

const I = [
    [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    [
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0]
    ],
    [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    [
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0]
    ]
];

const J = [
    [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ],
    [
        [0, 1, 1],
        [0, 1, 0],
        [0, 1, 0]
    ],
    [
        [0, 0, 0],
        [1, 1, 1],
        [0, 0, 1]
    ],
    [
        [0, 1, 0],
        [0, 1, 0],
        [1, 1, 0]
    ]
];


let board = [];
for (let r = 0; r < ROW; r++) {
    board[r] = [];
    for (let c = 0; c < COL; c++) {
        board[r][c] = VACANT;
    }
}

function drawSquare(x, y, color) {
    context.fillStyle = color;
    context.fillRect(x * SQ, y * SQ, SQ, SQ);

    context.strokeStyle = "GHOSTWHITE";
    context.strokeRect(x * SQ, y * SQ, SQ, SQ);
}

function drawBoard() {
    for (let r = 0; r < ROW; r++) {
        for (let c = 0; c < COL; c++) {
            drawSquare(c, r, board[r][c]);
        }
    }
}

// Global variables for game state
let score = 0;
let gameOver = false;
let dropStart = Date.now();
const dropInterval = 1000; // milliseconds (velocidad de caída inicial)

// drawBoard(); // Esto se llamará en el bucle del juego

const PIECES = [
    [Z, "red"],
    [S, "green"],
    [T, "purple"],
    [O, "yellow"],
    [L, "orange"],
    [I, "cyan"],
    [J, "blue"]
];

function generateRandomPiece() {
    let r = Math.floor(Math.random() * PIECES.length); // 0 -> 6
    return new Piece(PIECES[r][0], PIECES[r][1]);
}

let p = generateRandomPiece(); // La pieza activa

function Piece(tetromino, color) {
    this.tetromino = tetromino;
    this.color = color;

    this.tetrominoN = 0; // Empieza con la primera rotación
    this.activeTetromino = this.tetromino[this.tetrominoN];

    this.x = 3;
    this.y = -2; // La pieza empieza ligeramente por encima del tablero
}

Piece.prototype.draw = function () {
    this.activeTetromino.forEach((row, r) => {
        row.forEach((value, c) => {
            if (value === 1) {
                drawSquare(this.x + c, this.y + r, this.color);
            }
        });
    });
};

Piece.prototype.undraw = function () {
    this.activeTetromino.forEach((row, r) => {
        row.forEach((value, c) => {
            if (value === 1) {
                drawSquare(this.x + c, this.y + r, VACANT);
            }
        });
    });
};

// Detección de colisiones
Piece.prototype.collision = function (x, y, piece) {
    for (let r = 0; r < piece.length; r++) {
        for (let c = 0; c < piece[r].length; c++) {
            if (piece[r][c] === 0) {
                continue;
            }
            let newX = this.x + c + x;
            let newY = this.y + r + y;

            // Condición para colisión con los límites del tablero (izq, der, abajo)
            if (newX < 0 || newX >= COL || newY >= ROW) {
                return true;
            }
            // Permitir que la pieza se forme fuera del tablero por arriba (y < 0)
            if (newY < 0) {
                continue;
            }
            // Colisión con otra pieza ya en el tablero
            if (board[newY][newX] !== VACANT) {
                return true;
            }
        }
    }
    return false;
};

// Mover pieza hacia abajo
Piece.prototype.moveDown = function () {
    if (!this.collision(0, 1, this.activeTetromino)) {
        this.undraw();
        this.y++;
        this.draw();
    } else {
        // La pieza ha colisionado, bloquearla
        this.lock();
        p = generateRandomPiece(); // Generar nueva pieza
        // Comprobar si la nueva pieza colisiona al instante (Game Over)
        if (p.collision(0, 0, p.activeTetromino)) {
            gameOver = true;
            alert("¡Game Over! Puntuación: " + score);
        }
    }
};

// Mover pieza a la derecha
Piece.prototype.moveRight = function () {
    if (!this.collision(1, 0, this.activeTetromino)) {
        this.undraw();
        this.x++;
        this.draw();
    }
};

// Mover pieza a la izquierda
Piece.prototype.moveLeft = function () {
    if (!this.collision(-1, 0, this.activeTetromino)) {
        this.undraw();
        this.x--;
        this.draw();
    }
};

// Rotar pieza
Piece.prototype.rotate = function () {
    let nextTetrominoN = (this.tetrominoN + 1) % this.tetromino.length;
    let nextTetromino = this.tetromino[nextTetrominoN];
    let kick = 0; // Para el "wall kick" si colisiona al rotar

    // Comprobar colisión al rotar
    if (this.collision(0, 0, nextTetromino)) {
        // Intentar mover la pieza para evitar la colisión (simple wall kick)
        if (this.x > COL / 2) { // Si la pieza está a la derecha
            kick = -1; // Mover a la izquierda
        } else { // Si la pieza está a la izquierda
            kick = 1; // Mover a la derecha
        }
        if (this.collision(kick, 0, nextTetromino)) {
            return; // No se puede rotar ni con "kick"
        }
    }

    this.undraw();
    this.x += kick; // Aplicar el "kick" si hubo
    this.tetrominoN = nextTetrominoN;
    this.activeTetromino = this.tetromino[this.tetrominoN];
    this.draw();
};

// Bloquear pieza en el tablero
Piece.prototype.lock = function () {
    this.activeTetromino.forEach((row, r) => {
        row.forEach((value, c) => {
            if (value === 1) {
                // Si la pieza se bloquea por encima del tablero, es Game Over
                if (this.y + r < 0) {
                    gameOver = true;
                } else {
                    board[this.y + r][this.x + c] = this.color;
                }
            }
        });
    });

    // Limpiar filas completas
    for (let r = 0; r < ROW; r++) {
        let isRowFull = true;
        for (let c = 0; c < COL; c++) {
            if (board[r][c] === VACANT) {
                isRowFull = false;
                break;
            }
        }
        if (isRowFull) {
            // Mover todas las filas superiores una posición hacia abajo
            for (let y = r; y > 1; y--) {
                for (let c = 0; c < COL; c++) {
                    board[y][c] = board[y - 1][c];
                }
            }
            // La fila superior se vuelve vacía
            for (let c = 0; c < COL; c++) {
                board[0][c] = VACANT;
            }
            score += 10; // Incrementar puntuación
        }
    }
    drawBoard(); // Redibujar el tablero después de limpiar líneas
    scoreDisplay.innerHTML = score; // Actualizar la puntuación en la interfaz
};


// Bucle principal del juego (caída automática de piezas)
function drop() {
    let now = Date.now();
    let delta = now - dropStart;

    if (delta > dropInterval && !gameOver) {
        p.moveDown();
        dropStart = Date.now();
    }
    if (!gameOver) {
        requestAnimationFrame(drop); // Llamar a la función nuevamente para el siguiente frame
    }
}

// Llamada inicial para iniciar el bucle del juego
drop();

// Controlar la pieza con el teclado
document.addEventListener("keydown", function (e) {
    if (gameOver) return; // No permitir movimientos si el juego ha terminado

    if (e.keyCode === 37) { // Flecha izquierda
        p.moveLeft();
        dropStart = Date.now(); // Resetear el temporizador de caída para dar tiempo a reaccionar
    } else if (e.keyCode === 38) { // Flecha arriba (rotar)
        p.rotate();
        dropStart = Date.now();
    } else if (e.keyCode === 39) { // Flecha derecha
        p.moveRight();
        dropStart = Date.now();
    } else if (e.keyCode === 40) { // Flecha abajo (caída acelerada)
        p.moveDown();
    }
});
