-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 14, 2023 at 09:45 AM
-- Server version: 10.6.5-MariaDB-log
-- PHP Version: 7.4.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `uigf_dict`
--

-- --------------------------------------------------------

--
-- Table structure for table `generic_dict`
--

CREATE TABLE `generic_dict` (
  `game_id` int(11) NOT NULL,
  `item_id` bigint(15) NOT NULL,
  `text` text NOT NULL,
  `lang` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `i18n_dict`
--

CREATE TABLE `i18n_dict` (
  `game_id` int(11) NOT NULL,
  `item_id` bigint(15) NOT NULL,
  `chs_text` text NOT NULL,
  `cht_text` text NOT NULL,
  `de_text` text NOT NULL,
  `en_text` text NOT NULL,
  `es_text` text NOT NULL,
  `fr_text` text NOT NULL,
  `id_text` text NOT NULL,
  `jp_text` text NOT NULL,
  `kr_text` text NOT NULL,
  `pt_text` text NOT NULL,
  `ru_text` text NOT NULL,
  `th_text` text NOT NULL,
  `vi_text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `i18n_dict`
--
ALTER TABLE `i18n_dict`
  ADD PRIMARY KEY (`game_id`,`item_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
