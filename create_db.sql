CREATE TABLE IF NOT EXISTS `poop_tracker`.`food` (
  `ID_food` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `meat` VARCHAR(45) NOT NULL,
  `protein` INT NULL DEFAULT NULL,
  `fat` INT NULL DEFAULT NULL,
  `ash` INT NULL DEFAULT NULL,
  `fibres` INT NULL DEFAULT NULL,
  `moisture` INT NULL DEFAULT NULL,
  `timestamp` TIMESTAMP(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
  PRIMARY KEY (`ID_food`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;
CREATE TABLE IF NOT EXISTS `poop_tracker`.`poop` (
  `ID_poop` INT NOT NULL AUTO_INCREMENT,
  `weight` INT NOT NULL,
  `air_quality` INT NOT NULL,
  `timestamp` TIMESTAMP(6) NULL DEFAULT CURRENT_TIMESTAMP(6),
  `food_ID` INT NOT NULL,
  PRIMARY KEY (`ID_poop`, `food_ID`),
  INDEX `fk_poop_food_idx` (`food_ID` ASC) VISIBLE,
  CONSTRAINT `fk_poop_food`
    FOREIGN KEY (`food_ID`)
    REFERENCES `poop_tracker`.`food` (`ID_food`))
ENGINE = InnoDB
AUTO_INCREMENT = 30
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;