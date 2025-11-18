CREATE TABLE campaign_performance (
    campaign_id      VARCHAR(50) PRIMARY KEY,
    platform         VARCHAR(50),
    influencer_category VARCHAR(50),
    campaign_type    VARCHAR(50),
    start_date       TIMESTAMP,
    engagements      INT,
    estimated_reach  INT,
    product_sales    FLOAT,
    budget           FLOAT,
    campaign_duration_days INT,
    end_date         TIMESTAMP
);