# 🔴🟡 4 på rad – Connect Four for Home Assistant

Et familiespill rett i Home Assistant. Alle i familien kan spille mot alle – samtidig – fra mobilappen,
nettbrettet på veggen eller PC-en. Med poengtavle, serier, push-varsler og et eget menypunkt i sidemenyen.

*English below.*

## Funksjoner
- **Eget menypunkt «4 på rad»** i sidemenyen – lobby, brett og poengtavle.
- **Velg spillerne blant personene i Home Assistant** – ingen YAML.
- **Ett parti per spillerpar** – spill mot flere samtidig, med egen serie per par («Du 3 – 1 Adrian»).
- **Push-varsel** når det er din tur («Din tur mot Gisle! 🎯») som åpner riktig brett. Mobilen finnes automatisk.
- **Juksesperre:** den som er logget inn kan bare flytte i egne partier, og bare på sin tur.
  En felles bruker (f.eks. veggnettbrett) kan spille for alle.
- **Poeng:** seier 3, lynseier +1 (≤ 7 egne trekk), uavgjort 1, motstander ga opp 3 – kan justeres.
- **Kort til egne dashbord** – fullt spill, et lite «Din tur»-kort, eller et statuskort til f.eks. WallPanel.
- Norsk og engelsk.

## Installasjon (HACS)
1. HACS → ⋮ → **Egendefinerte repositorier** → legg til `https://github.com/Gizmopower1/ha-fire-pa-rad`, type **Integrasjon**.
2. Last ned **4 på rad** og start Home Assistant på nytt.
3. **Innstillinger → Enheter og tjenester → Legg til integrasjon → 4 på rad**.
4. Kryss av spillerne, og velg mobilen hver spiller skal få varsler på.

Spillere og poeng endres senere under **Konfigurer** på integrasjonen.

## Kort til dashbord
Kortet lastes automatisk – integrasjonen registrerer selv dashbordressursen (`/fire_pa_rad_static/fire-pa-rad.js`).

```yaml
type: custom:fire-pa-rad-card   # fullt spill (lobby, brett, poengtavle)
```
```yaml
type: custom:fire-pa-rad-card   # «🎯 Din tur mot Adrian» – trykk for å åpne spillet
mode: summary
```
```yaml
type: custom:fire-pa-rad-card   # hvem sin tur + hvem som leder (fin i WallPanel)
mode: status
```

| Valg | Standard | Beskrivelse |
|---|---|---|
| `mode` | `full` | `full`, `summary` eller `status` |
| `title` | «4 på rad» | Egen overskrift |
| `navigation_path` | `/fire-pa-rad` | Hvor `summary` åpner |
| `glass` | `true` | Mørk, gjennomsiktig bakgrunn i `status` |

## Entiteter og tjenester
| Entitet | |
|---|---|
| `sensor.fire_pa_rad` | Antall partier i gang (attributtene brukes av kortet) |
| `sensor.fire_pa_rad_<person>` | Poeng per spiller (+ seire, uavgjort, tap) |
| `switch.…_push_varsler` | Slå push-varsler av/på |

Tjenester: `fire_pa_rad.start`, `fire_pa_rad.drop`, `fire_pa_rad.resign`, `fire_pa_rad.reset_scores` (admin).

---

## English
A Connect Four game for the whole family inside Home Assistant: pick the players among your HA persons,
play everyone at once from the companion app, get push notifications when it is your turn, and follow the
scoreboard. Adds a **Connect Four** sidebar entry and a `custom:fire-pa-rad-card` (`mode: full | summary | status`).

Install through HACS as a custom repository (type *Integration*), restart, then add the **4 på rad** integration.

## Lisens / License
MIT
