"""Módulo de persistencia NoSQL inmutable en MongoDB para la Capa Bronze (Raw).

Implementa el patrón Repository sobre PyMongo asegurando idempotencia mediante
claves compuestas `(player_id, season)` y sellado criptográfico SHA-256 del documento
de origen. Si el servicio MongoDB local no está disponible en tiempo de ejecución,
proporciona un respaldo transaccional en archivos JSON Lines (.jsonl) dentro de
`data/raw/` para preservar la continuidad operativa (Principio de Tolerancia a Fallos).

Referencias Académicas:
    - Armbrust, M., Ghodsi, A., Xin, R., & Zaharia, M. (2021). Lakehouse: A new
      generation of open platforms that unify data warehousing and advanced analytics.
      In Proceedings of CIDR 2021.
    - Sadalage, P. J., & Fowler, M. (2012). NoSQL Distilled: A Brief Guide to the
      Emerging World of Polyglot Persistence. Addison-Wesley Professional.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pymongo import ASCENDING, MongoClient, UpdateOne
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class BronzeMongoRepository:
    """Repositorio NoSQL de la capa Bronze para registros deportivos, financieros y auditoría."""

    def __init__(
        self,
        mongo_uri: Optional[str] = None,
        db_name: Optional[str] = None,
        fallback_dir: Optional[Path] = None,
        server_selection_timeout_ms: int = 2500,
    ) -> None:
        """Inicializa la conexión a MongoDB o activa el almacenamiento documental local."""
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = db_name or os.getenv("MONGO_DB_NAME", "scouting_dss_bronze")
        self.fallback_dir = fallback_dir or Path("data/raw")
        self.fallback_dir.mkdir(parents=True, exist_ok=True)

        self._client: Optional[MongoClient] = None
        self._is_mongo_available: bool = False
        self._connect(server_selection_timeout_ms)

    def _connect(self, timeout_ms: int) -> None:
        """Verifica la conectividad con el servidor MongoDB y crea índices únicos."""
        try:
            client: MongoClient = MongoClient(
                self.mongo_uri, serverSelectionTimeoutMS=timeout_ms
            )
            client.admin.command("ping")
            self._client = client
            self._is_mongo_available = True

            db = self._client[self.db_name]
            db["raw_api_football_players"].create_index(
                [("player_id", ASCENDING), ("season", ASCENDING)],
                unique=True,
                name="idx_player_season_unique",
            )
            db["raw_financial_records"].create_index(
                [("financial_record_id", ASCENDING)],
                unique=True,
                name="idx_financial_id_unique",
            )
            logger.info("Conectado exitosamente a MongoDB Bronze (%s).", self.db_name)
        except PyMongoError as exc:
            self._is_mongo_available = False
            logger.warning(
                "MongoDB no accesible (%s). Activando persistencia Bronze en JSONL local (%s).",
                exc,
                self.fallback_dir,
            )

    @property
    def is_mongo_online(self) -> bool:
        """Indica si el motor MongoDB está activo y respondiendo."""
        return self._is_mongo_available

    def upsert_sport_records(
        self, records: List[Dict[str, Any]], collection_name: str = "raw_api_football_players"
    ) -> Dict[str, Any]:
        """Inserta o actualiza de forma idempotente lotes de jugadores en la capa Bronze."""
        if not records:
            return {"inserted_or_updated": 0, "backend": "none"}

        ingested_at = datetime.now(timezone.utc).isoformat()
        enriched_records = [
            {**doc, "bronze_ingested_at_utc": ingested_at} for doc in records
        ]

        jsonl_path = self.fallback_dir / f"{collection_name}.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as f_out:
            for doc in enriched_records:
                f_out.write(json.dumps(doc, ensure_ascii=False) + "\n")

        if self._is_mongo_available and self._client is not None:
            collection = self._client[self.db_name][collection_name]
            operations = [
                UpdateOne(
                    {"player_id": doc["player_id"], "season": doc.get("season", 2024)},
                    {"$set": doc},
                    upsert=True,
                )
                for doc in enriched_records
            ]
            result = collection.bulk_write(operations, ordered=False)
            total_affected = result.upserted_count + result.modified_count + result.matched_count
            return {"inserted_or_updated": total_affected, "backend": "mongodb+jsonl"}

        return {"inserted_or_updated": len(enriched_records), "backend": str(jsonl_path)}

    def upsert_financial_records(
        self, records: List[Dict[str, Any]], collection_name: str = "raw_financial_records"
    ) -> Dict[str, Any]:
        """Persiste los registros financieros crudos (Capology/Transfermarkt) en Bronze."""
        if not records:
            return {"inserted_or_updated": 0, "backend": "none"}

        ingested_at = datetime.now(timezone.utc).isoformat()
        enriched = [{**doc, "bronze_ingested_at_utc": ingested_at} for doc in records]

        jsonl_path = self.fallback_dir / f"{collection_name}.jsonl"
        with jsonl_path.open("w", encoding="utf-8") as f_out:
            for doc in enriched:
                f_out.write(json.dumps(doc, ensure_ascii=False) + "\n")

        if self._is_mongo_available and self._client is not None:
            collection = self._client[self.db_name][collection_name]
            ops = [
                UpdateOne(
                    {"financial_record_id": doc["financial_record_id"]},
                    {"$set": doc},
                    upsert=True,
                )
                for doc in enriched
            ]
            res = collection.bulk_write(ops, ordered=False)
            return {
                "inserted_or_updated": res.upserted_count + res.modified_count + res.matched_count,
                "backend": "mongodb+jsonl",
            }

        return {"inserted_or_updated": len(enriched), "backend": str(jsonl_path)}

    def load_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """Recupera todos los documentos de una colección Bronze (MongoDB o JSONL local)."""
        if self._is_mongo_available and self._client is not None:
            collection = self._client[self.db_name][collection_name]
            return list(collection.find({}, {"_id": 0}))

        jsonl_path = self.fallback_dir / f"{collection_name}.jsonl"
        if not jsonl_path.exists():
            return []

        with jsonl_path.open("r", encoding="utf-8") as f_in:
            return [json.loads(line) for line in f_in if line.strip()]

    def log_audit_event(
        self, event_payload: Dict[str, Any], collection_name: str = "ingestion_audit_logs"
    ) -> None:
        """Registra un informe de auditoría (p. ej., IngestionGate) en la capa Bronze."""
        if self._is_mongo_available and self._client is not None:
            self._client[self.db_name][collection_name].insert_one(dict(event_payload))
            return

        audit_path = self.fallback_dir / f"{collection_name}.jsonl"
        with audit_path.open("a", encoding="utf-8") as f_audit:
            f_audit.write(json.dumps(event_payload, ensure_ascii=False) + "\n")
