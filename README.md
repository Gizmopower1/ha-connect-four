# 🔴🟡 Connect Four for Home Assistant

A family Connect Four game that runs inside Home Assistant. Everyone can play everyone at the same time
from the companion app, a wall tablet or a PC. It has a scoreboard, a running score per pair of players,
push notifications and its own sidebar entry.

## Features
- **A "Connect Four" sidebar entry** with the main menu, the boards and the scoreboard.
- **Players are picked from your Home Assistant persons**, so no YAML is needed.
- **One game per pair of players.** You can play several opponents at once, and each pair keeps its own score ("You 3 – 1 Player2").
- **Push notifications** when it is your turn ("Your turn against Player1! 🎯"). Tapping one opens the right board, and each player's phone is found automatically. Each player can turn their own notifications on or off with a switch in the main menu. They are on by default.
- **Anti-cheat:** a player who is logged in can only move in their own games, and only on their turn.
  A shared user (for example a wall tablet) can play for everyone.
- **Points:** win 3, lightning win +1 (≤ 7 own moves), draw 1, opponent resigned 3. You can change all of these.
- **Optional dashboard cards:** the full game, a small "your turn" card and a status card.
- English and Norwegian (Bokmål). The language follows your Home Assistant language setting.

## Installation (HACS)
1. HACS → ⋮ → **Custom repositories** → add `https://github.com/Gizmopower1/ha-connect-four` with type **Integration**.
2. Download **Connect Four** and restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration → Connect Four**.
4. Tick the players, then pick the phone each player should be notified on.

You can change the players and the points later under **Configure** on the integration.
To change the sidebar name, rename the integration entry.

## Dashboard cards (optional)
The sidebar entry is all you need to play. The cards are extras for your own dashboards. The integration
registers the dashboard resource (`/connect_four_static/connect-four.js`) itself.

| Mode | What it shows |
|---|---|
| `full` | The whole game: main menu, boards and scoreboard |
| `summary` | A compact "🎯 Your turn against Player2" card. Tap it to open the game |
| `status` | Whose turn it is in every game, plus who is leading |

```yaml
type: custom:connect-four-card
mode: summary
```

Ready-to-use examples are in [`examples/`](examples):
- [`summary-card.yaml`](examples/summary-card.yaml) is the summary card, shown only to the players.
- [`full-card-view.yaml`](examples/full-card-view.yaml) is a dashboard view with the full game.
- [`wallpanel-status.yaml`](examples/wallpanel-status.yaml) is the status card on a
  [WallPanel](https://github.com/j-a-n/lovelace-wallpanel) screensaver. It is optional and only useful if you use WallPanel.

| Option | Default | Description |
|---|---|---|
| `mode` | `full` | `full`, `summary` or `status` |
| `title` | "Connect Four" | Custom heading |
| `navigation_path` | `/connect-four` | Where the `summary` card goes when tapped |
| `glass` | `false` | Dark see-through background for `status`, for use on top of photos (e.g. WallPanel) |

## Entities and actions
| Entity | |
|---|---|
| `sensor.connect_four` | Number of games in progress. The card reads its attributes |
| `sensor.connect_four_<person>` | Points for each player, plus wins, draws and losses |
| `switch.connect_four_push_<person>` | Turns push notifications on or off for one player |

Actions: `connect_four.start`, `connect_four.drop`, `connect_four.resign`, `connect_four.set_notifications`, and `connect_four.reset_scores` (admin only).

## Upgrading from `fire_pa_rad`
Earlier versions of this integration were called `fire_pa_rad`. When you set up Connect Four, it picks up the
old players, phones, games and scores automatically, as long as the old integration is still set up. After that, remove the old integration and its
`custom_components/fire_pa_rad` folder. Then change `custom:fire-pa-rad-card` to `custom:connect-four-card` in your
dashboards. The old dashboard resource is removed automatically.

## License
MIT
