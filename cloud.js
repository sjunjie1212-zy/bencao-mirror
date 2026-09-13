/* BENCAO MIRROR — Encounter 云端同步（可选层）
 *
 * 原则：
 *   1. 本地优先：本地记录永远先写、且不受云端影响。
 *   2. 零摩擦：Supabase Anonymous Sign-in，进站即有身份。
 *   3. 诚实：老数据只按真实存在的信息导入，不编造步骤细节。
 *
 * 任何失败都不抛出、不阻塞页面。未配置或脚本加载失败 = 纯本地模式。
 */
(function () {
  'use strict';

  var LS = 'bencao:rd1';
  var CONSENT_KEY = LS + ':cloud:consent';
  var QUEUE_KEY = LS + ':cloud:pending';
  var MIGRATED_KEY = LS + ':cloud:migrated';
  var MAX_QUEUE = 200;
  var MAX_ATTEMPTS = 5;

  var cfg = window.BENCAO_CLOUD || {};
  var client = null;
  var userId = null;      // public.users.id
  var herbMap = null;     // { 'BC.001': 12 }
  var herbs = [];         // HERBS 数组（由 app.js 传入）
  var startedAt = null;
  var consentPromise = null;

  function log() {
    try { console.debug.apply(console, ['[cloud]'].concat([].slice.call(arguments))); } catch (e) {}
  }
  function uuid() {
    try { return crypto.randomUUID(); }
    catch (e) { return 'c' + Date.now() + Math.random().toString(16).slice(2); }
  }
  function available() {
    return !!(cfg.enabled && cfg.url && cfg.anonKey && window.supabase &&
              typeof window.supabase.createClient === 'function');
  }
  function readJSON(key, fallback) {
    try { var v = JSON.parse(localStorage.getItem(key) || 'null'); return v === null ? fallback : v; }
    catch (e) { return fallback; }
  }
  function writeJSON(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {}
  }

  /* ---------------- 离线队列 ---------------- */
  function queue() { var q = readJSON(QUEUE_KEY, []); return Array.isArray(q) ? q : []; }
  function saveQueue(q) {
    if (q.length > MAX_QUEUE) {
      log('queue overflow, dropping oldest', q.length - MAX_QUEUE);
      q = q.slice(-MAX_QUEUE);
    }
    writeJSON(QUEUE_KEY, q);
  }
  function enqueue(payload) {
    payload.attempts = payload.attempts || 0;
    var q = queue();
    if (payload.client_id && q.some(function (p) { return p.client_id === payload.client_id; })) return;
    q.push(payload);
    saveQueue(q);
  }

  /* ---------------- 会话 ---------------- */
  function ensureSession() {
    if (!available()) return Promise.resolve(null);
    if (client.auth.getSession) {
      return client.auth.getSession().then(function (res) {
        var session = res && res.data ? res.data.session : null;
        if (session) return session;
        return client.auth.signInAnonymously().then(function (r) {
          return r && r.data ? r.data.session : null;
        }).catch(function (e) { log('anon sign-in failed', e && e.message); return null; });
      }).catch(function (e) { log('getSession failed', e && e.message); return null; });
    }
    return Promise.resolve(null);
  }

  function ensureUser() {
    if (userId) return Promise.resolve(userId);
    return client.from('users').select('id').limit(1).then(function (res) {
      if (res.error) { log('users select', res.error.message); return null; }
      if (res.data && res.data.length) { userId = res.data[0].id; return userId; }
      // 触发器未装时的兜底：插入自己那一行（RLS: users_self_insert）
      return client.auth.getUser().then(function (u) {
        var authUid = u && u.data && u.data.user ? u.data.user.id : null;
        if (!authUid) return null;
        return client.from('users')
          .insert({ auth_uid: authUid, nickname: null })
          .select('id').then(function (ins) {
            if (ins.error) { log('users insert', ins.error.message); return null; }
            userId = ins.data && ins.data[0] ? ins.data[0].id : null;
            return userId;
          });
      });
    });
  }

  function loadHerbMap() {
    if (herbMap) return Promise.resolve(herbMap);
    return client.from('herbs').select('id,code').then(function (res) {
      if (res.error) { log('herbs select', res.error.message); return null; }
      herbMap = {};
      (res.data || []).forEach(function (r) { herbMap[r.code] = r.id; });
      return herbMap;
    });
  }

  /* ---------------- 同意 ---------------- */
  function consentState() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }
  function askConsent() {
    return new Promise(function (resolve) {
      var dlg = document.getElementById('cloudDialog');
      if (!dlg) { resolve(false); return; }
      var settled = false;
      function done(ok) {
        if (settled) return;
        settled = true;
        try { localStorage.setItem(CONSENT_KEY, ok ? (cfg.consentVersion || 'v1') : 'declined'); } catch (e) {}
        cleanup();
        resolve(ok);
      }
      function onYes() { done(true); }
      function onNo() { done(false); }
      function onCancel() { done(false); }   // Esc / 关闭 = 暂不用
      function cleanup() {
        var y = dlg.querySelector('[data-cloud-consent-yes]');
        var n = dlg.querySelector('[data-cloud-consent-no]');
        if (y) y.removeEventListener('click', onYes);
        if (n) n.removeEventListener('click', onNo);
        dlg.removeEventListener('cancel', onCancel);
        dlg.removeEventListener('close', onCancel);
        try { dlg.close(); } catch (e) {}
      }
      var yes = dlg.querySelector('[data-cloud-consent-yes]');
      var no = dlg.querySelector('[data-cloud-consent-no]');
      if (yes) yes.addEventListener('click', onYes);
      if (no) no.addEventListener('click', onNo);
      dlg.addEventListener('cancel', onCancel);
      dlg.addEventListener('close', onCancel);
      try { dlg.showModal(); } catch (e) { resolve(false); }
    });
  }
  function ensureConsent() {
    if (!available()) return Promise.resolve(false);
    var st = consentState();
    if (st && st !== 'declined') return Promise.resolve(true);
    if (st === 'declined') return Promise.resolve(false);
    if (consentPromise) return consentPromise;
    consentPromise = askConsent().then(function (ok) { consentPromise = null; return ok; });
    return consentPromise;
  }

  /* ---------------- 步骤映射 ---------------- */
  function buildObservations(values) {
    var v = values || {};
    var out = [];
    if (v.look) out.push({ step: 'look', dimension: 'see', value: { choice: v.look } });
    if (v.touch) out.push({ step: 'touch', dimension: 'touch', value: { choice: v.touch } });
    if (v.smell1confirm) out.push({ step: 'smell_first', dimension: 'smell', value: { confirmed: true } });
    if (v.first) out.push({ step: 'smell_first', dimension: 'smell', value: { first: v.first } });
    if (v.assoc) out.push({ step: 'smell_first', dimension: 'smell', value: { assoc: v.assoc } });
    if (v.smell2confirm) out.push({ step: 'smell_second', dimension: 'smell', value: { confirmed: true } });
    if (v.compare) out.push({ step: 'compare', dimension: 'compare', value: { choice: v.compare } });
    var raw = String(v.raw_note || '').trim();
    if (raw) out.push({ step: 'leave', dimension: 'compare', value: {}, raw_note: raw.slice(0, 160) });
    return out;
  }

  /* ---------------- 上传 ---------------- */
  function uploadOne(payload) {
    return ensureUser().then(function (uid) {
      if (!uid) throw new Error('no user row');
      return loadHerbMap().then(function (map) {
        if (!map) throw new Error('no herb map');
        var herbId = map[payload.code];
        if (!herbId) throw new Error('herb not in cloud: ' + payload.code);
        var row = {
          user_id: uid,
          herb_id: herbId,
          material_source: payload.material_source || 'unknown',
          started_at: payload.started_at,
          completed_at: payload.completed_at,
          device: (payload.device || '').slice(0, 120),
          app_version: payload.app_version || cfg.appVersion || '',
          client_id: payload.client_id,
          is_public: false
        };
        return client.from('encounters').insert(row).select('id').then(function (ins) {
          if (ins.error) {
            if (ins.error.code === '23505') {   // 已存在（幂等）
              return client.from('encounters').select('id').eq('client_id', payload.client_id).limit(1)
                .then(function (s) { return s.data && s.data[0] ? s.data[0].id : null; });
            }
            throw new Error(ins.error.message);
          }
          return ins.data && ins.data[0] ? ins.data[0].id : null;
        }).then(function (encId) {
          if (!encId) return null;
          var obs = (payload.observations || []).map(function (o) {
            return { encounter_id: encId, step: o.step, dimension: o.dimension, value: o.value || {}, raw_note: o.raw_note || null };
          });
          var chain = obs.length
            ? client.from('encounter_observations').insert(obs)
            : Promise.resolve({});
          return Promise.resolve(chain).then(function (r) {
            if (r && r.error) log('observations insert', r.error.message);
            return client.from('user_herb_profile').upsert({
              user_id: uid,
              herb_id: herbId,
              encounter_count: payload.count || 1,
              first_at: payload.started_at,
              last_at: payload.completed_at,
              latest_note: payload.latest_note || null
            }, { onConflict: 'user_id,herb_id' });
          });
        });
      });
    });
  }

  function flush() {
    if (!available() || !consentedNow()) return Promise.resolve();
    var q = queue();
    if (!q.length) return Promise.resolve();
    var remaining = [];
    var chain = Promise.resolve();
    q.forEach(function (payload) {
      chain = chain.then(function () {
        return uploadOne(payload).catch(function (e) {
          payload.attempts = (payload.attempts || 0) + 1;
          if (payload.attempts < MAX_ATTEMPTS) remaining.push(payload);
          else log('dropping payload after max attempts', payload.client_id, e && e.message);
        });
      });
    });
    return chain.then(function () { saveQueue(remaining); });
  }
  function consentedNow() {
    var st = consentState();
    return !!(st && st !== 'declined');
  }

  /* ---------------- 对外 API ---------------- */
  function beginEncounter() {
    startedAt = new Date().toISOString();
  }

  function submitEncounter(herb, values, count) {
    if (!available()) return;
    ensureSession().then(function () {
      return ensureConsent();
    }).then(function (ok) {
      if (!ok) return;
      var now = new Date().toISOString();
      var raw = String((values && values.raw_note) || '').trim();
      enqueue({
        client_id: uuid(),
        code: herb.no,
        material_source: 'mine',
        started_at: startedAt || now,
        completed_at: now,
        device: (navigator.userAgent || ''),
        app_version: cfg.appVersion,
        count: count || 1,
        latest_note: raw ? raw.slice(0, 160) : null,
        observations: buildObservations(values)
      });
      startedAt = null;
      flush();
    }).catch(function (e) { log('submit failed', e && e.message); });
  }

  // 老数据导入：每味只导 1 条，device 标记 legacy，不伪造步骤历史
  function migrateLegacy() {
    if (!available()) return;
    try { if (localStorage.getItem(MIGRATED_KEY)) return; } catch (e) { return; }
    ensureSession().then(function () {
      var last = {};
      var total = 0;
      var list = Array.isArray(herbs) ? herbs : [];
      list.forEach(function (h) {
        var c = 0;
        try { c = Number(localStorage.getItem(LS + ':' + h.id + ':count') || 0); } catch (e) {}
        if (!c) return;
        var vals = readJSON(LS + ':' + h.id + ':last', null);
        if (!vals) return;
        total += c;
        last[h.id] = { herb: h, count: c, values: vals };
      });
      if (!total) { writeJSON(MIGRATED_KEY, true); return; }
      ensureConsent().then(function (ok) {
        if (!ok) return;
        Object.keys(last).forEach(function (k) {
          var item = last[k];
          var now = new Date().toISOString();
          enqueue({
            client_id: uuid(),
            code: item.herb.no,
            material_source: 'unknown',
            started_at: now,
            completed_at: now,
            device: 'legacy-localStorage',
            app_version: cfg.appVersion,
            count: item.count,
            latest_note: String(item.values.raw_note || '').trim().slice(0, 160) || null,
            observations: buildObservations(item.values)
          });
        });
        writeJSON(MIGRATED_KEY, true);
        flush();
        log('legacy migrated for', Object.keys(last).length, 'herbs');
      });
    }).catch(function (e) { log('migrate failed', e && e.message); });
  }

  function init(options) {
    herbs = (options && options.herbs) || [];
    if (!available()) { log('cloud disabled (local-only mode)'); return; }
    try {
      client = window.supabase.createClient(cfg.url, cfg.anonKey, {
        auth: { persistSession: true, autoRefreshToken: true }
      });
    } catch (e) { log('client init failed', e && e.message); return; }
    window.addEventListener('online', function () { flush(); });
    ensureSession().then(function () {
      if (consentedNow()) { migrateLegacy(); flush(); }
    }).catch(function (e) { log('init session', e && e.message); });
  }

  window.Cloud = {
    init: init,
    beginEncounter: beginEncounter,
    submitEncounter: submitEncounter,
    flush: flush,
    available: available
  };
})();
