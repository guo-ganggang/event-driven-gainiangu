/*
Navicat MySQL Data Transfer

Source Server         : Master_DB
Source Server Version : 50628
Source Host           : 123.56.187.168:3306
Source Database       : Chinese_stream

Target Server Type    : MYSQL
Target Server Version : 50628
File Encoding         : 65001

Date: 2016-11-24 00:15:20
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for timelines_live
-- ----------------------------
DROP TABLE IF EXISTS `timelines_live`;
CREATE TABLE `timelines_live` (
  `mid` bigint(20) NOT NULL,
  `uid` bigint(20) NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  `omid` bigint(20) DEFAULT NULL,
  `ouid` bigint(20) DEFAULT NULL,
  `oname` varchar(30) DEFAULT NULL,
  `text` varchar(1024) NOT NULL,
  `pic_url` varchar(1024) DEFAULT NULL,
  `app_source` varchar(45) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `repost_num` int(11) NOT NULL,
  `favourite_num` int(11) NOT NULL,
  `comment_num` int(11) NOT NULL,
  `geo_info` varchar(75) DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  PRIMARY KEY (`mid`),
  KEY `t_index` (`created_at`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
