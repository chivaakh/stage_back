/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.7.2-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: stage
-- ------------------------------------------------------
-- Server version	11.7.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add content type',4,'add_contenttype'),
(14,'Can change content type',4,'change_contenttype'),
(15,'Can delete content type',4,'delete_contenttype'),
(16,'Can view content type',4,'view_contenttype'),
(17,'Can add session',5,'add_session'),
(18,'Can change session',5,'change_session'),
(19,'Can delete session',5,'delete_session'),
(20,'Can view session',5,'view_session'),
(21,'Can add utilisateur',6,'add_utilisateur'),
(22,'Can change utilisateur',6,'change_utilisateur'),
(23,'Can delete utilisateur',6,'delete_utilisateur'),
(24,'Can view utilisateur',6,'view_utilisateur'),
(25,'Can add categorie',7,'add_categorie'),
(26,'Can change categorie',7,'change_categorie'),
(27,'Can delete categorie',7,'delete_categorie'),
(28,'Can view categorie',7,'view_categorie'),
(29,'Can add commande',8,'add_commande'),
(30,'Can change commande',8,'change_commande'),
(31,'Can delete commande',8,'delete_commande'),
(32,'Can view commande',8,'view_commande'),
(33,'Can add details client',9,'add_detailsclient'),
(34,'Can change details client',9,'change_detailsclient'),
(35,'Can delete details client',9,'delete_detailsclient'),
(36,'Can view details client',9,'view_detailsclient'),
(37,'Can add details commercant',10,'add_detailscommercant'),
(38,'Can change details commercant',10,'change_detailscommercant'),
(39,'Can delete details commercant',10,'delete_detailscommercant'),
(40,'Can view details commercant',10,'view_detailscommercant'),
(41,'Can add produit',11,'add_produit'),
(42,'Can change produit',11,'change_produit'),
(43,'Can delete produit',11,'delete_produit'),
(44,'Can view produit',11,'view_produit'),
(45,'Can add specification produit',12,'add_specificationproduit'),
(46,'Can change specification produit',12,'change_specificationproduit'),
(47,'Can delete specification produit',12,'delete_specificationproduit'),
(48,'Can view specification produit',12,'view_specificationproduit'),
(49,'Can add panier',13,'add_panier'),
(50,'Can change panier',13,'change_panier'),
(51,'Can delete panier',13,'delete_panier'),
(52,'Can view panier',13,'view_panier'),
(53,'Can add mouvement stock',14,'add_mouvementstock'),
(54,'Can change mouvement stock',14,'change_mouvementstock'),
(55,'Can delete mouvement stock',14,'delete_mouvementstock'),
(56,'Can view mouvement stock',14,'view_mouvementstock'),
(57,'Can add journal admin',15,'add_journaladmin'),
(58,'Can change journal admin',15,'change_journaladmin'),
(59,'Can delete journal admin',15,'delete_journaladmin'),
(60,'Can view journal admin',15,'view_journaladmin'),
(61,'Can add image utilisateur',16,'add_imageutilisateur'),
(62,'Can change image utilisateur',16,'change_imageutilisateur'),
(63,'Can delete image utilisateur',16,'delete_imageutilisateur'),
(64,'Can view image utilisateur',16,'view_imageutilisateur'),
(65,'Can add image produit',17,'add_imageproduit'),
(66,'Can change image produit',17,'change_imageproduit'),
(67,'Can delete image produit',17,'delete_imageproduit'),
(68,'Can view image produit',17,'view_imageproduit'),
(69,'Can add favori',18,'add_favori'),
(70,'Can change favori',18,'change_favori'),
(71,'Can delete favori',18,'delete_favori'),
(72,'Can view favori',18,'view_favori'),
(73,'Can add detail commande',19,'add_detailcommande'),
(74,'Can change detail commande',19,'change_detailcommande'),
(75,'Can delete detail commande',19,'delete_detailcommande'),
(76,'Can view detail commande',19,'view_detailcommande'),
(77,'Can add avis',20,'add_avis'),
(78,'Can change avis',20,'change_avis'),
(79,'Can delete avis',20,'delete_avis'),
(80,'Can view avis',20,'view_avis'),
(81,'Can add Token',21,'add_token'),
(82,'Can change Token',21,'change_token'),
(83,'Can delete Token',21,'delete_token'),
(84,'Can view Token',21,'view_token'),
(85,'Can add Token',22,'add_tokenproxy'),
(86,'Can change Token',22,'change_tokenproxy'),
(87,'Can delete Token',22,'delete_tokenproxy'),
(88,'Can view Token',22,'view_tokenproxy');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authtoken_token`
--

DROP TABLE IF EXISTS `authtoken_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `authtoken_token` (
  `key` varchar(40) NOT NULL,
  `created` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`key`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `authtoken_token_user_id_35299eff_fk_myapp_utilisateur_id` FOREIGN KEY (`user_id`) REFERENCES `myapp_utilisateur` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authtoken_token`
--

LOCK TABLES `authtoken_token` WRITE;
/*!40000 ALTER TABLE `authtoken_token` DISABLE KEYS */;
/*!40000 ALTER TABLE `authtoken_token` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_myapp_utilisateur_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_myapp_utilisateur_id` FOREIGN KEY (`user_id`) REFERENCES `myapp_utilisateur` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES
(1,'admin','logentry'),
(3,'auth','group'),
(2,'auth','permission'),
(21,'authtoken','token'),
(22,'authtoken','tokenproxy'),
(4,'contenttypes','contenttype'),
(20,'myapp','avis'),
(7,'myapp','categorie'),
(8,'myapp','commande'),
(19,'myapp','detailcommande'),
(9,'myapp','detailsclient'),
(10,'myapp','detailscommercant'),
(18,'myapp','favori'),
(17,'myapp','imageproduit'),
(16,'myapp','imageutilisateur'),
(15,'myapp','journaladmin'),
(14,'myapp','mouvementstock'),
(13,'myapp','panier'),
(11,'myapp','produit'),
(12,'myapp','specificationproduit'),
(6,'myapp','utilisateur'),
(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2025-05-21 19:14:32.182049'),
(2,'contenttypes','0002_remove_content_type_name','2025-05-21 19:14:32.219236'),
(3,'auth','0001_initial','2025-05-21 19:14:32.342027'),
(4,'auth','0002_alter_permission_name_max_length','2025-05-21 19:14:32.365387'),
(5,'auth','0003_alter_user_email_max_length','2025-05-21 19:14:32.368681'),
(6,'auth','0004_alter_user_username_opts','2025-05-21 19:14:32.371934'),
(7,'auth','0005_alter_user_last_login_null','2025-05-21 19:14:32.375608'),
(8,'auth','0006_require_contenttypes_0002','2025-05-21 19:14:32.376870'),
(9,'auth','0007_alter_validators_add_error_messages','2025-05-21 19:14:32.380644'),
(10,'auth','0008_alter_user_username_max_length','2025-05-21 19:14:32.383578'),
(11,'auth','0009_alter_user_last_name_max_length','2025-05-21 19:14:32.387169'),
(12,'auth','0010_alter_group_name_max_length','2025-05-21 19:14:32.404180'),
(13,'auth','0011_update_proxy_permissions','2025-05-21 19:14:32.408407'),
(14,'auth','0012_alter_user_first_name_max_length','2025-05-21 19:14:32.412300'),
(15,'myapp','0001_initial','2025-05-21 19:14:33.276108'),
(16,'admin','0001_initial','2025-05-21 19:14:33.338006'),
(17,'admin','0002_logentry_remove_auto_add','2025-05-21 19:14:33.351853'),
(18,'admin','0003_logentry_add_action_flag_choices','2025-05-21 19:14:33.359007'),
(19,'authtoken','0001_initial','2025-05-21 19:14:33.404227'),
(20,'authtoken','0002_auto_20160226_1747','2025-05-21 19:14:33.433967'),
(21,'authtoken','0003_tokenproxy','2025-05-21 19:14:33.436842'),
(22,'authtoken','0004_alter_tokenproxy_options','2025-05-21 19:14:33.440393'),
(23,'sessions','0001_initial','2025-05-21 19:14:33.464444');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_avis`
--

DROP TABLE IF EXISTS `myapp_avis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_avis` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `note` int(11) NOT NULL,
  `commentaire` longtext NOT NULL,
  `date_creation` datetime(6) NOT NULL,
  `client_id` bigint(20) NOT NULL,
  `produit_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_avis_client_id_91015af3_fk_myapp_detailsclient_id` (`client_id`),
  KEY `myapp_avis_produit_id_dd44cc06_fk_myapp_produit_id` (`produit_id`),
  CONSTRAINT `myapp_avis_client_id_91015af3_fk_myapp_detailsclient_id` FOREIGN KEY (`client_id`) REFERENCES `myapp_detailsclient` (`id`),
  CONSTRAINT `myapp_avis_produit_id_dd44cc06_fk_myapp_produit_id` FOREIGN KEY (`produit_id`) REFERENCES `myapp_produit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_avis`
--

LOCK TABLES `myapp_avis` WRITE;
/*!40000 ALTER TABLE `myapp_avis` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_avis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_categorie`
--

DROP TABLE IF EXISTS `myapp_categorie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_categorie` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_categorie`
--

LOCK TABLES `myapp_categorie` WRITE;
/*!40000 ALTER TABLE `myapp_categorie` DISABLE KEYS */;
INSERT INTO `myapp_categorie` VALUES
(1,'Chaussures','Chaussures de sport et ville'),
(2,'Accessoires','Accessoires de mode'),
(3,'Accessoires','Accessoires de mode'),
(4,'Accessoires','Accessoires de mode');
/*!40000 ALTER TABLE `myapp_categorie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_commande`
--

DROP TABLE IF EXISTS `myapp_commande`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_commande` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date_commande` datetime(6) NOT NULL,
  `montant_total` decimal(10,2) NOT NULL,
  `statut` varchar(30) NOT NULL,
  `client_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_commande_client_id_cf76bb53_fk_myapp_detailsclient_id` (`client_id`),
  CONSTRAINT `myapp_commande_client_id_cf76bb53_fk_myapp_detailsclient_id` FOREIGN KEY (`client_id`) REFERENCES `myapp_detailsclient` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_commande`
--

LOCK TABLES `myapp_commande` WRITE;
/*!40000 ALTER TABLE `myapp_commande` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_commande` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_detailcommande`
--

DROP TABLE IF EXISTS `myapp_detailcommande`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_detailcommande` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `quantite` int(11) NOT NULL,
  `prix_unitaire` decimal(10,2) NOT NULL,
  `commande_id` bigint(20) NOT NULL,
  `specification_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_detailcommande_commande_id_f97a6144_fk_myapp_commande_id` (`commande_id`),
  KEY `myapp_detailcommande_specification_id_cc1e6d62_fk_myapp_spe` (`specification_id`),
  CONSTRAINT `myapp_detailcommande_commande_id_f97a6144_fk_myapp_commande_id` FOREIGN KEY (`commande_id`) REFERENCES `myapp_commande` (`id`),
  CONSTRAINT `myapp_detailcommande_specification_id_cc1e6d62_fk_myapp_spe` FOREIGN KEY (`specification_id`) REFERENCES `myapp_specificationproduit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_detailcommande`
--

LOCK TABLES `myapp_detailcommande` WRITE;
/*!40000 ALTER TABLE `myapp_detailcommande` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_detailcommande` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_detailsclient`
--

DROP TABLE IF EXISTS `myapp_detailsclient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_detailsclient` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `adresse` longtext NOT NULL,
  `ville` varchar(100) NOT NULL,
  `code_postal` varchar(10) NOT NULL,
  `pays` varchar(50) NOT NULL,
  `photo_profil_id` bigint(20) DEFAULT NULL,
  `utilisateur_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `utilisateur_id` (`utilisateur_id`),
  KEY `myapp_detailsclient_photo_profil_id_78e948cb_fk_myapp_ima` (`photo_profil_id`),
  CONSTRAINT `myapp_detailsclient_photo_profil_id_78e948cb_fk_myapp_ima` FOREIGN KEY (`photo_profil_id`) REFERENCES `myapp_imageutilisateur` (`id`),
  CONSTRAINT `myapp_detailsclient_utilisateur_id_1f326b08_fk_myapp_uti` FOREIGN KEY (`utilisateur_id`) REFERENCES `myapp_utilisateur` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_detailsclient`
--

LOCK TABLES `myapp_detailsclient` WRITE;
/*!40000 ALTER TABLE `myapp_detailsclient` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_detailsclient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_detailscommercant`
--

DROP TABLE IF EXISTS `myapp_detailscommercant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_detailscommercant` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom_boutique` varchar(200) NOT NULL,
  `description_boutique` longtext NOT NULL,
  `adresse_commerciale` longtext NOT NULL,
  `ville` varchar(100) NOT NULL,
  `code_postal` varchar(10) NOT NULL,
  `pays` varchar(50) NOT NULL,
  `est_verifie` tinyint(1) NOT NULL,
  `note_moyenne` decimal(3,2) NOT NULL,
  `commission_rate` decimal(5,2) NOT NULL,
  `logo_id` bigint(20) DEFAULT NULL,
  `utilisateur_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `utilisateur_id` (`utilisateur_id`),
  KEY `myapp_detailscommerc_logo_id_433da5db_fk_myapp_ima` (`logo_id`),
  CONSTRAINT `myapp_detailscommerc_logo_id_433da5db_fk_myapp_ima` FOREIGN KEY (`logo_id`) REFERENCES `myapp_imageutilisateur` (`id`),
  CONSTRAINT `myapp_detailscommerc_utilisateur_id_31662696_fk_myapp_uti` FOREIGN KEY (`utilisateur_id`) REFERENCES `myapp_utilisateur` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_detailscommercant`
--

LOCK TABLES `myapp_detailscommercant` WRITE;
/*!40000 ALTER TABLE `myapp_detailscommercant` DISABLE KEYS */;
INSERT INTO `myapp_detailscommercant` VALUES
(1,'TechZone','Produits électroniques et gadgets','12 rue du test','Paris','75001','France',1,0.00,0.00,NULL,1);
/*!40000 ALTER TABLE `myapp_detailscommercant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_favori`
--

DROP TABLE IF EXISTS `myapp_favori`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_favori` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date_ajout` datetime(6) NOT NULL,
  `client_id` bigint(20) NOT NULL,
  `produit_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_favori_client_id_3a4ec73c_fk_myapp_detailsclient_id` (`client_id`),
  KEY `myapp_favori_produit_id_828f2961_fk_myapp_produit_id` (`produit_id`),
  CONSTRAINT `myapp_favori_client_id_3a4ec73c_fk_myapp_detailsclient_id` FOREIGN KEY (`client_id`) REFERENCES `myapp_detailsclient` (`id`),
  CONSTRAINT `myapp_favori_produit_id_828f2961_fk_myapp_produit_id` FOREIGN KEY (`produit_id`) REFERENCES `myapp_produit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_favori`
--

LOCK TABLES `myapp_favori` WRITE;
/*!40000 ALTER TABLE `myapp_favori` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_favori` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_imageproduit`
--

DROP TABLE IF EXISTS `myapp_imageproduit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_imageproduit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `url_image` varchar(255) NOT NULL,
  `est_principale` tinyint(1) NOT NULL,
  `ordre` int(11) NOT NULL,
  `date_ajout` datetime(6) NOT NULL,
  `produit_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_imageproduit_produit_id_8da7d421_fk_myapp_produit_id` (`produit_id`),
  CONSTRAINT `myapp_imageproduit_produit_id_8da7d421_fk_myapp_produit_id` FOREIGN KEY (`produit_id`) REFERENCES `myapp_produit` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_imageproduit`
--

LOCK TABLES `myapp_imageproduit` WRITE;
/*!40000 ALTER TABLE `myapp_imageproduit` DISABLE KEYS */;
INSERT INTO `myapp_imageproduit` VALUES
(1,'https://images.unsplash.com/photo-1517430816045-df4b7de11d1c',1,0,'2025-05-23 00:29:34.850802',1);
/*!40000 ALTER TABLE `myapp_imageproduit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_imageutilisateur`
--

DROP TABLE IF EXISTS `myapp_imageutilisateur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_imageutilisateur` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `url_image` varchar(255) NOT NULL,
  `type_image` varchar(50) NOT NULL,
  `date_ajout` datetime(6) NOT NULL,
  `utilisateur_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_imageutilisate_utilisateur_id_9eda16ba_fk_myapp_uti` (`utilisateur_id`),
  CONSTRAINT `myapp_imageutilisate_utilisateur_id_9eda16ba_fk_myapp_uti` FOREIGN KEY (`utilisateur_id`) REFERENCES `myapp_utilisateur` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_imageutilisateur`
--

LOCK TABLES `myapp_imageutilisateur` WRITE;
/*!40000 ALTER TABLE `myapp_imageutilisateur` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_imageutilisateur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_journaladmin`
--

DROP TABLE IF EXISTS `myapp_journaladmin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_journaladmin` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `action` varchar(255) NOT NULL,
  `details` longtext NOT NULL,
  `date_heure` datetime(6) NOT NULL,
  `admin_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_journaladmin_admin_id_5a923b07_fk_myapp_utilisateur_id` (`admin_id`),
  CONSTRAINT `myapp_journaladmin_admin_id_5a923b07_fk_myapp_utilisateur_id` FOREIGN KEY (`admin_id`) REFERENCES `myapp_utilisateur` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_journaladmin`
--

LOCK TABLES `myapp_journaladmin` WRITE;
/*!40000 ALTER TABLE `myapp_journaladmin` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_journaladmin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_mouvementstock`
--

DROP TABLE IF EXISTS `myapp_mouvementstock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_mouvementstock` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `quantite` int(11) NOT NULL,
  `type_mouvement` varchar(30) NOT NULL,
  `reference_document` varchar(50) DEFAULT NULL,
  `date_mouvement` datetime(6) NOT NULL,
  `commentaire` longtext DEFAULT NULL,
  `specification_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_mouvementstock_specification_id_ff4ab3c5_fk_myapp_spe` (`specification_id`),
  CONSTRAINT `myapp_mouvementstock_specification_id_ff4ab3c5_fk_myapp_spe` FOREIGN KEY (`specification_id`) REFERENCES `myapp_specificationproduit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_mouvementstock`
--

LOCK TABLES `myapp_mouvementstock` WRITE;
/*!40000 ALTER TABLE `myapp_mouvementstock` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_mouvementstock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_panier`
--

DROP TABLE IF EXISTS `myapp_panier`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_panier` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `quantite` int(11) NOT NULL,
  `date_ajout` datetime(6) NOT NULL,
  `client_id` bigint(20) NOT NULL,
  `specification_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_panier_client_id_0b5ea34d_fk_myapp_detailsclient_id` (`client_id`),
  KEY `myapp_panier_specification_id_e6f4051f_fk_myapp_spe` (`specification_id`),
  CONSTRAINT `myapp_panier_client_id_0b5ea34d_fk_myapp_detailsclient_id` FOREIGN KEY (`client_id`) REFERENCES `myapp_detailsclient` (`id`),
  CONSTRAINT `myapp_panier_specification_id_e6f4051f_fk_myapp_spe` FOREIGN KEY (`specification_id`) REFERENCES `myapp_specificationproduit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_panier`
--

LOCK TABLES `myapp_panier` WRITE;
/*!40000 ALTER TABLE `myapp_panier` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_panier` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_produit`
--

DROP TABLE IF EXISTS `myapp_produit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_produit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `reference` varchar(50) NOT NULL,
  `nom` varchar(200) NOT NULL,
  `description` longtext NOT NULL,
  `categorie_id` bigint(20) DEFAULT NULL,
  `commercant_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_produit_categorie_id_35db9b9e_fk_myapp_categorie_id` (`categorie_id`),
  KEY `myapp_produit_commercant_id_1592e531_fk_myapp_det` (`commercant_id`),
  CONSTRAINT `myapp_produit_categorie_id_35db9b9e_fk_myapp_categorie_id` FOREIGN KEY (`categorie_id`) REFERENCES `myapp_categorie` (`id`),
  CONSTRAINT `myapp_produit_commercant_id_1592e531_fk_myapp_det` FOREIGN KEY (`commercant_id`) REFERENCES `myapp_detailscommercant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_produit`
--

LOCK TABLES `myapp_produit` WRITE;
/*!40000 ALTER TABLE `myapp_produit` DISABLE KEYS */;
INSERT INTO `myapp_produit` VALUES
(1,'ACC001','Montre connectée','Montre connectée avec cardiofréquencemètre et GPS.',4,1);
/*!40000 ALTER TABLE `myapp_produit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_specificationproduit`
--

DROP TABLE IF EXISTS `myapp_specificationproduit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_specificationproduit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `description` longtext NOT NULL,
  `prix` decimal(10,2) NOT NULL,
  `prix_promo` decimal(10,2) DEFAULT NULL,
  `quantite_stock` int(11) NOT NULL,
  `est_defaut` tinyint(1) NOT NULL,
  `reference_specification` varchar(50) NOT NULL,
  `produit_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `myapp_specificationp_produit_id_ddc5f849_fk_myapp_pro` (`produit_id`),
  CONSTRAINT `myapp_specificationp_produit_id_ddc5f849_fk_myapp_pro` FOREIGN KEY (`produit_id`) REFERENCES `myapp_produit` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_specificationproduit`
--

LOCK TABLES `myapp_specificationproduit` WRITE;
/*!40000 ALTER TABLE `myapp_specificationproduit` DISABLE KEYS */;
INSERT INTO `myapp_specificationproduit` VALUES
(1,'Noir - Taille unique','Montre connectée noire',199.99,159.99,10,1,'ACC001-NOIR',1);
/*!40000 ALTER TABLE `myapp_specificationproduit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_utilisateur`
--

DROP TABLE IF EXISTS `myapp_utilisateur`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_utilisateur` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `telephone` varchar(20) NOT NULL,
  `date_inscription` datetime(6) NOT NULL,
  `derniere_connexion` datetime(6) NOT NULL,
  `est_actif` tinyint(1) NOT NULL,
  `role` varchar(20) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_utilisateur`
--

LOCK TABLES `myapp_utilisateur` WRITE;
/*!40000 ALTER TABLE `myapp_utilisateur` DISABLE KEYS */;
INSERT INTO `myapp_utilisateur` VALUES
(1,'pbkdf2_sha256$1000000$Mc82aw5s0ll7PlzuMMlMrt$49sd0fa2Zp/tNkvD38gkQvPP/7pcWjKsx01NepY3Xxk=',NULL,'vendeur@test.com','0600000000','2025-05-23 00:29:07.242549','2025-05-23 00:29:07.242586',1,'commercant',0,0);
/*!40000 ALTER TABLE `myapp_utilisateur` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_utilisateur_groups`
--

DROP TABLE IF EXISTS `myapp_utilisateur_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_utilisateur_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `utilisateur_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `myapp_utilisateur_groups_utilisateur_id_group_id_45ab4903_uniq` (`utilisateur_id`,`group_id`),
  KEY `myapp_utilisateur_groups_group_id_254254f5_fk_auth_group_id` (`group_id`),
  CONSTRAINT `myapp_utilisateur_gr_utilisateur_id_cc363a5d_fk_myapp_uti` FOREIGN KEY (`utilisateur_id`) REFERENCES `myapp_utilisateur` (`id`),
  CONSTRAINT `myapp_utilisateur_groups_group_id_254254f5_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_utilisateur_groups`
--

LOCK TABLES `myapp_utilisateur_groups` WRITE;
/*!40000 ALTER TABLE `myapp_utilisateur_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_utilisateur_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `myapp_utilisateur_user_permissions`
--

DROP TABLE IF EXISTS `myapp_utilisateur_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `myapp_utilisateur_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `utilisateur_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `myapp_utilisateur_user_p_utilisateur_id_permissio_03f9ce61_uniq` (`utilisateur_id`,`permission_id`),
  KEY `myapp_utilisateur_us_permission_id_50e03da4_fk_auth_perm` (`permission_id`),
  CONSTRAINT `myapp_utilisateur_us_permission_id_50e03da4_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `myapp_utilisateur_us_utilisateur_id_5aa90dbb_fk_myapp_uti` FOREIGN KEY (`utilisateur_id`) REFERENCES `myapp_utilisateur` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `myapp_utilisateur_user_permissions`
--

LOCK TABLES `myapp_utilisateur_user_permissions` WRITE;
/*!40000 ALTER TABLE `myapp_utilisateur_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `myapp_utilisateur_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-05-23 12:01:21
