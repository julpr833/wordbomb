-- ============================================================================
--  _    _  _______________________  ________  _________ 
-- | |  | ||  _  | ___ \  _  \ ___ \|  _  |  \/  || ___ \
-- | |  | || | | | |_/ / | | | |_/ /| | | | .  . || |_/ /
-- | |/\| || | | |    /| | | | ___ \| | | | |\/| || ___ \
-- \  /\  /\ \_/ / |\ \| |/ /| |_/ /\ \_/ / |  | || |_/ /
--  \/  \/  \___/\_| \_|___/ \____/  \___/\_|  |_/\____/                                                 
-- ============================================================================
-- Description: Complete database structure for managing users, games,
--              words, roles, and administrative actions
-- ============================================================================

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- ============================================================================
-- SCHEMA CREATION
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS `wordbomb` DEFAULT CHARACTER SET utf8;
USE `wordbomb`;

-- ============================================================================
-- TABLE: USUARIO (Users)
-- Description: Stores user account information including credentials,
--              profile data, and account status
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`USUARIO` (
  `ID_Usuario` INT NOT NULL AUTO_INCREMENT,
  `Username` VARCHAR(45) NOT NULL,
  `Correo` VARCHAR(100) NOT NULL,
  `Password` VARCHAR(255) NOT NULL,
  `Avatar_URL` VARCHAR(255) NULL,
  `FechaRegistro` DATE NOT NULL,
  `PuntosTotales` INT NOT NULL DEFAULT 0,
  `Vetado` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID_Usuario`),
  UNIQUE INDEX `Correo_UNIQUE` (`Correo` ASC) VISIBLE,
  UNIQUE INDEX `Username_UNIQUE` (`Username` ASC) VISIBLE
) ENGINE = InnoDB;

-- ============================================================================
-- TABLE: PARTIDA (Game Matches)
-- Description: Stores game session data including start/end times,
--              statistics, and winner information
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`PARTIDA` (
  `ID_Partida` INT NOT NULL AUTO_INCREMENT,
  `FechaInicio` DATETIME NOT NULL,
  `FechaFinalizacion` DATETIME NULL,
  `TotalPalabras` INT NOT NULL,
  `TotalTurnos` INT NULL,
  `Ganador_ID` INT NOT NULL,
  `Creador_ID` INT NOT NULL,
  PRIMARY KEY (`ID_Partida`),
  INDEX `fk_PARTIDA_USUARIO1_idx` (`Ganador_ID` ASC) VISIBLE,
  INDEX `fk_PARTIDA_USUARIO2_idx` (`Creador_ID` ASC) VISIBLE,
  CONSTRAINT `fk_PARTIDA_USUARIO1`
    FOREIGN KEY (`Ganador_ID`)
    REFERENCES `wordbomb`.`USUARIO` (`ID_Usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_PARTIDA_USUARIO2`
    FOREIGN KEY (`Creador_ID`)
    REFERENCES `wordbomb`.`USUARIO` (`ID_Usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- ============================================================================
-- TABLE: PALABRA (Words)
-- Description: Dictionary of valid words that can be used in games
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`PALABRA` (
  `ID_Palabra` INT NOT NULL AUTO_INCREMENT,
  `Palabra` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ID_Palabra`)
) ENGINE = InnoDB;

-- ============================================================================
-- TABLE: ROL (Roles)
-- Description: User role definitions for permission management
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`ROL` (
  `ID_Rol` INT NOT NULL AUTO_INCREMENT,
  `NombreRol` VARCHAR(25) NOT NULL,
  PRIMARY KEY (`ID_Rol`)
) ENGINE = InnoDB;

-- Setup default values
INSERT INTO `wordbomb`.`ROL` VALUES (1, "Usuario"), (2, "Administrador");

-- ============================================================================
-- TABLE: USUARIO_ROL (User-Role Assignment)
-- Description: Many-to-many relationship between users and roles
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`USUARIO_ROL` (
  `Usuario_ID` INT NOT NULL,
  `Rol_ID` INT NOT NULL,
  PRIMARY KEY (`Usuario_ID`, `Rol_ID`),
  INDEX `fk_USUARIO_has_ROL_ROL1_idx` (`Rol_ID` ASC) VISIBLE,
  INDEX `fk_USUARIO_has_ROL_USUARIO_idx` (`Usuario_ID` ASC) VISIBLE,
  CONSTRAINT `fk_USUARIO_has_ROL_USUARIO`
    FOREIGN KEY (`Usuario_ID`)
    REFERENCES `wordbomb`.`USUARIO` (`ID_Usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_USUARIO_has_ROL_ROL1`
    FOREIGN KEY (`Rol_ID`)
    REFERENCES `wordbomb`.`ROL` (`ID_Rol`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- ============================================================================
-- TABLE: PALABRAS_PARTIDA (Game Words)
-- Description: Tracks words played during each game match, including
--              which user played them and on which turn
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`PALABRAS_PARTIDA` (
  `Partida_ID` INT NOT NULL,
  `Palabra_ID` INT NOT NULL,
  `Usuario_ID` INT NOT NULL,
  `Turno` INT NOT NULL,
  PRIMARY KEY (`Partida_ID`, `Palabra_ID`),
  INDEX `fk_PARTIDA_has_PALABRA_PALABRA1_idx` (`Palabra_ID` ASC) VISIBLE,
  INDEX `fk_PARTIDA_has_PALABRA_PARTIDA1_idx` (`Partida_ID` ASC) VISIBLE,
  INDEX `fk_PALABRAS_PARTIDA_USUARIO1_idx` (`Usuario_ID` ASC) VISIBLE,
  CONSTRAINT `fk_PARTIDA_has_PALABRA_PARTIDA1`
    FOREIGN KEY (`Partida_ID`)
    REFERENCES `wordbomb`.`PARTIDA` (`ID_Partida`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_PARTIDA_has_PALABRA_PALABRA1`
    FOREIGN KEY (`Palabra_ID`)
    REFERENCES `wordbomb`.`PALABRA` (`ID_Palabra`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_PALABRAS_PARTIDA_USUARIO1`
    FOREIGN KEY (`Usuario_ID`)
    REFERENCES `wordbomb`.`USUARIO` (`ID_Usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- ============================================================================
-- TABLE: PARTIDA_PARTICIPANTE (Game Participants)
-- Description: Many-to-many relationship tracking which users participated
--              in which game matches
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`PARTIDA_PARTICIPANTE` (
  `Usuario_ID` INT NOT NULL,
  `Partida_ID` INT NOT NULL,
  PRIMARY KEY (`Usuario_ID`, `Partida_ID`),
  INDEX `fk_USUARIO_has_PARTIDA_PARTIDA1_idx` (`Partida_ID` ASC) VISIBLE,
  INDEX `fk_USUARIO_has_PARTIDA_USUARIO1_idx` (`Usuario_ID` ASC) VISIBLE,
  CONSTRAINT `fk_USUARIO_has_PARTIDA_USUARIO1`
    FOREIGN KEY (`Usuario_ID`)
    REFERENCES `wordbomb`.`USUARIO` (`ID_Usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_USUARIO_has_PARTIDA_PARTIDA1`
    FOREIGN KEY (`Partida_ID`)
    REFERENCES `wordbomb`.`PARTIDA` (`ID_Partida`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- ============================================================================
-- TABLE: ACCION_ADMINISTRATIVA (Administrative Actions)
-- Description: Catalog of possible administrative actions for audit logging
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`ACCION_ADMINISTRATIVA` (
  `ID_Accion` INT NOT NULL AUTO_INCREMENT,
  `NombreAccion` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ID_Accion`)
) ENGINE = InnoDB;

-- ============================================================================
-- TABLE: REGISTRO_AUDITORIA (Audit Log)
-- Description: Tracks administrative actions performed by administrators
--              for security and compliance purposes
-- ============================================================================

CREATE TABLE IF NOT EXISTS `wordbomb`.`REGISTRO_AUDITORIA` (
  `ID_Registro` INT NOT NULL AUTO_INCREMENT,
  `Administrador_ID` INT NOT NULL,
  `Accion_ID` INT NOT NULL,
  `FechaRegistro` DATETIME NOT NULL,
  PRIMARY KEY (`ID_Registro`),
  INDEX `fk_REGISTRO_AUDITORIA_USUARIO1_idx` (`Administrador_ID` ASC) VISIBLE,
  INDEX `fk_REGISTRO_AUDITORIA_ACCION_ADMINISTRATIVA1_idx` (`Accion_ID` ASC) VISIBLE,
  CONSTRAINT `fk_REGISTRO_AUDITORIA_USUARIO1`
    FOREIGN KEY (`Administrador_ID`)
    REFERENCES `wordbomb`.`USUARIO` (`ID_Usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_REGISTRO_AUDITORIA_ACCION_ADMINISTRATIVA1`
    FOREIGN KEY (`Accion_ID`)
    REFERENCES `wordbomb`.`ACCION_ADMINISTRATIVA` (`ID_Accion`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- ============================================================================
-- Restore original settings
-- ============================================================================

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================