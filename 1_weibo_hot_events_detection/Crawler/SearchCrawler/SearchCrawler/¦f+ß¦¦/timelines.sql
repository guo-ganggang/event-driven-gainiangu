/*
Navicat MySQL Data Transfer

Source Server         : Master_DB
Source Server Version : 50628
Source Host           : 123.56.187.168:3306
Source Database       : search_crawler

Target Server Type    : MYSQL
Target Server Version : 50628
File Encoding         : 65001

Date: 2016-11-23 21:27:20
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for timelines
-- ----------------------------
DROP TABLE IF EXISTS `timelines`;
CREATE TABLE `timelines` (
  `mid` bigint(20) NOT NULL,
  `encrypted_mid` varchar(20) COLLATE utf8_bin NOT NULL,
  `uid` bigint(20) NOT NULL,
  `screen_name` varchar(50) COLLATE utf8_bin NOT NULL,
  `text` varchar(2048) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `app_source` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `attitudes` int(11) NOT NULL,
  `comments` int(11) NOT NULL,
  `reposts` int(11) NOT NULL,
  `pic_urls` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `json` mediumtext COLLATE utf8_bin NOT NULL,
  `timestamp` datetime NOT NULL,
  `omid` bigint(20) NOT NULL,
  PRIMARY KEY (`mid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
