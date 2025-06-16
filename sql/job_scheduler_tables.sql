-- ====================================================================
-- TABLAS PARA EL MÓDULO JOB SCHEDULER (VERSIÓN LIGERA)
-- ====================================================================
-- 
-- Archivo: sql/job_scheduler_tables.sql
-- Descripción: Estructura de base de datos para el módulo Job Scheduler
-- Base de datos: MySQL 5.7+
--
-- INSTRUCCIONES DE USO:
-- mysql -u root -p test < sql/job_scheduler_tables.sql
--
-- ====================================================================

USE test;
SET NAMES utf8mb4;

-- ====================================================================
-- TABLA: scheduled_jobs (simplificada, sin logs)
-- ====================================================================

DROP TABLE IF EXISTS scheduled_jobs;

CREATE TABLE scheduled_jobs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID único del registro',
    job_id VARCHAR(100) NOT NULL UNIQUE COMMENT 'ID único del job (snake_case)',
    job_name VARCHAR(255) NOT NULL COMMENT 'Nombre legible del job',
    description TEXT COMMENT 'Descripción del job',
    config_json LONGTEXT COMMENT 'Configuración JSON específica del job',
    schedule_type ENUM('manual', 'interval', 'cron', 'daily', 'weekly') DEFAULT 'manual' COMMENT 'Tipo de programación',
    schedule_value VARCHAR(100) COMMENT 'Valor del cron o intervalo en minutos',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Si el job está activo',
    last_run DATETIME COMMENT 'Última vez que se ejecutó',
    next_run DATETIME COMMENT 'Próxima ejecución programada',
    last_status ENUM('success', 'failed', 'running', 'pending') COMMENT 'Estado de la última ejecución',
    last_output TEXT COMMENT 'Salida de la última ejecución (se sobrescribe)',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de actualización',
    
    INDEX idx_job_id (job_id),
    INDEX idx_next_run (next_run),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='Jobs programados del sistema';

-- ====================================================================
-- DATOS DE EJEMPLO
-- ====================================================================

INSERT INTO scheduled_jobs (
    job_id, 
    job_name, 
    description, 
    config_json,
    schedule_type,
    schedule_value,
    is_active
) VALUES (
    'example_job',
    'Job de Ejemplo',
    'Un job de demostración que procesa datos según la configuración',
    '{
        "mode": "test",
        "iterations": 5,
        "send_notification": false,
        "process_data": {
            "source": "database",
            "limit": 100
        }
    }',
    'manual',
    NULL,
    TRUE
);

-- ====================================================================
-- VERIFICACIÓN
-- ====================================================================

SELECT 
    'scheduled_jobs' as Tabla,
    COUNT(*) as Registros
FROM scheduled_jobs;

SELECT '✅ Tabla del Job Scheduler creada correctamente' as Estado;