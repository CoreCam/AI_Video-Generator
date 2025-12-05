"""
Database operations for the Sora Core platform.
Clean extraction focusing on core data management.
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import uuid

class DatabaseClient:
    """Database client for managing personas, jobs, and application data."""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "postgresql://localhost/sora_core"
        self.connection = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection."""
        try:
            import psycopg2
            self.connection = psycopg2.connect(self.connection_string)
            print(f"✅ Database connection established")
        except ImportError:
            print("⚠️ psycopg2 not installed - using mock database")
            self.connection = None
        except Exception as e:
            print(f"⚠️ Database connection failed: {e} - using mock database")
            self.connection = None
    
    async def create_persona(self, persona_data: Dict[str, Any]) -> str:
        """
        Create a new persona in the database.
        
        Args:
            persona_data: Persona information dictionary
            
        Returns:
            Created persona ID
        """
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO personas (id, name, description, consent_status, created_at, metadata)
                    VALUES (%(id)s, %(name)s, %(description)s, %(consent_status)s, %(created_at)s, %(metadata)s)
                """, {
                    "id": persona_data["id"],
                    "name": persona_data["name"],
                    "description": persona_data.get("description", ""),
                    "consent_status": persona_data.get("consent_status", "pending"),
                    "created_at": persona_data.get("created_at", datetime.utcnow()),
                    "metadata": json.dumps(persona_data.get("metadata", {}))
                })
                self.connection.commit()
                cursor.close()
            else:
                # Mock database operation
                print(f"Mock: Created persona {persona_data['id']}")
            
            print(f"✅ Created persona {persona_data['id']}")
            return persona_data["id"]
            
        except Exception as e:
            print(f"❌ Error creating persona: {e}")
            raise
    
    async def get_persona(self, persona_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a persona by ID.
        
        Args:
            persona_id: ID of the persona to retrieve
            
        Returns:
            Persona data or None if not found
        """
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM personas WHERE id = %s", (persona_id,))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    return self._format_persona_result(result)
            else:
                # Mock database operation
                return self._generate_mock_persona(persona_id)
            
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving persona {persona_id}: {e}")
            return None
    
    async def list_personas(
        self,
        limit: int = 50,
        offset: int = 0,
        consent_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List personas with optional filtering.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            consent_status: Filter by consent status
            
        Returns:
            List of persona dictionaries
        """
        try:
            if self.connection:
                cursor = self.connection.cursor()
                query = """
                    SELECT * FROM personas 
                    WHERE ($3 IS NULL OR consent_status = $3)
                    ORDER BY created_at DESC
                    LIMIT $1 OFFSET $2
                """
                cursor.execute(query, (limit, offset, consent_status))
                results = cursor.fetchall()
                cursor.close()
                
                return [self._format_persona_result(result) for result in results]
            else:
                # Mock database operation
                return [self._generate_mock_persona(f"persona_{i}") for i in range(min(limit, 3))]
            
        except Exception as e:
            print(f"❌ Error listing personas: {e}")
            return []
    
    async def update_persona(
        self,
        persona_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a persona.
        
        Args:
            persona_id: ID of the persona to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful
        """
        try:
            if self.connection:
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key == "metadata":
                        set_clauses.append(f"{key} = %s")
                        values.append(json.dumps(value))
                    else:
                        set_clauses.append(f"{key} = %s")
                        values.append(value)
                
                values.append(persona_id)
                
                cursor = self.connection.cursor()
                query = f"UPDATE personas SET {', '.join(set_clauses)} WHERE id = %s"
                cursor.execute(query, values)
                self.connection.commit()
                cursor.close()
            else:
                # Mock database operation
                print(f"Mock: Updated persona {persona_id} with {updates}")
            
            print(f"✅ Updated persona {persona_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating persona {persona_id}: {e}")
            return False
    
    async def delete_persona(self, persona_id: str) -> bool:
        """Delete a persona."""
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM personas WHERE id = %s", (persona_id,))
                self.connection.commit()
                cursor.close()
            else:
                # Mock database operation
                print(f"Mock: Deleted persona {persona_id}")
            
            print(f"✅ Deleted persona {persona_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting persona {persona_id}: {e}")
            return False
    
    async def create_generation_job(self, job_data: Dict[str, Any]) -> str:
        """Create a new generation job."""
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO generation_jobs (id, type, persona_ids, prompt, parameters, status, created_at)
                    VALUES (%(id)s, %(type)s, %(persona_ids)s, %(prompt)s, %(parameters)s, %(status)s, %(created_at)s)
                """, {
                    "id": job_data["id"],
                    "type": job_data["type"],
                    "persona_ids": json.dumps(job_data["persona_ids"]),
                    "prompt": job_data["prompt"],
                    "parameters": json.dumps(job_data["parameters"]),
                    "status": job_data["status"],
                    "created_at": job_data["created_at"]
                })
                self.connection.commit()
                cursor.close()
            else:
                # Mock database operation
                print(f"Mock: Created generation job {job_data['id']}")
            
            print(f"✅ Created generation job {job_data['id']}")
            return job_data["id"]
            
        except Exception as e:
            print(f"❌ Error creating generation job: {e}")
            raise
    
    async def get_generation_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a generation job by ID."""
        try:
            if self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM generation_jobs WHERE id = %s", (job_id,))
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    return self._format_job_result(result)
            else:
                # Mock database operation
                return self._generate_mock_job(job_id)
            
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving job {job_id}: {e}")
            return None
    
    async def update_generation_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """Update a generation job."""
        try:
            if self.connection:
                # Build dynamic update query
                set_clauses = []
                values = []
                
                for key, value in updates.items():
                    if key in ["persona_ids", "parameters"]:
                        set_clauses.append(f"{key} = %s")
                        values.append(json.dumps(value))
                    else:
                        set_clauses.append(f"{key} = %s")
                        values.append(value)
                
                values.append(job_id)
                
                cursor = self.connection.cursor()
                query = f"UPDATE generation_jobs SET {', '.join(set_clauses)} WHERE id = %s"
                cursor.execute(query, values)
                self.connection.commit()
                cursor.close()
            else:
                # Mock database operation
                print(f"Mock: Updated job {job_id} with {updates}")
            
            print(f"✅ Updated job {job_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating job {job_id}: {e}")
            return False
    
    def _format_persona_result(self, result: tuple) -> Dict[str, Any]:
        """Format database result into persona dictionary."""
        # Assuming columns: id, name, description, consent_status, created_at, metadata
        return {
            "id": result[0],
            "name": result[1],
            "description": result[2],
            "consent_status": result[3],
            "created_at": result[4].isoformat() if result[4] else None,
            "metadata": json.loads(result[5]) if result[5] else {}
        }
    
    def _format_job_result(self, result: tuple) -> Dict[str, Any]:
        """Format database result into job dictionary."""
        # Assuming columns: id, type, persona_ids, prompt, parameters, status, created_at
        return {
            "id": result[0],
            "type": result[1],
            "persona_ids": json.loads(result[2]) if result[2] else [],
            "prompt": result[3],
            "parameters": json.loads(result[4]) if result[4] else {},
            "status": result[5],
            "created_at": result[6].isoformat() if result[6] else None
        }
    
    def _generate_mock_persona(self, persona_id: str) -> Dict[str, Any]:
        """Generate mock persona data."""
        return {
            "id": persona_id,
            "name": f"Mock Persona {persona_id}",
            "description": "A mock persona for testing",
            "consent_status": "approved",
            "created_at": datetime.utcnow().isoformat(),
            "metadata": {
                "files": [],
                "embeddings_generated": True
            }
        }
    
    def _generate_mock_job(self, job_id: str) -> Dict[str, Any]:
        """Generate mock job data."""
        return {
            "id": job_id,
            "type": "video",
            "persona_ids": ["persona_1"],
            "prompt": "Generate a sample video",
            "parameters": {"quality": "hd", "duration": 30},
            "status": "completed",
            "created_at": datetime.utcnow().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get database client status."""
        return {
            "connection_string": self.connection_string,
            "connected": self.connection is not None,
            "using_mock": self.connection is None
        }