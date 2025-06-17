# modules/job_scheduler_module.py
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import asyncio
import threading
import time
from croniter import croniter
from .base_module import BaseModule, ModuleConfig
from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from pydantic import BaseModel

# Importar jobs
from .jobs.base_job import BaseJob
from .jobs.test import TestJob
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
        self.register_job(TestJob())# Añadir aquí más jobs según se creen
    
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
        """Loop principal del scheduler - ejecuta cada 30 segundos"""
        while self.scheduler_running:
            try:
                # Usar run_in_executor para evitar bloqueos
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._check_and_run_jobs())
                loop.close()
            except Exception as e:
                print(f"❌ Error en scheduler loop: {e}")
            
            # Esperar 30 segundos antes de la siguiente verificación
            time.sleep(5)
    
    async def _check_and_run_jobs(self):
        """Verifica y ejecuta jobs programados"""
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            now = datetime.now()
            print(f"🔍 Verificando jobs programados a las {now.strftime('%H:%M:%S')}")
            
            # Buscar jobs que necesitan ejecutarse
            query = text("""
                SELECT job_id, config_json, schedule_type, schedule_value, last_run 
                FROM scheduled_jobs 
                WHERE is_active = TRUE 
                AND schedule_type != 'manual'
                AND (last_status != 'running' OR last_status IS NULL)
            """)
            
            result = db.execute(query)
            jobs_to_check = result.fetchall()
            
            for job_row in jobs_to_check:
                job_id = job_row[0]
                config_json = job_row[1]
                schedule_type = job_row[2]
                schedule_value = job_row[3]
                last_run = job_row[4]
                
                # Verificar si debe ejecutarse
                should_run = self._should_job_run(schedule_type, schedule_value, last_run, now)
                
                if should_run and job_id in self.jobs_registry:
                    print(f"🚀 Ejecutando job programado: {job_id}")
                    # Ejecutar en un thread separado para no bloquear
                    threading.Thread(
                        target=self._execute_job_sync,
                        args=(job_id, config_json),
                        daemon=True
                    ).start()
        
        except Exception as e:
            print(f"❌ Error verificando jobs: {e}")
        finally:
            db.close()
    
    def _should_job_run(self, schedule_type: str, schedule_value: str, last_run: datetime, now: datetime) -> bool:
        """Determina si un job debe ejecutarse basado en su programación"""
        if not last_run:
            # Si nunca se ha ejecutado, ejecutar ahora
            return True
        
        if schedule_type == "interval" and schedule_value:
            try:
                minutes = int(schedule_value)
                next_run = last_run + timedelta(minutes=minutes)
                return now >= next_run
            except:
                return False
                
        elif schedule_type == "cron" and schedule_value:
            try:
                # Usar last_run como base para calcular la próxima ejecución
                cron = croniter(schedule_value, last_run)
                next_run = cron.get_next(datetime)
                # Si la próxima ejecución calculada desde last_run es menor o igual a ahora, ejecutar
                return next_run <= now
            except:
                return False
                
        elif schedule_type == "daily":
            next_run = last_run + timedelta(days=1)
            return now >= next_run
            
        elif schedule_type == "weekly":
            next_run = last_run + timedelta(weeks=1)
            return now >= next_run
        
        return False
    
    def _execute_job_sync(self, job_id: str, config_json: str):
        """Ejecuta un job de forma síncrona"""
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            job = self.jobs_registry.get(job_id)
            if not job:
                print(f"❌ Job {job_id} no encontrado en el registro")
                return
            
            print(f"🔄 Iniciando ejecución de job: {job_id}")
            
            # Marcar como running
            db.execute(
                text("UPDATE scheduled_jobs SET last_status = 'running' WHERE job_id = :job_id"),
                {"job_id": job_id}
            )
            db.commit()
            
            # Ejecutar job - aquí es donde se ejecuta el código específico del job
            result = job.run(config_json or "{}", db)
            
            print(f"📊 Resultado de {job_id}: {result.get('status', 'unknown')}")
            
            # Guardar resultado
            status = result.get("status", "failed")
            output_summary = {
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": result.get("duration_seconds", 0)
            }
            
            # Incluir toda la salida del job
            if "output" in result:
                output_summary["summary"] = str(result["output"])[:500]
            if "error" in result:
                output_summary["error"] = result["error"]
            
            # Incluir otros campos del resultado
            for key, value in result.items():
                if key not in ["status", "started_at", "finished_at", "duration_seconds", "output", "error"]:
                    output_summary[key] = value
            
            # Actualizar con el resultado
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
            
            print(f"✅ Job {job_id} completado con estado: {status}")
            
        except Exception as e:
            print(f"❌ Error ejecutando job {job_id}: {e}")
            import traceback
            traceback.print_exc()
            
            # Marcar como failed
            try:
                db.execute(
                    text("""
                        UPDATE scheduled_jobs 
                        SET last_status = 'failed',
                            last_output = :output
                        WHERE job_id = :job_id
                    """),
                    {
                        "output": json.dumps({
                            "error": str(e), 
                            "timestamp": datetime.now().isoformat(),
                            "traceback": traceback.format_exc()
                        }),
                        "job_id": job_id
                    }
                )
                db.commit()
            except:
                pass
        finally:
            db.close()
    
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
            
            # Validar configuración JSON
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
            background_tasks.add_task(self._execute_job_sync, job_id, config_json)
            
            return {"status": "started", "message": f"Job {job_id} iniciado"}
        
        # Eliminar job de la base de datos
        @self.router.delete(f"{self.config.endpoint}/jobs/{{job_id}}")
        async def delete_job(job_id: str, db: Session = Depends(get_db)):
            result = db.execute(
                text("DELETE FROM scheduled_jobs WHERE job_id = :job_id"),
                {"job_id": job_id}
            )
            db.commit()
            
            if result.rowcount > 0:
                return {"status": "success", "message": f"Job {job_id} eliminado de la base de datos"}
            else:
                return {"status": "not_found", "message": f"Job {job_id} no encontrado en la base de datos"}
        
        # Obtener jobs programados activos
        @self.router.get(f"{self.config.endpoint}/scheduled")
        async def get_scheduled_jobs(db: Session = Depends(get_db)):
            results = db.execute(
                text("""
                    SELECT job_id, job_name, schedule_type, schedule_value, 
                           is_active, last_run, next_run, last_status
                    FROM scheduled_jobs
                    ORDER BY 
                        CASE WHEN is_active = TRUE THEN 0 ELSE 1 END,
                        last_run DESC
                """)
            ).fetchall()
            
            scheduled_jobs = []
            for r in results:
                job_data = {
                    "job_id": r[0],
                    "job_name": r[1],
                    "schedule_type": r[2],
                    "schedule_value": r[3],
                    "is_active": r[4],
                    "last_run": r[5],
                    "last_status": r[7]
                }
                
                # Calcular próxima ejecución basada en la última
                if r[4] and r[2] != 'manual' and r[5]:  # is_active y no manual y tiene last_run
                    next_run = self._calculate_next_run(r[2], r[3], r[5])
                    job_data["next_run"] = next_run
                else:
                    job_data["next_run"] = None
                
                scheduled_jobs.append(job_data)
            
            return scheduled_jobs
        
        # Obtener estado del scheduler
        @self.router.get(f"{self.config.endpoint}/scheduler/status")
        async def get_scheduler_status():
            return {
                "running": self.scheduler_running,
                "jobs_count": len(self.jobs_registry),
                "check_interval": "30 seconds"
            }
    
    def _calculate_next_run(self, schedule_type: str, schedule_value: str, last_run: datetime) -> Optional[datetime]:
        """Calcula la próxima ejecución basada en la última"""
        try:
            if schedule_type == "interval" and schedule_value:
                minutes = int(schedule_value)
                return last_run + timedelta(minutes=minutes)
            elif schedule_type == "cron" and schedule_value:
                cron = croniter(schedule_value, last_run)
                return cron.get_next(datetime)
            elif schedule_type == "daily":
                return last_run + timedelta(days=1)
            elif schedule_type == "weekly":
                return last_run + timedelta(weeks=1)
        except:
            pass
        return None