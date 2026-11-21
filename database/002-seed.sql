-- Fictional seed data for S06
INSERT INTO exhibits (code, name, theme, suggested_minutes)
VALUES
('EXH-001', 'The Golden Kingdoms', 'Ancient Civilisations', 20),
('EXH-002', 'Oceans of Tomorrow', 'Nature and Conservation', 30),
('EXH-003', 'Inventors at Work', 'Science and Innovation', 25),
('EXH-004', 'Colours of the City', 'Art and Culture', 15),
('EXH-005', 'Beyond the Stars', 'Space and Astronomy', 35),
('EXH-006', 'The Living Archive', 'History and Memory', 20)
ON CONFLICT (code) DO NOTHING;
