INSERT INTO users(email,name,password_hash,role,enabled,created_at)
VALUES ('john@aisupport.com','John Doe','$2a$10$0m.Nuft/3Gtg6ABF8UAJYOmBpF8VrYzilxfgNxtToboT7bY8zl.S6','customer',true,NOW())
ON CONFLICT (email) DO NOTHING;

INSERT INTO users(email,name,password_hash,role,enabled,created_at)
VALUES ('officer@aisupport.com','Support Officer','$2a$10$0m.Nuft/3Gtg6ABF8UAJYOmBpF8VrYzilxfgNxtToboT7bY8zl.S6','officer',true,NOW())
ON CONFLICT (email) DO NOTHING;

INSERT INTO customers(email,name,tier,status,created_at,updated_at,metadata)
VALUES ('john@aisupport.com','John Doe','pro','active',NOW(),NOW(),'{"plan":"pro"}')
ON CONFLICT (email) DO NOTHING;
