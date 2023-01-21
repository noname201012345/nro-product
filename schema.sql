DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT ,
  `username` varchar(255) NOT NULL ,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL
);