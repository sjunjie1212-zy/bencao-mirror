/* BENCAO MIRROR — 云端配置（公开文件）
 *
 * anon key 按设计就是公开的，安全性由数据库 RLS 保证。
 * service_role key 绝不允许出现在前端或本仓库。
 *
 * enabled 为 false 时，站点完全按本地模式运行（不联网、不上传）。
 */
window.BENCAO_CLOUD = {
  enabled: false,                       // 填好 url / anonKey 后改为 true
  url: 'https://REPLACE-ME.supabase.co',
  anonKey: 'REPLACE-ME-ANON-KEY',
  consentVersion: '2026-09-13-v1',
  appVersion: '3.6.5-VF1'
};
