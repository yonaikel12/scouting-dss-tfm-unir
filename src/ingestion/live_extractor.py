"""Módulo de extracción en vivo por lotes de equipo desde API-Football v3.

Arquitectura resiliente para el plan gratuito de API-Football:
- Resuelve la restricción Free de la API: el parámetro 'page' no puede ser > 3 a nivel de liga.
- Itera equipo por equipo (/players?team={id}&season={season}), donde cada plantilla ocupa
  únicamente 2 páginas (máx 40 jugadores/club), eludiendo el límite de paginación global.
- Día 1: 20 clubes de La Liga + 20 clubes de Premier League (~82 peticiones, ~1.300 futbolistas).
- Día 2: Serie A, Bundesliga y Ligue 1 (~85 peticiones, ~1.400 futbolistas).
- Control estricto de cadencia: 6.5 segundos entre llamadas (máx 10 req/min).
- Checkpointing en `data/raw/live_ingestion_state.json` para reanudar sin pérdidas.
"""

from io import open
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
import requests

from src.ingestion.api_client import APIFootballClient
from src.ingestion.real_players_catalog import get_verified_420_real_players

logger = logging.getLogger(__name__)

TARGET_LEAGUES = [
    {"id": 140, "name": "La Liga", "country": "Spain"},
    {"id": 39, "name": "Premier League", "country": "England"},
    {"id": 135, "name": "Serie A", "country": "Italy"},
    {"id": 78, "name": "Bundesliga", "country": "Germany"},
    {"id": 61, "name": "Ligue 1", "country": "France"},
    {"id": 88, "name": "Eredivisie", "country": "Netherlands"},
]


class TeamBatchLiveExtractor:
    """Extractor en vivo por lotes de equipos para sortear la restricción page <= 3 del plan gratuito."""

    def __init__(
        self,
        season: int = 2023,
        min_request_interval: float = 6.5,
        min_requests_safety_margin: int = 4,
        project_root: Optional[Path] = None,
    ) -> None:
        self.season = season
        self.min_interval = min_request_interval
        self.safety_margin = min_requests_safety_margin
        self.project_root = project_root or Path(__file__).resolve().parents[2]

        env_file = self.project_root / ".env"
        load_dotenv(env_file)
        self.api_key = os.getenv("API_FOOTBALL_KEY", "")
        if not self.api_key:
            raise ValueError("No se encontró la variable API_FOOTBALL_KEY en el archivo .env")

        self.raw_dir = self.project_root / "data" / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.raw_dir / "live_ingestion_state.json"
        self.raw_jsonl_file = self.raw_dir / "live_api_football_players.jsonl"
        self.bronze_flat_file = self.raw_dir / "live_players_bronze.jsonl"

        # Mapeo de posesión de clubes
        self.possession_lookup: Dict[str, float] = {}
        for p in get_verified_420_real_players():
            self.possession_lookup[str(p["club_name"])] = float(p["team_possession_pct"])

    def _get_status(self) -> Dict[str, Any]:
        """Consulta el estado y saldo de peticiones del día."""
        headers = {"x-apisports-key": self.api_key}
        resp = requests.get("https://v3.football.api-sports.io/status", headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json().get("response", {})

    def _get_league_teams(self, league_id: int) -> List[Dict[str, Any]]:
        """Obtiene la lista de clubes de una competición."""
        headers = {"x-apisports-key": self.api_key}
        resp = requests.get(
            "https://v3.football.api-sports.io/teams",
            headers=headers,
            params={"league": league_id, "season": self.season},
            timeout=25,
        )
        resp.raise_for_status()
        data = resp.json().get("response", [])
        teams = []
        for item in data:
            t = item.get("team", {})
            if t.get("id"):
                teams.append({"id": t["id"], "name": t.get("name", "Unknown")})
        return teams

    def load_state(self) -> Dict[str, Any]:
        """Carga el estado previo de la descarga."""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "completed_leagues": [],
            "current_league_index": 0,
            "current_team_index": 0,
            "teams_cache": {},
            "total_players_extracted": 0,
            "total_calls_made": 0,
        }

    def save_state(self, state: Dict[str, Any]) -> None:
        """Guarda el estado actual de forma segura."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def run_daily_batch(self, max_calls_today: int = 80) -> Dict[str, Any]:
        """Ejecuta la ingesta equipo por equipo respetando cuota diaria y cadencia."""
        status = self._get_status()
        requests_info = status.get("requests", {})
        current_used = int(requests_info.get("current", 0))
        limit_day = int(requests_info.get("limit_day", 100))
        remaining_today = max(0, limit_day - current_used)

        print(f"\n=======================================================")
        print(f"ESTADO DE LA API (dashboard.api-football.com)")
        print(f"=======================================================")
        print(f"Plan: {status.get('subscription', {}).get('plan', 'Free')}")
        print(f"Peticiones usadas hoy: {current_used} / {limit_day}")
        print(f"Peticiones disponibles hoy: {remaining_today}")
        print(f"=======================================================\n")

        if remaining_today <= self.safety_margin:
            print("AVISO: Cuota de hoy alcanzada. Se reanudará automáticamente al resetearse a las 00:00 UTC.")
            return {"status": "QUOTA_EXHAUSTED", "remaining": remaining_today}

        allowed_calls = min(max_calls_today, remaining_today - self.safety_margin)
        print(f"Peticiones autorizadas para este lote de hoy: {allowed_calls}\n")

        state = self.load_state()
        calls_done_this_session = 0

        while calls_done_this_session < allowed_calls:
            l_idx = state.get("current_league_index", 0)
            if l_idx >= len(TARGET_LEAGUES):
                print("\n¡FELICIDADES! Las 5 Grandes Ligas europeas han sido completamente extraídas.")
                break

            league = TARGET_LEAGUES[l_idx]
            league_key = str(league["id"])

            # Cargar o consultar clubes de la liga si no están en caché
            if league_key not in state.get("teams_cache", {}):
                print(f"[{calls_done_this_session + 1}/{allowed_calls}] Obteniendo catálogo de clubes de {league['name']}...")
                teams = self._get_league_teams(league["id"])
                calls_done_this_session += 1
                state["total_calls_made"] = state.get("total_calls_made", 0) + 1
                if "teams_cache" not in state:
                    state["teams_cache"] = {}
                state["teams_cache"][league_key] = teams
                state["current_team_index"] = 0
                self.save_state(state)
                time.sleep(self.min_interval)
                continue

            teams = state["teams_cache"][league_key]
            t_idx = state.get("current_team_index", 0)

            if t_idx >= len(teams):
                if league["name"] not in state["completed_leagues"]:
                    state["completed_leagues"].append(league["name"])
                print(f"\n[OK] LIGA COMPLETADA: {league['name']} ({len(teams)} clubes)!\n")
                state["current_league_index"] += 1
                state["current_team_index"] = 0
                self.save_state(state)
                continue

            team = teams[t_idx]
            print(f"[{calls_done_this_session + 1}/{allowed_calls}] Extrayendo {league['name']} | Club [{t_idx + 1}/{len(teams)}]: {team['name']} (ID {team['id']})...")

            # Consultamos las páginas 1 y 2 del club (plantilla completa)
            for page in [1, 2]:
                if calls_done_this_session >= allowed_calls:
                    break

                t0 = time.time()
                headers = {"x-apisports-key": self.api_key}
                params = {"team": team["id"], "season": self.season, "page": page}

                resp = requests.get(
                    "https://v3.football.api-sports.io/players",
                    headers=headers,
                    params=params,
                    timeout=25,
                )
                calls_done_this_session += 1
                state["total_calls_made"] = state.get("total_calls_made", 0) + 1

                if resp.status_code == 200:
                    data = resp.json()
                    players_raw = data.get("response", [])
                    paging = data.get("paging", {})
                    total_pages = int(paging.get("total", 1))

                    if players_raw:
                        with open(self.raw_jsonl_file, "a", encoding="utf-8") as f_raw, \
                             open(self.bronze_flat_file, "a", encoding="utf-8") as f_flat:
                            for raw_p in players_raw:
                                f_raw.write(json.dumps(raw_p, ensure_ascii=False) + "\n")
                                flat = APIFootballClient.flatten_player_payload(
                                    raw_p,
                                    season=self.season,
                                    team_possession_lookup=self.possession_lookup,
                                )
                                if flat is not None and flat["player_id"] > 0:
                                    f_flat.write(json.dumps(flat, ensure_ascii=False) + "\n")
                                    state["total_players_extracted"] = state.get("total_players_extracted", 0) + 1

                        print(f"      Página {page}: +{len(players_raw)} jugadores guardados.")

                    # Si el club no tiene más páginas, no consultar la página 2
                    if page >= total_pages:
                        break

                elapsed = time.time() - t0
                if elapsed < self.min_interval:
                    time.sleep(self.min_interval - elapsed)

            state["current_team_index"] = t_idx + 1
            self.save_state(state)

        print("\n=======================================================")
        print(f"RESUMEN DE LA SESIÓN DE HOY")
        print(f"=======================================================")
        print(f"Peticiones ejecutadas en esta sesión: {calls_done_this_session}")
        print(f"Total futbolistas reales acumulados en disco: {state.get('total_players_extracted', 0)}")
        print(f"Ligas completadas: {state.get('completed_leagues', [])}")
        if state.get("current_league_index", 0) < len(TARGET_LEAGUES):
            curr_l = TARGET_LEAGUES[state['current_league_index']]
            print(f"Siguiente objetivo en Día 2: {curr_l['name']} (Club {state.get('current_team_index', 0) + 1})")
        print(f"=======================================================\n")

        return state


if __name__ == "__main__":
    extractor = TeamBatchLiveExtractor()
    extractor.run_daily_batch(max_calls_today=80)
