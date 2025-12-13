const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const app = express();
const PORT = 3000;

// Middleware
app.use(bodyParser.json());

// DB Setup (ファイルに保存)
const db = new sqlite3.Database('./data/snippets.db');

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
});

// 保存用API
app.post('/api/save', (req, res) => {
  const { content, category } = req.body;
  if (!content) return res.status(400).json({ error: 'No content' });

  const stmt = db.prepare("INSERT INTO snippets (content, category) VALUES (?, ?)");
  stmt.run(content, category || 'uncategorized', function(err) {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    console.log(`Saved: [${category}] ${content.substring(0, 20)}...`);
    res.json({ id: this.lastID, status: 'success' });
  });
  stmt.finalize();
});

// 確認用API (ブラウザで http://localhost:3000/api/list にアクセス)
app.get('/api/list', (req, res) => {
  db.all("SELECT * FROM snippets ORDER BY created_at DESC", [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});