# modules/job_scheduler_module.py
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import asyncio
import threading
from croniter import croniter
from .base_module import BaseModule, ModuleConfig
from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from pydantic import BaseModel

# Importar jobs
from .jobs.base_job import BaseJob
from .jobs.backup_job import BackupJob



class JobConfig(BaseModel):
    job_id: str
    config_json: str
    schedule_type: str = "manual"
    schedule_value: Optional[str] = None
    is_active: bool = True

class JobExecuteRequest(BaseModel):
    job_id: str
    config_json: Optional[str] = None

class JobSchedulerModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.jobs_registry: Dict[str, BaseJob] = {}
        self.scheduler_thread = None
        self.scheduler_running = False
        self._discover_jobs()
        self._start_scheduler()
    
    def get_config(self) -> ModuleConfig:
        return ModuleConfig(
            id="job-scheduler",
            name="Job Scheduler",
            icon="fas fa-clock",
            color="linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
            endpoint="/api/job-scheduler",
            description="Gestión y programación de scripts automáticos",
            size="large"
        )
    
    def get_data(self) -> Dict[str, Any]:
        """Retorna información general del módulo"""
        return {
            "total_jobs": len(self.jobs_registry),
            "available_jobs": [job.to_dict() for job in self.jobs_registry.values()],
            "scheduler_status": "running" if self.scheduler_running else "stopped"
        }
    
    def _discover_jobs(self):
        """Descubre y registra todos los jobs disponibles"""
        # Registrar jobs manualmente
        self.register_job(BackupJob())
        # Añadir aquí más jobs según se creen
    
    def register_job(self, job: BaseJob):
        """Registra un job en el sistema"""
        self.jobs_registry[job.job_id] = job
        print(f"✅ Job registrado: {job.name} ({job.job_id})")
    
    def _start_scheduler(self):
        """Inicia el scheduler en un thread separado"""
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            print("🕐 Scheduler iniciado")
    
    def _scheduler_loop(self):
        """Loop principal del scheduler"""
        while self.scheduler_running:
            try:
                asyncio.run(self._check_and_run_jobs())
            except Exception as e:
                print(f"❌ Error en scheduler: {e}")
            
            # Esperar 60 segundos antes de la siguiente verificación
            threading.Event().wait(60)
    
    async def _check_and_run_jobs(self):
        """Verifica y ejecuta jobs programados"""
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            # Buscar jobs que necesitan ejecutarse
            now = datetime.now()
            query = text("""
                SELECT job_id, config_json 
                FROM scheduled_jobs 
                WHERE is_active = TRUE 
                AND schedule_type != 'manual'
                AND (next_run IS NULL OR next_run <= :now)
                AND (last_status != 'running' OR last_status IS NULL)
            """)
            
            result = db.execute(query, {"now": now})
            jobs_to_run = result.fetchall()
            
            for job_row in jobs_to_run:
                job_id = job_row[0]
                config_json = job_row[1]
                
                if job_id in self.jobs_registry:
                    print(f"🚀 Ejecutando job programado: {job_id}")
                    asyncio.create_task(self._execute_job_async(job_id, config_json, db))
                    self._update_next_run(job_id, db)
        
        except Exception as e:
            print(f"❌ Error verificando jobs: {e}")
        finally:
            db.close()
    
    def _update_next_run(self, job_id: str, db: Session):
        """Actualiza la próxima ejecución de un job"""
        job_data = db.execute(
            text("SELECT schedule_type, schedule_value FROM scheduled_jobs WHERE job_id = :job_id"),
            {"job_id": job_id}
        ).fetchone()
        
        if not job_data:
            return
        
        schedule_type, schedule_value = job_data
        next_run = None
        now = datetime.now()
        
        if schedule_type == "interval" and schedule_value:
            minutes = int(schedule_value)
            next_run = now + timedelta(minutes=minutes)
        elif schedule_type == "cron" and schedule_value:
            cron = croniter(schedule_value, now)
            next_run = cron.get_next(datetime)
        elif schedule_type == "daily":
            next_run = now + timedelta(days=1)
        elif schedule_type == "weekly":
            next_run = now + timedelta(weeks=1)
        
        if next_run:
            db.execute(
                text("UPDATE scheduled_jobs SET next_run = :next_run WHERE job_id = :job_id"),
                {"next_run": next_run, "job_id": job_id}
            )
            db.commit()
    
    async def _execute_job_async(self, job_id: str, config_json: str, db: Session):
        """Ejecuta un job de forma asíncrona"""
        job = self.jobs_registry.get(job_id)
        if not job:
            return
        
        # Marcar como running
        db.execute(
            text("UPDATE scheduled_jobs SET last_status = 'running' WHERE job_id = :job_id"),
            {"job_id": job_id}
        )
        db.commit()
        
        # Ejecutar job
        result = await asyncio.to_thread(job.run, config_json or "{}", db)
        
        # Guardar resultado (solo el último)
        status = result.get("status", "failed")
        output_summary = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": result.get("duration_seconds", 0)
        }
        
        # Si hay output específico, incluir solo un resumen
        if "output" in result:
            output_summary["summary"] = str(result["output"])[:500]  # Limitar a 500 caracteres
        if "error" in result:
            output_summary["error"] = result["error"]
        
        db.execute(
            text("""
                UPDATE scheduled_jobs 
                SET last_run = :last_run, 
                    last_status = :status,
                    last_output = :output
                WHERE job_id = :job_id
            """),
            {
                "last_run": datetime.now(),
                "status": status,
                "output": json.dumps(output_summary),
                "job_id": job_id
            }
        )
        db.commit()
    
    def setup_routes(self):
        """Configura las rutas del módulo"""
        super().setup_routes()
        
        # Listar todos los jobs disponibles
        @self.router.get(f"{self.config.endpoint}/jobs")
        async def list_jobs():
            return [job.to_dict() for job in self.jobs_registry.values()]
        
        # Obtener configuración de un job
        @self.router.get(f"{self.config.endpoint}/jobs/{{job_id}}")
        async def get_job_config(job_id: str, db: Session = Depends(get_db)):
            result = db.execute(
                text("SELECT * FROM scheduled_jobs WHERE job_id = :job_id"),
                {"job_id": job_id}
            ).fetchone()
            
            if result:
                return {
                    "job_id": result[1],
                    "job_name": result[2],
                    "description": result[3],
                    "config_json": result[4],
                    "schedule_type": result[5],
                    "schedule_value": result[6],
                    "is_active": result[7],
                    "last_run": result[8],
                    "next_run": result[9],
                    "last_status": result[10],
                    "last_output": result[11]
                }
            
            # Si no existe, retornar configuración por defecto
            job = self.jobs_registry.get(job_id)
            if job:
                return {
                    "job_id": job.job_id,
                    "job_name": job.name,
                    "description": job.description,
                    "config_json": json.dumps(job.default_config),
                    "schedule_type": "manual",
                    "is_active": True
                }
            
            raise HTTPException(status_code=404, detail="Job no encontrado")
        
        # Guardar configuración de un job
        @self.router.post(f"{self.config.endpoint}/jobs/{{job_id}}/config")
        async def save_job_config(job_id: str, config: JobConfig, db: Session = Depends(get_db)):
            job = self.jobs_registry.get(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job no encontrado")
            
            # Validar configuración
            try:
                config_dict = json.loads(config.config_json)
                is_valid, error = job.validate_config(config_dict)
                if not is_valid:
                    raise HTTPException(status_code=400, detail=error)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="JSON inválido")
            
            # Buscar si existe
            existing = db.execute(
                text("SELECT id FROM scheduled_jobs WHERE job_id = :job_id"),
                {"job_id": job_id}
            ).fetchone()
            
            if existing:
                # Actualizar
                db.execute(
                    text("""
                        UPDATE scheduled_jobs 
                        SET config_json = :config_json,
                            schedule_type = :schedule_type,
                            schedule_value = :schedule_value,
                            is_active = :is_active,
                            updated_at = :updated_at
                        WHERE job_id = :job_id
                    """),
                    {
                        "job_id": job_id,
                        "config_json": config.config_json,
                        "schedule_type": config.schedule_type,
                        "schedule_value": config.schedule_value,
                        "is_active": config.is_active,
                        "updated_at": datetime.now()
                    }
                )
            else:
                # Insertar nuevo
                db.execute(
                    text("""
                        INSERT INTO scheduled_jobs 
                        (job_id, job_name, description, config_json, schedule_type, schedule_value, is_active)
                        VALUES (:job_id, :job_name, :description, :config_json, :schedule_type, :schedule_value, :is_active)
                    """),
                    {
                        "job_id": job_id,
                        "job_name": job.name,
                        "description": job.description,
                        "config_json": config.config_json,
                        "schedule_type": config.schedule_type,
                        "schedule_value": config.schedule_value,
                        "is_active": config.is_active
                    }
                )
            
            db.commit()
            
            # Actualizar next_run si es necesario
            if config.schedule_type != "manual":
                self._update_next_run(job_id, db)
            
            return {"status": "success", "message": "Configuración guardada"}
        
        # Ejecutar job manualmente
        @self.router.post(f"{self.config.endpoint}/jobs/{{job_id}}/execute")
        async def execute_job(
            job_id: str, 
            request: JobExecuteRequest,
            background_tasks: BackgroundTasks,
            db: Session = Depends(get_db)
        ):
            job = self.jobs_registry.get(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job no encontrado")
            
            # Usar configuración guardada si no se proporciona
            config_json = request.config_json
            if not config_json:
                result = db.execute(
                    text("SELECT config_json FROM scheduled_jobs WHERE job_id = :job_id"),
                    {"job_id": job_id}
                ).fetchone()
                config_json = result[0] if result else "{}"
            
            # Ejecutar en background
            background_tasks.add_task(self._execute_job_async, job_id, config_json, db)
            
            return {"status": "started", "message": f"Job {job_id} iniciado"}
        
        # Obtener jobs programados activos
        @self.router.get(f"{self.config.endpoint}/scheduled")
        async def get_scheduled_jobs(db: Session = Depends(get_db)):
            results = db.execute(
                text("""
                    SELECT job_id, job_name, schedule_type, schedule_value, 
                           is_active, last_run, next_run, last_status
                    FROM scheduled_jobs
                    WHERE is_active = TRUE
                    ORDER BY 
                        CASE WHEN next_run IS NULL THEN 1 ELSE 0 END,
                        next_run ASC
                """)
            ).fetchall()
            
            return [
                {
                    "job_id": r[0],
                    "job_name": r[1],
                    "schedule_type": r[2],
                    "schedule_value": r[3],
                    "is_active": r[4],
                    "last_run": r[5],
                    "next_run": r[6],
                    "last_status": r[7]
                }
                for r in results
            ]