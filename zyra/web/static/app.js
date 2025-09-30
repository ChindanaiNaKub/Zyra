const api = {
  async post(path, body) {
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async get(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }
};

function $(sel){ return document.querySelector(sel); }

function render(state){
  const app = $('#app');
  app.innerHTML = `
    <div class="container">
      <h1>Zyra Web UI</h1>
      <div class="controls">
        <label>Style:
          <select id="style">
            <option value="aggressive">aggressive</option>
            <option value="defensive">defensive</option>
            <option value="experimental">experimental</option>
          </select>
        </label>
        <label>Think (ms):
          <input id="think" type="number" value="500" min="100" step="100" />
        </label>
        <button id="new">New Game</button>
      </div>
      <div class="status">
        <div>Side to move: <strong>${state.side_to_move}</strong></div>
        <div>Eval (cp): <strong>${Math.round(state.eval_cp ?? 0)}</strong></div>
        <div style="margin-top:6px; font-size: 12px; opacity: 0.8;">FEN: <code id="fen">${state.fen}</code></div>
      </div>
      <div class="layout">
        <div class="board" id="board"></div>
        <div class="history"><h3>History</h3><pre>${state.history.join(' ')}</pre></div>
      </div>
    </div>
  `;

  $('#new').onclick = async () => {
    const style = $('#style').value;
    const movetime_ms = parseInt($('#think').value, 10) || 500;
    const s = await api.post('/api/new', { style, movetime_ms });
    render(s);
  };

  drawBoard(state);
}

function parseFenPieces(fen){
  const board = {};
  const parts = fen.split(' ');
  const placement = parts[0];
  const rows = placement.split('/');
  for(let r=8; r>=1; r--){
    const rowStr = rows[8 - r];
    let file=0;
    for(const ch of rowStr){
      if(/[1-8]/.test(ch)){
        file += parseInt(ch,10);
      } else {
        const sq = 'abcdefgh'[file] + r;
        board[sq] = ch; // piece letter
        file++;
      }
    }
  }
  return board;
}

const PIECE_TO_SYMBOL = {
  'P': '♙','N': '♘','B': '♗','R': '♖','Q': '♕','K': '♔',
  'p': '♟','n': '♞','b': '♝','r': '♜','q': '♛','k': '♚',
};

async function drawBoard(state){
  const board = $('#board');
  board.innerHTML = '';
  const squares = [];
  // Basic 8x8 grid; click from->to for now
  for(let r=8; r>=1; r--){
    const row = document.createElement('div');
    row.className = 'row';
    for(let f=0; f<8; f++){
      const sq = document.createElement('div');
      sq.className = 'sq ' + (((r+f)%2===0)?'light':'dark');
      const alg = 'abcdefgh'[f] + r;
      sq.dataset.square = alg;
      row.appendChild(sq);
      squares.push(sq);
    }
    board.appendChild(row);
  }

  // Render pieces according to FEN
  const pieceMap = parseFenPieces(state.fen);
  for(const sq of squares){
    const p = pieceMap[sq.dataset.square];
    if(p){
      const span = document.createElement('span');
      const isWhite = p === p.toUpperCase();
      span.className = 'piece ' + (isWhite ? 'white' : 'black');
      span.textContent = PIECE_TO_SYMBOL[p] || p;
      span.draggable = true;
      sq.appendChild(span);
    }
  }

  let fromSq = null;
  let legalTargets = [];
  async function showLegal(from){
    legalTargets = [];
    squares.forEach(s => s.classList.remove('legal'));
    try{
      const res = await api.get(`/api/legal?from=${from}`);
      legalTargets = res.targets || [];
      squares.forEach(s => {
        if(legalTargets.includes(s.dataset.square)){
          s.classList.add('legal');
        }
      });
    } catch(_){}
  }

  squares.forEach(sq => {
    sq.onclick = async () => {
      if(!fromSq){
        fromSq = sq.dataset.square;
        squares.forEach(s => s.classList.remove('selected'));
        sq.classList.add('selected');
        await showLegal(fromSq);
      } else {
        const to = sq.dataset.square;
        const uci = fromSq + to;
        try {
          const ns = await api.post('/api/move', { uci });
          render(ns);
        } catch(e){
          // On illegal, refresh state and keep UX consistent
          const st = await api.get('/api/state');
          render(st);
        }
        fromSq = null;
      }
    };

    // Drag and drop handlers
    sq.ondragover = (e) => {
      e.preventDefault(); // Allow drop
      if (legalTargets.includes(sq.dataset.square)) {
        sq.classList.add('drag-over');
      }
    };

    sq.ondragleave = () => {
      sq.classList.remove('drag-over');
    };

    sq.ondrop = async (e) => {
      e.preventDefault();
      sq.classList.remove('drag-over');

      const fromSq = e.dataTransfer.getData('text/plain');
      const toSq = sq.dataset.square;

      if (fromSq && toSq && fromSq !== toSq) {
        const uci = fromSq + toSq;
        try {
          const ns = await api.post('/api/move', { uci });
          render(ns);
        } catch(e){
          // On illegal, refresh state and keep UX consistent
          const st = await api.get('/api/state');
          render(st);
        }
      }
    };
  });

  // Piece drag handlers
  document.querySelectorAll('.piece').forEach(piece => {
    piece.ondragstart = (e) => {
      const square = piece.parentElement.dataset.square;
      e.dataTransfer.setData('text/plain', square);
      e.dataTransfer.effectAllowed = 'move';

      // Show legal moves for this piece
      showLegal(square);

      // Add dragging class for visual feedback
      piece.classList.add('dragging');
    };

    piece.ondragend = () => {
      // Clean up visual feedback
      document.querySelectorAll('.sq').forEach(s => {
        s.classList.remove('drag-over');
      });
      piece.classList.remove('dragging');
    };
  });
}

async function init(){
  const state = await api.post('/api/new', {});
  render(state);
}

init();
