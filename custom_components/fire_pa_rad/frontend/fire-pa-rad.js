/* 4 på rad – card + sidebar panel for the fire_pa_rad integration. */
const FPR_VERSION = "0.1.2";

const FPR_T = {
  nb: {
    title: "4 på rad", your_games: "Dine partier", all_games: "Alle partier", scoreboard: "Poengtavle",
    rules: "Slik spiller du", back: "Alle partier", your_turn: "Din tur!", your_turn_vs: "Din tur mot {n}",
    turn_of: "{n} sin tur", turn_vs: "{n} sin tur mot {o}", waiting_for: "Venter på {n}", challenge: "Utfordre {n}", tap_start: "Trykk for å starte et parti",
    you_won: "Du vant!", you_beat: "Du slo {n}!", won: "{n} vant!", they_won: "{n} vant denne gangen", draw: "Uavgjort!",
    draw_vs: "Uavgjort mot {n}", new_round: "Ny runde", start: "Start spill", resign: "Gi opp", sure: "Sikker? Motstanderen får seieren.",
    yes: "Ja, gi opp", no: "Nei", cancel_info: "Under 2 brikker: partiet avbrytes uten poeng.", last_move: "siste trekk {t}",
    you_are: "Du er {d} mot {n}", push_info: "Du får push-varsel når det er din tur", no_game: "Ingen parti i gang",
    series: "Stilling", draws: "{d} uavgj.", no_games_yet: "Ingen partier ennå", you: "Du", tap_new: "Trykk for ny runde",
    games_total: "{n} partier spilt totalt", player: "Spiller", games: "Spill", w: "S", d: "U", l: "T", pct: "Seier%", points: "Poeng",
    leader: "👑 {n} leder med {p} poeng", shared_lead: "👑 Delt ledelse: {n} ({p} p)", none_active: "Ingen partier i gang",
    not_found: "Fant ikke {e}. Er integrasjonen «4 på rad» satt opp?", now: "akkurat nå", min: "for {n} min siden",
    hours: "for {n} t siden", days: "for {n} d siden", challenge_someone: "Trykk for å utfordre noen",
    tap_play: "Trykk for å spille", and: "og",
    rules_text: "<ol><li>Velg en motstander og trykk <b>Utfordre</b> – et 🪙 myntkast avgjør hvem som begynner.</li><li>Trykk på en <b>kolonne</b> for å slippe brikken din. Du kan ha partier mot alle samtidig.</li><li>Første til <b>fire på rad</b> – vannrett, loddrett eller på skrå – vinner.</li></ol>",
    points_text: "🏆 Seier {w} p · ⚡ Lynseier (≤ {m} egne trekk) +{b} · 🤝 Uavgjort {d} p · 🏳️ Motstander ga opp {w} p",
  },
  en: {
    title: "Connect Four", your_games: "Your games", all_games: "All games", scoreboard: "Scoreboard",
    rules: "How to play", back: "All games", your_turn: "Your turn!", your_turn_vs: "Your turn against {n}",
    turn_of: "{n}'s turn", turn_vs: "{n}'s turn against {o}", waiting_for: "Waiting for {n}", challenge: "Challenge {n}", tap_start: "Tap to start a game",
    you_won: "You won!", you_beat: "You beat {n}!", won: "{n} won!", they_won: "{n} won this time", draw: "Draw!",
    draw_vs: "Draw against {n}", new_round: "New round", start: "Start game", resign: "Resign", sure: "Sure? Your opponent wins.",
    yes: "Yes, resign", no: "No", cancel_info: "Under 2 pieces: the game is cancelled without points.", last_move: "last move {t}",
    you_are: "You are {d} against {n}", push_info: "You get a notification when it is your turn", no_game: "No game in progress",
    series: "Series", draws: "{d} draws", no_games_yet: "No games yet", you: "You", tap_new: "Tap for a new round",
    games_total: "{n} games played in total", player: "Player", games: "Games", w: "W", d: "D", l: "L", pct: "Win%", points: "Points",
    leader: "👑 {n} leads with {p} points", shared_lead: "👑 Shared lead: {n} ({p} p)", none_active: "No games in progress",
    not_found: "Could not find {e}. Is the Connect Four integration set up?", now: "just now", min: "{n} min ago",
    hours: "{n} h ago", days: "{n} d ago", challenge_someone: "Tap to challenge someone",
    tap_play: "Tap to play", and: "and",
    rules_text: "<ol><li>Pick an opponent and tap <b>Challenge</b> – a 🪙 coin toss decides who starts.</li><li>Tap a <b>column</b> to drop your piece. You can play everyone at the same time.</li><li>First to get <b>four in a row</b> – horizontally, vertically or diagonally – wins.</li></ol>",
    points_text: "🏆 Win {w} p · ⚡ Lightning win (≤ {m} own moves) +{b} · 🤝 Draw {d} p · 🏳️ Opponent resigned {w} p",
  },
};

const FPR_COLORS = ["#ff7043", "#ab47bc", "#42a5f5", "#66bb6a", "#ffa726", "#26c6da", "#ec407a", "#8d6e63"];

const FPR_CSS = `
  :host { display: block; }
  ha-card { padding: 16px; overflow: hidden; }
  .muted { opacity: .7; font-size: .88em; }
  h2 { margin: 4px 0 12px; font-size: 1.35em; display: flex; align-items: center; gap: 8px; }
  h3 { margin: 18px 0 8px; font-size: 1.05em; opacity: .85; }
  .tile { display: flex; align-items: center; gap: 14px; padding: 12px 14px; margin: 8px 0; border-radius: 16px;
          background: var(--secondary-background-color, rgba(127,127,127,.12)); cursor: pointer; transition: transform .1s; }
  .tile:active { transform: scale(.98); }
  .tile.hot { box-shadow: 0 0 0 2px #66bb6a, 0 0 16px rgba(102,187,106,.45); }
  .av { flex: none; width: 46px; height: 46px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 21px; color: #fff; background-size: cover; background-position: center; }
  .av.sm { width: 26px; height: 26px; font-size: .8em; margin-right: 8px; display: inline-flex; vertical-align: middle; }
  .t1 { font-weight: 700; font-size: 1.08em; }
  .dot { display: inline-block; width: .85em; height: .85em; border-radius: 50%; vertical-align: -1px; box-shadow: 0 0 0 2px rgba(255,255,255,.6); }
  .dot.r { background: #e53935; } .dot.y { background: #fdd835; }
  .status { padding: 14px 16px; border-radius: 16px; background: var(--secondary-background-color, rgba(127,127,127,.12)); margin-bottom: 12px; }
  .status .big { font-size: 1.4em; font-weight: 700; }
  .series { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--divider-color, rgba(127,127,127,.3)); }
  .back { cursor: pointer; display: inline-flex; align-items: center; gap: 6px; margin-bottom: 10px; color: var(--primary-color); font-weight: 600; }
  .board { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; padding: 8px 6px 10px; border-radius: 22px; max-width: 520px; margin: 0 auto;
           background: linear-gradient(180deg, #2372e8 0%, #0d3d91 100%); box-shadow: 0 10px 26px rgba(0,0,0,.45), inset 0 2px 0 rgba(255,255,255,.25); }
  .col { display: flex; flex-direction: column; align-items: center; gap: clamp(3px, 1.1vw, 7px); padding: 2px 0; border-radius: 12px; cursor: pointer; min-width: 0; }
  .col.locked { cursor: default; }
  .col:not(.locked):hover { background: rgba(255,255,255,.08); }
  .col > div { width: 86%; aspect-ratio: 1; border-radius: 50%; }
  .ghost { opacity: 0; transition: opacity .2s, transform .2s; }
  .ghost.r, .ghost.y { opacity: .35; }
  .col:not(.locked):hover .ghost.r, .col:not(.locked):hover .ghost.y { opacity: .9; transform: translateY(3px); }
  .cell { box-shadow: inset 0 4px 7px rgba(0,0,0,.55); }
  .e { background: rgba(8,18,48,.9); }
  .r { background: radial-gradient(circle at 35% 30%, #ff8a80, #e53935 55%, #a31515); }
  .y { background: radial-gradient(circle at 35% 30%, #fff59d, #fdd835 55%, #c6a700); }
  .cell.r, .cell.y { box-shadow: inset 0 -3px 6px rgba(0,0,0,.35), 0 2px 3px rgba(0,0,0,.4); }
  .last { animation: fpr-fall .6s cubic-bezier(.55,0,.8,1.25); }
  @keyframes fpr-fall { from { transform: translateY(calc(var(--rad) * -116%)); } to { transform: translateY(0); } }
  .win { animation: fpr-pulse .8s ease-in-out infinite alternate; box-shadow: 0 0 0 3px #fff, 0 0 14px 4px rgba(255,255,255,.8) !important; }
  @keyframes fpr-pulse { from { transform: scale(1); } to { transform: scale(1.1); } }
  .actions { display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; position: relative; clear: both; }
  .btn { flex: 1; min-width: 120px; border: none; border-radius: 14px; padding: 14px; font-size: 1em; font-weight: 700; color: #fff; cursor: pointer; }
  .btn.go { background: linear-gradient(90deg, #2e7d32, #43a047); }
  .btn.stop { background: #8e2424; }
  .btn.grey { background: #616161; }
  .err { margin-top: 10px; padding: 10px 12px; border-radius: 12px; background: rgba(229,57,53,.2); }
  table { width: 100%; border-collapse: collapse; }
  th { font-weight: 500; opacity: .65; font-size: .8em; text-align: center; padding: 4px 2px; }
  td { text-align: center; padding: 8px 2px; border-top: 1px solid var(--divider-color, rgba(127,127,127,.25)); }
  td.n, th.n { text-align: left; white-space: nowrap; font-weight: 600; }
  td.p { font-weight: 800; font-size: 1.2em; color: #f9a825; }
  tr.lead td { background: rgba(255,213,79,.1); }
  details { margin-top: 14px; } summary { cursor: pointer; font-weight: 600; }
  .glass { background: rgba(0,0,0,.6); color: #fff; text-shadow: 1px 1px 3px rgba(0,0,0,.8); border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.6); }
  .summary { display: flex; align-items: center; gap: 14px; cursor: pointer; }
  .summary .icon { font-size: 34px; }
  .kicker { opacity: .7; font-size: .8em; letter-spacing: .06em; text-transform: uppercase; }
`;

const fprEsc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fprLang = (hass) => (["nb", "no", "nn"].includes(String(hass?.locale?.language || hass?.language || "en").split("-")[0]) ? "nb" : "en");
const fprGameId = (a, b) => [a, b].sort().map((p) => p.split(".")[1]).join("__");
const fprNavigate = (path) => { history.pushState(null, "", path); window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } })); };

class FireParadCard extends HTMLElement {
  static getStubConfig() { return { mode: "full" }; }

  setConfig(config) {
    this._config = { entity: "sensor.fire_pa_rad", mode: "full", navigation_path: "/fire-pa-rad", ...config };
    this._sig = null;
    if (!this.shadowRoot) {
      this.attachShadow({ mode: "open" });
      this.shadowRoot.addEventListener("click", (ev) => this._onClick(ev));
    }
    this._render();
  }

  getCardSize() { return this._config?.mode === "full" ? 10 : 2; }

  connectedCallback() { this._tick = setInterval(() => { this._sig = null; this._render(); }, 60000); }
  disconnectedCallback() { clearInterval(this._tick); }

  set hass(hass) {
    this._hass = hass;
    const st = hass.states[this._config.entity];
    const sig = [st?.last_updated, hass.user?.id, fprLang(hass), this._selected, this._confirm, this._err].join("|");
    if (sig !== this._sig) { this._sig = sig; this._render(); }
  }

  select(gameId) { this._selected = gameId || null; this._confirm = false; this._sig = null; this._render(); this.dispatchEvent(new CustomEvent("fpr-select", { detail: this._selected })); }

  _t(key, vars = {}) {
    const s = (FPR_T[fprLang(this._hass)] || FPR_T.en)[key] || key;
    return s.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");
  }

  _ago(iso) {
    if (!iso) return "";
    const m = Math.round((Date.now() - new Date(iso)) / 60000);
    if (m < 1) return this._t("now");
    if (m < 60) return this._t("min", { n: m });
    if (m < 1440) return this._t("hours", { n: Math.round(m / 60) });
    return this._t("days", { n: Math.round(m / 1440) });
  }

  _model() {
    const st = this._hass?.states[this._config.entity];
    if (!st) return null;
    const a = st.attributes;
    const players = (a.players || []).map((p, i) => ({ ...p, color: FPR_COLORS[i % FPR_COLORS.length] }));
    const by = Object.fromEntries(players.map((p) => [p.person, p]));
    const me = players.find((p) => p.user_id && p.user_id === this._hass.user?.id)?.person || null;
    const pairs = [];
    for (let i = 0; i < players.length; i++)
      for (let j = i + 1; j < players.length; j++) {
        const [p1, p2] = [players[i].person, players[j].person].sort();
        const id = fprGameId(p1, p2);
        pairs.push({ id, game: { p1, p2, status: "none", wins1: 0, wins2: 0, draws: 0, ...(a.games || {})[id] } });
      }
    return { players, by, me, pairs, total: a.total || 0, last: a.last_result || "" };
  }

  _name(m, person) { return m.by[person]?.name || person; }
  _avatar(m, person, small = false) {
    const p = m.by[person] || {};
    const style = p.picture ? `background-image:url('${fprEsc(p.picture)}')` : `background:${p.color || "#888"}`;
    return `<span class="av${small ? " sm" : ""}" style="${style}">${p.picture ? "" : fprEsc((p.name || "?")[0])}</span>`;
  }
  _dot(game, person) { return `<span class="dot ${person === game.p1 ? "r" : "y"}"></span>`; }
  _active(g) { return g.status === "playing" ? (g.turn === 1 ? g.p1 : g.p2) : null; }
  _winner(g) { return g.result === "1" ? g.p1 : g.result === "2" ? g.p2 : null; }
  _list(names) { return names.length > 1 ? `${names.slice(0, -1).join(", ")} ${this._t("and")} ${names[names.length - 1]}` : names[0]; }

  _render() {
    if (!this.shadowRoot || !this._config || !this._hass) return;
    const m = this._model();
    let body;
    if (!m) body = `<ha-card><div class="muted">${this._t("not_found", { e: fprEsc(this._config.entity) })}</div></ha-card>`;
    else if (this._config.mode === "summary") body = this._renderSummary(m);
    else if (this._config.mode === "status") body = this._renderStatus(m);
    else body = `<ha-card>${this._selected ? this._renderGame(m) : this._renderLobby(m)}${this._err ? `<div class="err">${fprEsc(this._err)}</div>` : ""}</ha-card>`;
    this.shadowRoot.innerHTML = `<style>${FPR_CSS}</style>${body}`;
  }

  // ---- lobby -----------------------------------------------------------
  _renderLobby(m) {
    let html = `<h2>🔴🟡 ${fprEsc(this._config.title || this._t("title"))}</h2>`;
    if (m.me) {
      html += `<h3>${this._t("your_games")}</h3>`;
      for (const { id, game } of m.pairs.filter((x) => x.game.p1 === m.me || x.game.p2 === m.me)) html += this._opponentTile(m, id, game);
    } else {
      html += `<h3>${this._t("all_games")}</h3>`;
      for (const { id, game } of m.pairs) html += this._pairTile(m, id, game);
    }
    html += `<h3>${this._t("scoreboard")}</h3>${this._scoreboard(m)}`;
    const o = this._hass.states[this._config.entity]?.attributes || {};
    html += `<details><summary>${this._t("rules")}</summary>${this._t("rules_text")}<div class="muted">${this._t("points_text", { w: o.points_win ?? 3, d: o.points_draw ?? 1, m: o.lightning_moves ?? 7, b: o.lightning_bonus ?? 1 })}</div></details>`;
    return html;
  }

  _opponentTile(m, id, g) {
    const opp = g.p1 === m.me ? g.p2 : g.p1;
    const n = fprEsc(this._name(m, opp));
    const mine = g.p1 === m.me ? g.wins1 : g.wins2, theirs = g.p1 === m.me ? g.wins2 : g.wins1;
    let t, u, hot = false;
    if (g.status === "playing") {
      hot = this._active(g) === m.me;
      t = hot ? `🎯 ${this._t("your_turn_vs", { n })}` : `⏳ ${this._t("turn_of", { n })}`;
      u = this._t("last_move", { t: this._ago(g.updated) });
    } else if (g.status === "finished") {
      const w = this._winner(g);
      t = !w ? `🤝 ${this._t("draw_vs", { n })}` : w === m.me ? `🏆 ${this._t("you_beat", { n })}` : `😅 ${this._t("won", { n })}`;
      u = this._t("tap_new");
    } else { t = `⚔️ ${this._t("challenge", { n })}`; u = this._t("tap_start"); }
    const series = mine + theirs + (g.draws || 0) ? `${this._t("you")} ${mine} – ${theirs} ${n}${g.draws ? ` · ${this._t("draws", { d: g.draws })}` : ""}` : this._t("no_games_yet");
    return `<div class="tile${hot ? " hot" : ""}" data-action="open" data-game="${id}" data-opp="${fprEsc(opp)}">${this._avatar(m, opp)}<div><div class="t1">${t}</div><div class="muted">${u} · ${series}</div></div></div>`;
  }

  _pairTile(m, id, g) {
    const a = this._active(g);
    let u;
    if (g.status === "playing") u = `${this._dot(g, a)} <b>${fprEsc(this._t("turn_of", { n: this._name(m, a) }))}</b> · ${this._ago(g.updated)}`;
    else if (g.status === "finished") { const w = this._winner(g); u = w ? `🏆 ${fprEsc(this._t("won", { n: this._name(m, w) }))} · ${this._t("tap_new")}` : `🤝 ${this._t("draw")} · ${this._t("tap_new")}`; }
    else u = this._t("tap_start");
    return `<div class="tile" data-action="open" data-game="${id}"><div><div class="t1">${this._dot(g, g.p1)} ${fprEsc(this._name(m, g.p1))} <span class="muted">${g.wins1} – ${g.wins2}</span> ${fprEsc(this._name(m, g.p2))} ${this._dot(g, g.p2)}</div><div class="muted">${u}</div></div></div>`;
  }

  _scoreboard(m) {
    const rows = [...m.players].sort((a, b) => b.points - a.points || b.wins - a.wins || a.losses - b.losses);
    const medal = ["🥇", "🥈", "🥉"];
    const tr = rows.map((p, i) => `<tr${i === 0 && p.points > 0 ? ' class="lead"' : ""}><td>${medal[i] || i + 1 + "."}</td><td class="n">${this._avatar(m, p.person, true)}${fprEsc(p.name)}</td><td>${p.played}</td><td>${p.wins}</td><td>${p.draws}</td><td>${p.losses}</td><td>${p.played ? Math.round((100 * p.wins) / p.played) : 0}%</td><td class="p">${p.points}</td></tr>`).join("");
    return `<table><tr><th></th><th class="n">${this._t("player")}</th><th>${this._t("games")}</th><th>${this._t("w")}</th><th>${this._t("d")}</th><th>${this._t("l")}</th><th>${this._t("pct")}</th><th>${this._t("points")}</th></tr>${tr}</table><div class="muted" style="text-align:right;margin-top:6px">${this._t("games_total", { n: m.total })}</div>`;
  }

  // ---- one game -----------------------------------------------------------
  _renderGame(m) {
    const pair = m.pairs.find((x) => x.id === this._selected);
    if (!pair) { this._selected = null; return this._renderLobby(m); }
    const g = pair.game, id = pair.id;
    const active = this._active(g);
    const inGame = m.me === g.p1 || m.me === g.p2;
    const opp = m.me === g.p1 ? g.p2 : g.p1;
    let big, sub;
    if (g.status === "playing") {
      if (active === m.me) { big = `🎯 ${this._t("your_turn")}`; sub = this._t("you_are", { d: this._dot(g, m.me), n: fprEsc(this._name(m, opp)) }); }
      else if (inGame) { big = `⏳ ${fprEsc(this._t("turn_of", { n: this._name(m, active) }))}`; sub = this._t("push_info"); }
      else { big = `${this._dot(g, active)} ${fprEsc(this._t("turn_of", { n: this._name(m, active) }))}`; sub = this._t("last_move", { t: this._ago(g.updated) }); }
    } else if (g.status === "finished") {
      const w = this._winner(g);
      big = !w ? `🤝 ${this._t("draw")}` : w === m.me ? `🏆 ${this._t("you_won")}` : inGame ? `😅 ${fprEsc(this._t("they_won", { n: this._name(m, w) }))}` : `🏆 ${fprEsc(this._t("won", { n: this._name(m, w) }))}`;
      sub = "";
    } else { big = `🎮 ${this._t("no_game")}`; sub = ""; }
    const series = `${this._t("series")}: ${this._dot(g, g.p1)} ${fprEsc(this._name(m, g.p1))} <b>${g.wins1}</b> – <b>${g.wins2}</b> ${fprEsc(this._name(m, g.p2))} ${this._dot(g, g.p2)}${g.draws ? ` · ${this._t("draws", { d: g.draws })}` : ""}`;

    const board = g.board && g.board.length === 42 ? g.board : ".".repeat(42);
    const win = g.win || [];
    const canPlay = g.status === "playing" && (!inGame || active === m.me);
    const animKey = `${id}:${g.moves}`;
    const animate = this._animated !== animKey;
    this._animated = animKey;
    let cols = "";
    for (let c = 0; c < 7; c++) {
      let cells = "";
      for (let r = 0; r < 6; r++) {
        const i = r * 7 + c, v = board[i];
        const cls = v === "R" ? "r" : v === "Y" ? "y" : "e";
        const extra = win.includes(i) ? " win" : i === g.last && animate ? " last" : "";
        cells += `<div class="cell ${cls}${extra}" style="--rad:${r + 2}"></div>`;
      }
      const ghost = canPlay && board[c] === "." ? (g.turn === 1 ? "r" : "y") : "";
      cols += `<div class="col${canPlay && board[c] === "." ? "" : " locked"}" data-action="drop" data-col="${c}"><div class="ghost ${ghost}"></div>${cells}</div>`;
    }

    let actions;
    if (g.status === "playing") {
      actions = this._confirm
        ? `<div class="muted" style="width:100%">${this._t((g.moves || 0) < 2 ? "cancel_info" : "sure")}</div><button class="btn stop" data-action="resign-yes">${this._t("yes")}</button><button class="btn grey" data-action="resign-no">${this._t("no")}</button>`
        : `<button class="btn stop" data-action="resign">🏳️ ${this._t("resign")}</button>`;
    } else actions = `<button class="btn go" data-action="start" data-game="${id}">▶ ${this._t(g.status === "finished" ? "new_round" : "start")}</button>`;

    return `<div class="back" data-action="back">← ${this._t("back")}</div>
      <div class="status"><div class="big">${big}</div>${sub ? `<div class="muted">${sub}</div>` : ""}<div class="series">${series}</div></div>
      <div class="board">${cols}</div><div class="actions">${actions}</div>`;
  }

  // ---- compact modes ---------------------------------------------------------
  _renderSummary(m) {
    let t, u, hot = false;
    if (m.me) {
      const mine = m.pairs.map((x) => x.game).filter((g) => g.status === "playing" && (g.p1 === m.me || g.p2 === m.me));
      const opp = (g) => this._name(m, g.p1 === m.me ? g.p2 : g.p1);
      const myTurn = mine.filter((g) => this._active(g) === m.me).map(opp);
      const waiting = mine.filter((g) => this._active(g) !== m.me).map(opp);
      if (myTurn.length) { hot = true; t = `🎯 ${this._t("your_turn_vs", { n: this._list(myTurn) })}`; u = waiting.length ? this._t("waiting_for", { n: this._list(waiting) }) : this._t("tap_play"); }
      else if (waiting.length) { t = `⏳ ${this._t("waiting_for", { n: this._list(waiting) })}`; u = this._t("push_info"); }
      else { t = `⚔️ ${this._t("none_active")}`; u = this._t("challenge_someone"); }
    } else {
      const n = m.pairs.filter((x) => x.game.status === "playing").length;
      t = n ? `🎮 ${n}` : `⚔️ ${this._t("none_active")}`; u = this._t("tap_start");
    }
    return `<ha-card style="${hot ? "box-shadow:0 0 0 2px #66bb6a,0 0 18px rgba(102,187,106,.6)" : ""}"><div class="summary" data-action="nav"><div class="icon">🎮</div><div><div class="kicker">${fprEsc(this._config.title || this._t("title"))}</div><div class="t1">${fprEsc(t)}</div><div class="muted">${fprEsc(u)}</div></div></div></ha-card>`;
  }

  _renderStatus(m) {
    const lines = m.pairs.map((x) => x.game).filter((g) => g.status === "playing").map((g) => {
      const a = this._active(g), o = a === g.p1 ? g.p2 : g.p1;
      return `${this._dot(g, a)} ${fprEsc(this._t("turn_vs", { n: this._name(m, a), o: this._name(m, o) }))}`;
    });
    const sorted = [...m.players].sort((a, b) => b.points - a.points);
    const top = sorted.filter((p) => p.points > 0 && p.points === sorted[0].points);
    const leader = top.length === 1 ? this._t("leader", { n: fprEsc(top[0].name), p: top[0].points }) : top.length > 1 ? this._t("shared_lead", { n: fprEsc(this._list(top.map((p) => p.name))), p: top[0].points }) : "";
    const glass = this._config.glass !== false;
    return `<ha-card class="${glass ? "glass" : ""}" style="${glass ? "background:rgba(0,0,0,.6)" : ""}"><div style="font-weight:700;font-size:1.1em;margin-bottom:4px">🎮 ${fprEsc(this._config.title || this._t("title"))}</div><div style="line-height:1.6;font-weight:600">${lines.length ? lines.join("<br>") : `<span class="muted">${this._t("none_active")}</span>`}</div>${leader ? `<div style="margin-top:6px;color:#ffd54f;font-weight:600">${leader}</div>` : ""}</ha-card>`;
  }

  // ---- actions ---------------------------------------------------------------
  async _call(service, data) {
    try {
      return await this._hass.callWS({ type: "call_service", domain: "fire_pa_rad", service, service_data: data, return_response: service === "start" });
    } catch (e) {
      this._err = e?.message || String(e);
      this._sig = null; this._render();
      setTimeout(() => { this._err = null; this._sig = null; this._render(); }, 5000);
      return null;
    }
  }

  async _onClick(ev) {
    const el = ev.composedPath().find((n) => n.dataset && n.dataset.action);
    if (!el) return;
    const m = this._model();
    const action = el.dataset.action;
    if (action === "nav") return fprNavigate(this._config.navigation_path);
    if (action === "back") return this.select(null);
    if (action === "open") {
      const pair = m.pairs.find((x) => x.id === el.dataset.game);
      if (pair && pair.game.status === "none" && el.dataset.opp) await this._call("start", { opponent: el.dataset.opp });
      return this.select(el.dataset.game);
    }
    const pair = m.pairs.find((x) => x.id === this._selected);
    if (!pair) return;
    if (action === "drop" && !el.classList.contains("locked")) return this._call("drop", { game_id: pair.id, column: Number(el.dataset.col) });
    if (action === "start") return this._call("start", m.me === pair.game.p1 || m.me === pair.game.p2 ? { opponent: m.me === pair.game.p1 ? pair.game.p2 : pair.game.p1 } : { player: pair.game.p1, opponent: pair.game.p2 });
    if (action === "resign") { this._confirm = true; this._sig = null; return this._render(); }
    if (action === "resign-no") { this._confirm = false; this._sig = null; return this._render(); }
    if (action === "resign-yes") { this._confirm = false; return this._call("resign", { game_id: pair.id }); }
  }
}

class FireParadPanel extends HTMLElement {
  set hass(hass) {
    this._hass = hass;
    if (!this._card) this._build();
    this._card.hass = hass;
    if (this._menu) this._menu.hass = hass;
  }
  set narrow(narrow) { this._narrow = narrow; if (this._menu) this._menu.narrow = narrow; }
  set panel(panel) { this._panel = panel; }

  connectedCallback() {
    this._onLoc = () => this._readLocation();
    window.addEventListener("location-changed", this._onLoc);
    window.addEventListener("popstate", this._onLoc);
  }
  disconnectedCallback() {
    window.removeEventListener("location-changed", this._onLoc);
    window.removeEventListener("popstate", this._onLoc);
  }

  _build() {
    const root = this.attachShadow({ mode: "open" });
    root.innerHTML = `<style>
      :host { display:block; min-height:100vh; background: var(--primary-background-color); color: var(--primary-text-color); }
      .bar { display:flex; align-items:center; gap:8px; height:56px; padding:0 8px; background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff); font-size:20px; }
      .wrap { max-width: 620px; margin: 0 auto; padding: 12px; }
    </style><div class="bar"><span id="menu"></span><span>${fprEsc(this._panel?.title || FPR_T[fprLang(this._hass)].title)}</span></div><div class="wrap"></div>`;
    this._menu = document.createElement("ha-menu-button");
    this._menu.hass = this._hass;
    this._menu.narrow = this._narrow;
    root.getElementById("menu").appendChild(this._menu);
    this._card = document.createElement("fire-pa-rad-card");
    this._card.setConfig({ mode: "full" });
    this._card.addEventListener("fpr-select", (ev) => {
      const url = new URL(location.href);
      if (ev.detail) url.searchParams.set("game", ev.detail); else url.searchParams.delete("game");
      history.replaceState(null, "", url.pathname + url.search);
    });
    root.querySelector(".wrap").appendChild(this._card);
    this._readLocation();
  }

  _readLocation() {
    if (!this._card || !location.pathname.startsWith("/fire-pa-rad")) return;
    const game = new URLSearchParams(location.search).get("game");
    if ((game || null) !== (this._card._selected || null)) this._card.select(game);
  }
}

if (!customElements.get("fire-pa-rad-card")) customElements.define("fire-pa-rad-card", FireParadCard);
if (!customElements.get("fire-pa-rad-panel")) customElements.define("fire-pa-rad-panel", FireParadPanel);
window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "fire-pa-rad-card"))
  window.customCards.push({ type: "fire-pa-rad-card", name: "4 på rad", description: "Connect Four for the family (modes: full, summary, status)", preview: false });
console.info(`%c 4 PÅ RAD %c ${FPR_VERSION} `, "background:#e53935;color:#fff;font-weight:700", "background:#fdd835;color:#000;font-weight:700");
