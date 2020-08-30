/*
Navicat MySQL Data Transfer

Source Server         : Master_DB
Source Server Version : 50628
Source Host           : 123.56.187.168:3306
Source Database       : Chinese_stream

Target Server Type    : MYSQL
Target Server Version : 50628
File Encoding         : 65001

Date: 2016-11-24 00:14:32
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for alarms
-- ----------------------------
DROP TABLE IF EXISTS `alarms`;
CREATE TABLE `alarms` (
  `domain` int(11) NOT NULL,
  `is_on` int(11) NOT NULL DEFAULT '0',
  `launch_time` datetime NOT NULL,
  PRIMARY KEY (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
