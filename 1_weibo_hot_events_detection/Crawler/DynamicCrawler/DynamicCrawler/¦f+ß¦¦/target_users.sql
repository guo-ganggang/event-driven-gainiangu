/*
Navicat MySQL Data Transfer

Source Server         : Master_DB
Source Server Version : 50628
Source Host           : 123.56.187.168:3306
Source Database       : Chinese_stream

Target Server Type    : MYSQL
Target Server Version : 50628
File Encoding         : 65001

Date: 2016-11-24 00:14:43
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for target_users
-- ----------------------------
DROP TABLE IF EXISTS `target_users`;
CREATE TABLE `target_users` (
  `uid` varchar(45) NOT NULL,
  `weight` int(11) NOT NULL DEFAULT '1',
  `domain` int(11) NOT NULL DEFAULT '0',
  `subdomain` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
