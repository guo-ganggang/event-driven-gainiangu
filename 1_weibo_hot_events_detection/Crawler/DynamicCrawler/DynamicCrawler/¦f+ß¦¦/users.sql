/*
Navicat MySQL Data Transfer

Source Server         : Master_DB
Source Server Version : 50628
Source Host           : 123.56.187.168:3306
Source Database       : Chinese_stream

Target Server Type    : MYSQL
Target Server Version : 50628
File Encoding         : 65001

Date: 2016-11-24 00:15:31
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` bigint(20) NOT NULL,
  `screen_name` varchar(255) NOT NULL,
  `avatar` varchar(255) NOT NULL,
  `description` varchar(1024) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `gender` varchar(255) NOT NULL,
  `follower_num` int(11) NOT NULL,
  `followee_num` int(11) NOT NULL,
  `weibo_num` int(11) NOT NULL,
  `level` int(255) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `credit_score` int(11) DEFAULT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `vip_level` int(11) DEFAULT NULL,
  `verified` int(255) NOT NULL,
  `verified_reason` varchar(510) DEFAULT NULL,
  `tags` varchar(510) DEFAULT NULL,
  `badges` varchar(510) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `json` text,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
