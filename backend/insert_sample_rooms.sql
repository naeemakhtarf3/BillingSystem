-- Insert sample room data
INSERT INTO room (room_number, type, status, daily_rate_cents, created_at, updated_at) VALUES
-- Standard Rooms
('101', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('102', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('103', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('104', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('105', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('106', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('107', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('108', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('109', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('110', 'standard', 'available', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Private Rooms
('201', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('202', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('203', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('204', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('205', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('206', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('207', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('208', 'private', 'available', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- ICU Rooms
('301', 'icu', 'available', 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('302', 'icu', 'available', 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('303', 'icu', 'available', 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('304', 'icu', 'available', 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('305', 'icu', 'available', 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('306', 'icu', 'available', 50000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- Maintenance Rooms
('401', 'standard', 'maintenance', 15000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('402', 'private', 'maintenance', 25000, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
