-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 06, 2025 at 03:34 PM
-- Server version: 8.0.35
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `uigf`
--

-- --------------------------------------------------------

--
-- Table structure for table `i18n_dict`
--

CREATE TABLE `i18n_dict` (
  `game_id` int NOT NULL,
  `item_id` bigint NOT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
