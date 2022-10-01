-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 01, 2022 at 01:18 PM
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
  `item_id` bigint(15) NOT NULL,
  `text` text NOT NULL,
  `lang` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `i18n_dict`
--

CREATE TABLE `i18n_dict` (
  `item_id` bigint(15) NOT NULL,
  `chs` text NOT NULL,
  `cht` text NOT NULL,
  `de` text NOT NULL,
  `en` text NOT NULL,
  `es` text NOT NULL,
  `fr` text NOT NULL,
  `id` text NOT NULL,
  `jp` text NOT NULL,
  `kr` text NOT NULL,
  `pt` text NOT NULL,
  `ru` text NOT NULL,
  `th` text NOT NULL,
  `vi` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `i18n_dict`
--
ALTER TABLE `i18n_dict`
  ADD PRIMARY KEY (`item_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
