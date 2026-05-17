-- ============================================
-- TradeFlow - 交易标签表 Schema
-- 用于快捷交易功能
-- ============================================

-- 4. 交易标签表 (stock_trade_tags)
CREATE TABLE IF NOT EXISTS stock_trade_tags (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    contract VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    latest_price DECIMAL(10, 4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_stock_trade_tags_contract ON stock_trade_tags(contract);

-- 启用 RLS
ALTER TABLE stock_trade_tags ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作）
DROP POLICY IF EXISTS "Allow all operations on stock_trade_tags" ON stock_trade_tags;
CREATE POLICY "Allow all operations on stock_trade_tags" ON stock_trade_tags
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 触发器：自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_stock_trade_tags_updated_at ON stock_trade_tags;
CREATE TRIGGER trg_stock_trade_tags_updated_at
BEFORE UPDATE ON stock_trade_tags
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 5. 持仓比例计算表 (portfolio_items)
CREATE TABLE IF NOT EXISTS portfolio_items (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contract VARCHAR(20) NOT NULL,
    tag VARCHAR(50) DEFAULT '',
    price DECIMAL(12, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引优化
CREATE INDEX IF NOT EXISTS idx_portfolio_items_tag ON portfolio_items(tag);
CREATE INDEX IF NOT EXISTS idx_portfolio_items_contract ON portfolio_items(contract);

-- 启用 RLS
ALTER TABLE portfolio_items ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作）
DROP POLICY IF EXISTS "Allow all operations on portfolio_items" ON portfolio_items;
CREATE POLICY "Allow all operations on portfolio_items" ON portfolio_items
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 触发器：自动更新 updated_at
DROP TRIGGER IF EXISTS trg_portfolio_items_updated_at ON portfolio_items;
CREATE TRIGGER trg_portfolio_items_updated_at
BEFORE UPDATE ON portfolio_items
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- 注释说明
COMMENT ON TABLE stock_trade_tags IS '交易标签表（快捷交易入口）';
COMMENT ON COLUMN stock_trade_tags.contract IS '合约代码（唯一）';
COMMENT ON COLUMN stock_trade_tags.name IS '合约名称';
COMMENT ON COLUMN stock_trade_tags.latest_price IS '最新价格（预留字段，后续由外部业务更新）';
COMMENT ON TABLE portfolio_items IS '持仓比例计算表';
COMMENT ON COLUMN portfolio_items.tag IS '分类标签（如白酒、科技等）';

-- ============================================
-- TradeFlow - 用户认证 Schema
-- ============================================

-- 6. 用户表 (app_users)
CREATE TABLE IF NOT EXISTS app_users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 迁移：如果旧表存在 email 列，重命名为 username
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'app_users' AND column_name = 'email'
    ) THEN
        ALTER TABLE app_users RENAME COLUMN email TO username;
        ALTER TABLE app_users ALTER COLUMN username TYPE VARCHAR(50);
    END IF;
END $$;

-- 清理旧索引（如果存在）
DROP INDEX IF EXISTS idx_app_users_email;

-- 索引
CREATE INDEX IF NOT EXISTS idx_app_users_username ON app_users(username);

-- 启用 RLS
ALTER TABLE app_users ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作）
DROP POLICY IF EXISTS "Allow all operations on app_users" ON app_users;
CREATE POLICY "Allow all operations on app_users" ON app_users
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 触发器：自动更新 updated_at
DROP TRIGGER IF EXISTS trg_app_users_updated_at ON app_users;
CREATE TRIGGER trg_app_users_updated_at
    BEFORE UPDATE ON app_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 用户认证 RPC 函数
-- ============================================

-- 验证用户登录
DROP FUNCTION IF EXISTS verify_user(VARCHAR, VARCHAR);

CREATE OR REPLACE FUNCTION verify_user(p_username VARCHAR, p_password VARCHAR)
RETURNS JSONB AS $$
DECLARE
    v_user app_users%ROWTYPE;
BEGIN
    SELECT * INTO v_user FROM app_users WHERE username = p_username;
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;
    IF v_user.password = md5(p_password || v_user.salt) THEN
        RETURN jsonb_build_object('id', v_user.id, 'username', v_user.username, 'role', v_user.role);
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 用户注册（自动生成密码）
DROP FUNCTION IF EXISTS register_user(VARCHAR);

CREATE OR REPLACE FUNCTION register_user(p_username VARCHAR)
RETURNS JSONB AS $$
DECLARE
    v_salt VARCHAR(32);
    v_password VARCHAR(16);
    v_hashed VARCHAR(255);
    v_id INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM app_users WHERE username = p_username) THEN
        RETURN jsonb_build_object('error', '用户名已被注册');
    END IF;
    v_salt := substring(encode(gen_random_bytes(16), 'hex') from 1 for 16);
    v_password := substring(encode(gen_random_bytes(8), 'hex') from 1 for 12);
    v_hashed := md5(v_password || v_salt);
    INSERT INTO app_users (username, password, salt, role)
    VALUES (p_username, v_hashed, v_salt, 'user')
    RETURNING id INTO v_id;
    RETURN jsonb_build_object('id', v_id, 'password', v_password);
END;
$$ LANGUAGE plpgsql;

-- 修改密码
CREATE OR REPLACE FUNCTION change_password(p_user_id INTEGER, p_old_password VARCHAR, p_new_password VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    v_user app_users%ROWTYPE;
    v_salt VARCHAR(32);
    v_hashed VARCHAR(255);
BEGIN
    SELECT * INTO v_user FROM app_users WHERE id = p_user_id;
    IF NOT FOUND OR v_user.password != md5(p_old_password || v_user.salt) THEN
        RETURN FALSE;
    END IF;
    v_salt := substring(encode(gen_random_bytes(16), 'hex') from 1 for 16);
    v_hashed := md5(v_new_password || v_salt);
    UPDATE app_users SET password = v_hashed, salt = v_salt, updated_at = NOW()
    WHERE id = p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 管理员：重置用户密码（默认 123456）
CREATE OR REPLACE FUNCTION reset_user_password(p_user_id INTEGER)
RETURNS VARCHAR(16) AS $$
DECLARE
    v_new_password VARCHAR(16) := '123456';
    v_salt VARCHAR(32);
    v_hashed VARCHAR(255);
BEGIN
    v_salt := substring(encode(gen_random_bytes(16), 'hex') from 1 for 16);
    v_hashed := md5(v_new_password || v_salt);
    UPDATE app_users SET password = v_hashed, salt = v_salt, updated_at = NOW()
    WHERE id = p_user_id;
    RETURN v_new_password;
END;
$$ LANGUAGE plpgsql;

-- 管理员：分页获取用户列表
CREATE OR REPLACE FUNCTION get_users(p_page INTEGER DEFAULT 1, p_page_size INTEGER DEFAULT 20)
RETURNS JSONB AS $$
DECLARE
    v_offset INTEGER;
    v_total INTEGER;
    v_users JSONB;
BEGIN
    v_offset := (p_page - 1) * p_page_size;
    SELECT COUNT(*) INTO v_total FROM app_users;
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'id', id, 'username', username, 'role', role, 'created_at', created_at
    ) ORDER BY created_at DESC), '[]'::JSONB)
    INTO v_users
    FROM app_users
    OFFSET v_offset LIMIT p_page_size;
    RETURN jsonb_build_object('users', v_users, 'total', v_total);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 种子数据：默认账号
-- ============================================

INSERT INTO app_users (username, password, salt, role) VALUES
    ('admin', md5('admin' || 'a1b2c3d4e5f6g7h8'), 'a1b2c3d4e5f6g7h8', 'admin'),
    ('user001', md5('123456' || 'u1u2u3u4u5u6u7u8'), 'u1u2u3u4u5u6u7u8', 'user')
ON CONFLICT (username) DO NOTHING;
