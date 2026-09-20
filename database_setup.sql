CREATE DATABASE IF NOT EXISTS guardian_pbvs CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'guardian_user'@'localhost' IDENTIFIED BY 'change_this_password';
GRANT ALL PRIVILEGES ON guardian_pbvs.* TO 'guardian_user'@'localhost';
FLUSH PRIVILEGES;
