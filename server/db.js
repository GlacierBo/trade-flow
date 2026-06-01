const { createClient } = require("@supabase/supabase-js");

// 兼容 VITE_ 前缀（用户可能直接复制了根目录的 .env）
const supabaseUrl = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL;
const supabaseKey =
  process.env.SUPABASE_KEY ||
  process.env.SUPABASE_SERVICE_KEY ||
  process.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error("缺少 Supabase 配置，请设置 SUPABASE_URL 和 SUPABASE_KEY 环境变量");
  console.error("参考 .env.example");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

module.exports = {
  async upsertStock(stock) {
    const { code, name, price, changePercent, open, high, low, yesterday, volume, amount, amplitude, turnoverRate, totalMarketCap, source } = stock;
    const { error } = await supabase.from("stocks").upsert(
      {
        code,
        name,
        price,
        changePercent,
        open,
        high,
        low,
        yesterday,
        volume,
        amount,
        amplitude,
        turnoverRate,
        totalMarketCap,
        source,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "code" }
    );
    if (error) console.error("upsertStock error:", error.message);
  },

  async getWatchlist() {
    // 获取自选列表
    const { data: items, error: e1 } = await supabase
      .from("watchlist")
      .select("code, name, added_at")
      .order("added_at");
    if (e1) throw e1;
    if (!items?.length) return [];

    // 批量关联最新行情
    const codes = items.map((i) => i.code);
    const { data: stocks, error: e2 } = await supabase
      .from("stocks")
      .select("*")
      .in("code", codes);
    if (e2) throw e2;

    const stockMap = new Map((stocks || []).map((s) => [s.code, s]));
    return items.map((item) => ({ ...item, ...(stockMap.get(item.code) || {}) }));
  },

  async addWatchlist(code, name) {
    const { error } = await supabase
      .from("watchlist")
      .upsert({ code, name }, { onConflict: "code" });
    if (error) throw error;
  },

  async removeWatchlist(code) {
    const { error } = await supabase
      .from("watchlist")
      .delete()
      .eq("code", code);
    if (error) throw error;
  },
};
