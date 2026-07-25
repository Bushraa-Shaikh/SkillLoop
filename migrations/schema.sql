-- =============================================================
-- SkillLoop – SQL Server Schema
-- Run this script once against your SQL Server instance.
-- =============================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'skillloop_db')
BEGIN
    CREATE DATABASE skillloop_db;
END
GO

USE skillloop_db;
GO

-- ---------------------------------------------------------------
-- 1. USERS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
CREATE TABLE Users (
    user_id         INT IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(100)   NOT NULL,
    email           NVARCHAR(255)   NOT NULL UNIQUE,
    password_hash   NVARCHAR(255)   NULL,          -- NULL for OAuth users
    university      NVARCHAR(200)   NULL,
    country         NVARCHAR(100)   NULL,
    bio             NVARCHAR(MAX)   NULL,
    profile_pic     NVARCHAR(500)   NULL,
    role            NVARCHAR(20)    NOT NULL DEFAULT 'buyer',   -- buyer | seller | both | admin
    is_verified     BIT             NOT NULL DEFAULT 0,
    verification_method NVARCHAR(20) NULL,         -- email | student_id
    auth_provider   NVARCHAR(20)    NOT NULL DEFAULT 'local',  -- local | google
    google_id       NVARCHAR(100)   NULL,
    is_active       BIT             NOT NULL DEFAULT 1,
    joined_at       DATETIME        NOT NULL DEFAULT GETDATE(),
    last_login      DATETIME        NULL,
    rating          FLOAT           NULL DEFAULT 0,
    total_reviews   INT             NOT NULL DEFAULT 0
);
GO

-- ---------------------------------------------------------------
-- 2. SKILLS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Skills' AND xtype='U')
CREATE TABLE Skills (
    skill_id    INT IDENTITY(1,1) PRIMARY KEY,
    name        NVARCHAR(100) NOT NULL UNIQUE,
    category    NVARCHAR(100) NULL,
    icon        NVARCHAR(50)  NULL
);
GO

-- ---------------------------------------------------------------
-- 3. USER SKILLS  (many-to-many)
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='UserSkills' AND xtype='U')
CREATE TABLE UserSkills (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    skill_id    INT NOT NULL REFERENCES Skills(skill_id) ON DELETE CASCADE,
    level       NVARCHAR(20) NULL DEFAULT 'Intermediate',  -- Beginner|Intermediate|Expert
    UNIQUE (user_id, skill_id)
);
GO

-- ---------------------------------------------------------------
-- 4. BADGES
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Badges' AND xtype='U')
CREATE TABLE Badges (
    badge_id    INT IDENTITY(1,1) PRIMARY KEY,
    name        NVARCHAR(100) NOT NULL,
    description NVARCHAR(500) NULL,
    icon        NVARCHAR(200) NULL,
    criteria    NVARCHAR(500) NULL
);
GO

-- ---------------------------------------------------------------
-- 5. USER BADGES  (many-to-many)
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='UserBadges' AND xtype='U')
CREATE TABLE UserBadges (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    badge_id    INT NOT NULL REFERENCES Badges(badge_id),
    earned_at   DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 6. GIGS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Gigs' AND xtype='U')
CREATE TABLE Gigs (
    gig_id          INT IDENTITY(1,1) PRIMARY KEY,
    seller_id       INT NOT NULL REFERENCES Users(user_id),
    title           NVARCHAR(200)   NOT NULL,
    description     NVARCHAR(MAX)   NOT NULL,
    category        NVARCHAR(100)   NULL,
    price           DECIMAL(10,2)   NOT NULL DEFAULT 0,
    delivery_days   INT             NOT NULL DEFAULT 3,
    revisions       INT             NOT NULL DEFAULT 1,
    thumbnail       NVARCHAR(500)   NULL,
    tags            NVARCHAR(500)   NULL,
    is_active       BIT             NOT NULL DEFAULT 1,
    allow_swap      BIT             NOT NULL DEFAULT 0,   -- skill-swap accepted
    views           INT             NOT NULL DEFAULT 0,
    orders_count    INT             NOT NULL DEFAULT 0,
    rating          FLOAT           NULL DEFAULT 0,
    total_reviews   INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL DEFAULT GETDATE(),
    updated_at      DATETIME        NULL
);
GO

-- ---------------------------------------------------------------
-- 7. GIG IMAGES
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='GigImages' AND xtype='U')
CREATE TABLE GigImages (
    image_id    INT IDENTITY(1,1) PRIMARY KEY,
    gig_id      INT NOT NULL REFERENCES Gigs(gig_id) ON DELETE CASCADE,
    image_path  NVARCHAR(500) NOT NULL,
    sort_order  INT NOT NULL DEFAULT 0
);
GO

-- ---------------------------------------------------------------
-- 8. WALLET
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Wallet' AND xtype='U')
CREATE TABLE Wallet (
    wallet_id   INT IDENTITY(1,1) PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE REFERENCES Users(user_id) ON DELETE CASCADE,
    balance     DECIMAL(10,2) NOT NULL DEFAULT 0,
    updated_at  DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 9. TRANSACTIONS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Transactions' AND xtype='U')
CREATE TABLE Transactions (
    txn_id      INT IDENTITY(1,1) PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES Users(user_id),
    order_id    INT NULL,                          -- FK added after Orders created
    type        NVARCHAR(30) NOT NULL,             -- credit | debit | escrow | release | refund
    amount      DECIMAL(10,2) NOT NULL,
    description NVARCHAR(500) NULL,
    created_at  DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 10. ORDERS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Orders' AND xtype='U')
CREATE TABLE Orders (
    order_id        INT IDENTITY(1,1) PRIMARY KEY,
    gig_id          INT NOT NULL REFERENCES Gigs(gig_id),
    buyer_id        INT NOT NULL REFERENCES Users(user_id),
    seller_id       INT NOT NULL REFERENCES Users(user_id),
    status          NVARCHAR(30)    NOT NULL DEFAULT 'Pending',
                    -- Pending | InProgress | Delivered | Completed | Cancelled | Disputed
    payment_method  NVARCHAR(20)    NOT NULL DEFAULT 'coins',  -- coins | swap
    amount          DECIMAL(10,2)   NOT NULL DEFAULT 0,
    requirements    NVARCHAR(MAX)   NULL,
    delivery_link   NVARCHAR(1000)  NULL,          -- drive link from seller
    created_at      DATETIME        NOT NULL DEFAULT GETDATE(),
    updated_at      DATETIME        NULL,
    delivered_at    DATETIME        NULL,
    completed_at    DATETIME        NULL
);
GO

-- Add FK from Transactions to Orders
ALTER TABLE Transactions
    ADD CONSTRAINT FK_Txn_Order FOREIGN KEY (order_id)
    REFERENCES Orders(order_id);
GO

-- ---------------------------------------------------------------
-- 11. REVIEWS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Reviews' AND xtype='U')
CREATE TABLE Reviews (
    review_id   INT IDENTITY(1,1) PRIMARY KEY,
    order_id    INT NOT NULL UNIQUE REFERENCES Orders(order_id),
    gig_id      INT NOT NULL REFERENCES Gigs(gig_id),
    reviewer_id INT NOT NULL REFERENCES Users(user_id),
    seller_id   INT NOT NULL REFERENCES Users(user_id),
    rating      TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     NVARCHAR(MAX) NULL,
    created_at  DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 12. MESSAGES
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Messages' AND xtype='U')
CREATE TABLE Messages (
    message_id  INT IDENTITY(1,1) PRIMARY KEY,
    order_id    INT NOT NULL REFERENCES Orders(order_id) ON DELETE CASCADE,
    sender_id   INT NOT NULL REFERENCES Users(user_id),
    body        NVARCHAR(MAX)   NOT NULL,
    drive_link  NVARCHAR(1000)  NULL,              -- optional file-share drive link
    is_read     BIT             NOT NULL DEFAULT 0,
    sent_at     DATETIME        NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 13. PROJECTS  (buyer posts a project for bidding)
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Projects' AND xtype='U')
CREATE TABLE Projects (
    project_id  INT IDENTITY(1,1) PRIMARY KEY,
    buyer_id    INT NOT NULL REFERENCES Users(user_id),
    title       NVARCHAR(200)   NOT NULL,
    description NVARCHAR(MAX)   NOT NULL,
    budget_min  DECIMAL(10,2)   NULL,
    budget_max  DECIMAL(10,2)   NULL,
    deadline    DATE            NULL,
    category    NVARCHAR(100)   NULL,
    status      NVARCHAR(20)    NOT NULL DEFAULT 'Open',  -- Open | Closed | Awarded
    created_at  DATETIME        NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 14. BIDS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Bids' AND xtype='U')
CREATE TABLE Bids (
    bid_id          INT IDENTITY(1,1) PRIMARY KEY,
    project_id      INT NOT NULL REFERENCES Projects(project_id) ON DELETE CASCADE,
    seller_id       INT NOT NULL REFERENCES Users(user_id),
    amount          DECIMAL(10,2) NOT NULL,
    delivery_days   INT NOT NULL DEFAULT 3,
    proposal        NVARCHAR(MAX) NULL,
    status          NVARCHAR(20)  NOT NULL DEFAULT 'Pending',  -- Pending | Accepted | Rejected
    created_at      DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 15. NOTIFICATIONS
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Notifications' AND xtype='U')
CREATE TABLE Notifications (
    notif_id    INT IDENTITY(1,1) PRIMARY KEY,
    user_id     INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    type        NVARCHAR(50)    NOT NULL,    -- order | message | bid | review | system
    title       NVARCHAR(200)   NOT NULL,
    body        NVARCHAR(500)   NULL,
    link        NVARCHAR(500)   NULL,
    is_read     BIT             NOT NULL DEFAULT 0,
    created_at  DATETIME        NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- 16. PORTFOLIO  (showcase items on profile)
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Portfolio' AND xtype='U')
CREATE TABLE Portfolio (
    portfolio_id    INT IDENTITY(1,1) PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    title           NVARCHAR(200)   NOT NULL,
    description     NVARCHAR(MAX)   NULL,
    image_path      NVARCHAR(500)   NULL,
    link            NVARCHAR(500)   NULL,
    created_at      DATETIME NOT NULL DEFAULT GETDATE()
);
GO

-- ---------------------------------------------------------------
-- Seed: default skill categories
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM Skills)
BEGIN
    INSERT INTO Skills (name, category) VALUES
        ('Web Development',   'Tech'),
        ('Mobile Development','Tech'),
        ('Graphic Design',    'Design'),
        ('UI/UX Design',      'Design'),
        ('Video Editing',     'Media'),
        ('Content Writing',   'Writing'),
        ('Data Analysis',     'Data'),
        ('Machine Learning',  'Data'),
        ('Digital Marketing', 'Marketing'),
        ('Translation',       'Languages'),
        ('Tutoring',          'Education'),
        ('Music Production',  'Media');
END
GO

-- ---------------------------------------------------------------
-- Seed: badges
-- ---------------------------------------------------------------
IF NOT EXISTS (SELECT 1 FROM Badges)
BEGIN
    INSERT INTO Badges (name, description, criteria) VALUES
        ('Top Seller',     'Completed 50+ orders',          'orders >= 50'),
        ('New Talent',     'Account less than 30 days old', 'account_age < 30'),
        ('Rising Star',    '5-star rating with 10+ reviews','rating=5 AND reviews>=10'),
        ('Verified Student','University verified',          'is_verified=1'),
        ('Speed Demon',    'All deliveries on time',        'late_deliveries=0');
END
GO

PRINT 'SkillLoop schema created successfully.';
GO