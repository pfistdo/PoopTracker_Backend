create database poop_tracker;
USE poop_tracker;

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


-- -----------------------------------------------------
-- Table `cat`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `cat` ;

CREATE TABLE IF NOT EXISTS `cat` (
  `ID_cat` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `weight` FLOAT NOT NULL,
  `timestamp` TIMESTAMP(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`ID_cat`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `air_quality`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `air_quality` ;

CREATE TABLE IF NOT EXISTS `air_quality` (
  `ID_air_quality` INT NOT NULL AUTO_INCREMENT,
  `lpg` INT NOT NULL,
  `co` INT NOT NULL,
  `smoke` INT NOT NULL,
  `timestamp` TIMESTAMP(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`ID_air_quality`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `food`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `food` ;

CREATE TABLE IF NOT EXISTS `food` (
  `ID_food` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `meat` VARCHAR(45) NOT NULL,
  `protein` INT NOT NULL,
  `fat` INT NOT NULL,
  `ash` INT NOT NULL,
  `fibres` INT NOT NULL,
  `moisture` INT NOT NULL,
  `timestamp` TIMESTAMP(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`ID_food`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `feeding`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `feeding` ;

CREATE TABLE IF NOT EXISTS `feeding` (
  `ID_feeding` INT NOT NULL AUTO_INCREMENT,
  `timestamp` TIMESTAMP(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
  `food_ID` INT NOT NULL,
  `cat_ID` INT NOT NULL,
  PRIMARY KEY (`ID_feeding`, `food_ID`, `cat_ID`),
  INDEX `fk_feeding_food1_idx` (`food_ID` ASC) VISIBLE,
  INDEX `fk_feeding_cat2_idx` (`cat_ID` ASC) VISIBLE,
  CONSTRAINT `fk_feeding_food1`
    FOREIGN KEY (`food_ID`)
    REFERENCES `food` (`ID_food`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_feeding_cat2`
    FOREIGN KEY (`cat_ID`)
    REFERENCES `cat` (`ID_cat`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `telephone_number`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `telephone_number` ;

CREATE TABLE IF NOT EXISTS `telephone_number` (
  `ID_telephone_number` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `telnr` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ID_telephone_number`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `poop`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `poop` ;

CREATE TABLE IF NOT EXISTS `poop` (
  `ID_poop` INT NOT NULL AUTO_INCREMENT,
  `weight` INT NOT NULL,
  `timestamp` TIMESTAMP(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
  `feeding_ID` INT NOT NULL,
  PRIMARY KEY (`ID_poop`, `feeding_ID`),
  INDEX `fk_poop_feeding_idx` (`feeding_ID` ASC) VISIBLE,
  CONSTRAINT `fk_poop_feeding`
    FOREIGN KEY (`feeding_ID`)
    REFERENCES `feeding` (`ID_feeding`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 30
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;