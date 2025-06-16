-- ====================================================================
-- SCRIPT DE INICIALIZACIÓN DE BASE DE DATOS - DASHBOARD MODULAR
-- ====================================================================
-- 
-- Archivo: app.sql
-- Descripción: Estructura básica de la base de datos
-- Versión: 1.0.0
-- Fecha: 2025-06-16
-- Base de datos: MySQL 5.7+
-- Usuario de aplicación: alex (solo lectura/escritura)
--
-- INSTRUCCIONES DE USO:
-- mysql -u root -p test < app.sql
--
-- ====================================================================

-- Seleccionar la base de datos
USE test;

-- Establecer charset
SET NAMES utf8mb4;

-- ====================================================================
-- TABLA: json_data
-- ====================================================================
-- Propósito: Almacenar configuraciones JSON del sistema
-- Usado por: JsonEditorModule
-- ====================================================================

DROP TABLE IF EXISTS json_data;

CREATE TABLE json_data (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID único del registro JSON',
    name VARCHAR(255) NOT NULL COMMENT 'Nombre del archivo JSON',
    content LONGTEXT NOT NULL COMMENT 'Contenido JSON como texto',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de actualización',
    
    INDEX idx_name (name)
) ENGINE=InnoDB 
  DEFAULT CHARSET=utf8mb4 
  COLLATE=utf8mb4_unicode_ci 
  COMMENT='Configuraciones JSON del dashboard';

-- ====================================================================
-- DATOS INICIALES
-- ====================================================================

-- Insertar configuración JSON por defecto para el editor
INSERT INTO json_data (id, name, content) VALUES (
    1,
    'configuracion_principal',
    '{"mensaje":"¡Bienvenido al editor JSON!","fecha":"2025-06-16T12:00:00.000Z","configuracion":{"tema":"oscuro","autoguardado":false,"version":"1.0.0"}}'
);

-- ====================================================================
-- VERIFICACIÓN
-- ====================================================================

-- Mostrar tabla creada
SELECT 
    'json_data' as Tabla,
    COUNT(*) as Registros
FROM json_data;

SELECT '✅ Estructura básica creada correctamente' as Estado;