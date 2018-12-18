-- Seed script for MySQL SQLAlchemy table creation example
-- Columns are as varchar from service response text/xml, process if needed as specific types
CREATE DATABASE `cmpd_accidents`;
CREATE TABLE `cmpd_accidents`.`accidents` (
  `event_no` VARCHAR(150) NOT NULL,
  `x_coord` VARCHAR(150) NULL,
  `y_coord` VARCHAR(150) NULL,
  `datetime_add` VARCHAR(150) NULL,
  `event_desc` VARCHAR(250) NULL,
  `address` VARCHAR(150) NULL,
  `latitude` VARCHAR(150) NULL,
  `division` VARCHAR(150) NULL,
  `longitude` VARCHAR(150) NULL,
  `event_type` VARCHAR(150) NULL,
  `weatherInfo` JSON,
  PRIMARY KEY (`event_no`));