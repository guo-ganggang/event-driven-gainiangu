/*
Navicat MySQL Data Transfer

Source Server         : Master_DB
Source Server Version : 50628
Source Host           : 123.56.187.168:3306
Source Database       : Chinese_stream

Target Server Type    : MYSQL
Target Server Version : 50628
File Encoding         : 65001

Date: 2016-11-24 00:14:13
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for account_parameters
-- ----------------------------
DROP TABLE IF EXISTS `account_parameters`;
CREATE TABLE `account_parameters` (
  `i` varchar(45) NOT NULL,
  `s` varchar(45) NOT NULL,
  `gsid` varchar(155) NOT NULL,
  `domain` int(11) NOT NULL DEFAULT '0',
  `account` varchar(100) NOT NULL,
  `passwd` varchar(100) NOT NULL DEFAULT 'q1314120',
  PRIMARY KEY (`account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
