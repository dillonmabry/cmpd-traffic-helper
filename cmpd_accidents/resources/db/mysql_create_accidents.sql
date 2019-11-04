-- Seed script for MySQL SQLAlchemy table creation example
-- Columns are as varchar from service response text/xml, process if needed as specific types
CREATE DATABASE `cmpd_accidents`;
CREATE TABLE `cmpd_accidents`.`accidents` (
  `EventNo` VARCHAR(150) NOT NULL,
  `XCoordinate` VARCHAR(150) NULL,
  `YCoordinate` VARCHAR(150) NULL,
  `EventDateTime` VARCHAR(150) NULL,
  `TypeDescription` VARCHAR(250) NULL,
  `CrossStreet1` VARCHAR(150) NULL,
  `CrossStreet2` VARCHAR(150) NULL,
  `Latitude` VARCHAR(150) NULL,
  `Division` VARCHAR(150) NULL,
  `Longitude` VARCHAR(150) NULL,
  `TypeCode` VARCHAR(150) NULL,
  `weatherInfo` JSON,
  PRIMARY KEY (`EventNo`));