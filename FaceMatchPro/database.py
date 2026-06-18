"""
FaceMatch Pro - Database Module
MongoDB integration for storing verification history
"""

import datetime
from typing import Optional, List, Dict, Any

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

_memory_store: List[Dict[str, Any]] = []
_next_id = 1


class DatabaseManager:
    """Manages all MongoDB operations with in-memory fallback."""

    def __init__(self, host="localhost", port=27017, db_name="face_verification"):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        self.use_memory = False
        self._connect()

    def _connect(self):
        if not MONGO_AVAILABLE:
            self.use_memory = True
            self.connected = True
            return
        try:
            self.client = MongoClient(self.host, self.port, serverSelectionTimeoutMS=3000)
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            self.collection = self.db["verification_history"]
            self.collection.create_index("timestamp")
            self.collection.create_index("match_status")
            self.connected = True
            self.use_memory = False
        except Exception:
            self.connected = True
            self.use_memory = True

    def get_status(self):
        if not self.connected:
            return "Disconnected"
        if self.use_memory:
            return "In-Memory (MongoDB N/A)"
        return "Connected"

    def save_result(self, image1_name, image2_name, similarity_score,
                    match_status, processing_time, extra=None):
        global _next_id
        record = {
            "image1_name": image1_name,
            "image2_name": image2_name,
            "similarity_score": round(similarity_score, 4),
            "match_status": match_status,
            "processing_time": round(processing_time, 4),
            "timestamp": datetime.datetime.now(),
            **(extra or {}),
        }
        if self.use_memory:
            record["_id"] = str(_next_id)
            _next_id += 1
            _memory_store.append(record)
            return record["_id"]
        try:
            result = self.collection.insert_one(record)
            return str(result.inserted_id)
        except Exception:
            return None

    def fetch_history(self, limit=500, search=None, status_filter=None):
        if self.use_memory:
            results = list(_memory_store)
            if search:
                s = search.lower()
                results = [r for r in results if
                           s in r.get("image1_name","").lower() or
                           s in r.get("image2_name","").lower()]
            if status_filter and status_filter != "All":
                results = [r for r in results if r.get("match_status") == status_filter]
            results.sort(key=lambda x: x["timestamp"], reverse=True)
            return results[:limit]
        try:
            query = {}
            if search:
                query["$or"] = [
                    {"image1_name": {"$regex": search, "$options": "i"}},
                    {"image2_name": {"$regex": search, "$options": "i"}},
                ]
            if status_filter and status_filter != "All":
                query["match_status"] = status_filter
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)
            return results
        except Exception:
            return []

    def delete_record(self, record_id):
        global _memory_store
        if self.use_memory:
            before = len(_memory_store)
            _memory_store = [r for r in _memory_store if r["_id"] != record_id]
            return len(_memory_store) < before
        try:
            from bson import ObjectId
            result = self.collection.delete_one({"_id": ObjectId(record_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    def get_analytics(self):
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if self.use_memory:
            total = len(_memory_store)
            matches = sum(1 for r in _memory_store if r.get("match_status") == "Match")
            scores = [r["similarity_score"] for r in _memory_store if "similarity_score" in r]
            avg_score = round(sum(scores)/len(scores), 2) if scores else 0.0
            today_count = sum(1 for r in _memory_store
                              if r.get("timestamp", datetime.datetime.min) >= today)
            daily = {}
            for r in _memory_store:
                ts = r.get("timestamp")
                if ts:
                    day = ts.strftime("%Y-%m-%d")
                    daily[day] = daily.get(day, 0) + 1
            return {"total": total, "matches": matches, "no_matches": total-matches,
                    "avg_similarity": avg_score, "today": today_count, "daily_trend": daily}
        try:
            pipeline = [{"$group": {"_id": None, "total": {"$sum": 1},
                "matches": {"$sum": {"$cond": [{"$eq": ["$match_status","Match"]},1,0]}},
                "avg_similarity": {"$avg": "$similarity_score"}}}]
            agg = list(self.collection.aggregate(pipeline))
            stats = agg[0] if agg else {"total":0,"matches":0,"avg_similarity":0}
            today_count = self.collection.count_documents({"timestamp": {"$gte": today}})
            trend_pipeline = [
                {"$match": {"timestamp": {"$gte": datetime.datetime.now()-datetime.timedelta(days=30)}}},
                {"$group": {"_id": {"$dateToString": {"format":"%Y-%m-%d","date":"$timestamp"}},
                            "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}]
            daily = {d["_id"]: d["count"] for d in self.collection.aggregate(trend_pipeline)}
            total = stats.get("total", 0)
            matches = stats.get("matches", 0)
            return {"total": total, "matches": matches, "no_matches": total-matches,
                    "avg_similarity": round(stats.get("avg_similarity") or 0, 2),
                    "today": today_count, "daily_trend": daily}
        except Exception:
            return {"total":0,"matches":0,"no_matches":0,"avg_similarity":0,"today":0,"daily_trend":{}}


_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance

def connect_database(host="localhost", port=27017):
    global _db_instance
    _db_instance = DatabaseManager(host=host, port=port)
    return _db_instance

def save_result(*args, **kwargs):
    return get_db().save_result(*args, **kwargs)

def fetch_history(*args, **kwargs):
    return get_db().fetch_history(*args, **kwargs)

def delete_record(record_id):
    return get_db().delete_record(record_id)
