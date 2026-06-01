const { createClient } = require("@supabase/supabase-js");

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
  // 插入一条行情记录
  async insertStock(stock) {
    const { code, name, price, changePercent, open, high, low, yesterday, volume, amount, amplitude, turnoverRate, totalMarketCap, source } = stock;
    const { error } = await supabase.from("fnos_stocks").insert({
      code, name, price, changePercent, open, high, low, yesterday,
      volume, amount, amplitude, turnoverRate, totalMarketCap, source,
    });
    if (error) console.error("insertStock error:", error.message);
  },

  // 获取某只股票的最新行情
  async getLatestStock(code) {
    const { data, error } = await supabase
      .from("fnos_stocks")
      .select("*")
      .eq("code", code)
      .order("created_at", { ascending: false })
      .limit(1);
    if (error) throw error;
    return data?.[0] || null;
  },

  // 获取自选列表（含最新行情）
  async getWatchlist() {
    const { data: items, error: e1 } = await supabase
      .from("fnos_watchlist")
      .select("code, name, added_at")
      .order("added_at");
    if (e1) throw e1;
    if (!items?.length) return [];

    // 每个自选关联最新一条行情
    const { data: stocks, error: e2 } = await supabase
      .from("fnos_stocks")
      .select("*")
      .in("code", items.map((i) => i.code))
      .order("created_at", { ascending: false });
    if (e2) throw e2;

    // 取每个 code 的最新一条
    const latest = new Map();
    for (const s of stocks || []) {
      if (!latest.has(s.code)) latest.set(s.code, s);
    }
    return items.map((item) => ({ ...item, ...(latest.get(item.code) || {}) }));
  },

  async addWatchlist(code, name) {
    const { error } = await supabase
      .from("fnos_watchlist")
      .upsert({ code, name }, { onConflict: "code" });
    if (error) throw error;
  },

  async removeWatchlist(code) {
    const { error } = await supabase
      .from("fnos_watchlist")
      .delete()
      .eq("code", code);
    if (error) throw error;
  },

  async getWatchlistCodes() {
    const { data, error } = await supabase
      .from("fnos_watchlist")
      .select("code, name");
    if (error) throw error;
    return data || [];
  },
};
