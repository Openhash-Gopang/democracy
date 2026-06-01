/**
 * pdv.js — K-Democracy PDV 기록 모듈 v1.0
 * gopang-proxy /pdv/report 엔드포인트 연동
 * school/report.js 의 sendToPDV() 패턴 준수
 */

const PROXY  = 'https://gopang-proxy.tensor-city.workers.dev';
const SVC_ID = 'democracy';

function _getUserIpv6() {
  try {
    const s = JSON.parse(sessionStorage.getItem('gopang_sso_token') || 'null');
    return s?.ipv6 || 'anonymous';
  } catch { return 'anonymous'; }
}

async function _hash(obj) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(obj)));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2,'0')).join('');
}

async function _sendToPDV(payload) {
  try {
    const res = await fetch(`${PROXY}/pdv/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ report: payload }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const ack = await res.json();
    console.info('[K-Democracy PDV] 기록 완료:', ack.pdv_entry);
    return ack;
  } catch(e) {
    console.warn('[K-Democracy PDV] 전송 실패 → 로컬 백업:', e.message);
    _backup(payload);
    return null;
  }
}

function _backup(payload) {
  try {
    const key  = 'kdemocracy_pdv_pending';
    const list = JSON.parse(localStorage.getItem(key) || '[]');
    list.push({ payload, failedAt: new Date().toISOString() });
    if (list.length > 200) list.splice(0, list.length - 200);
    localStorage.setItem(key, JSON.stringify(list));
  } catch {}
}

async function _flush() {
  try {
    const key  = 'kdemocracy_pdv_pending';
    const list = JSON.parse(localStorage.getItem(key) || '[]');
    if (!list.length) return;
    const failed = [];
    for (const item of list) {
      const ack = await _sendToPDV(item.payload);
      if (!ack) failed.push(item);
    }
    localStorage.setItem(key, JSON.stringify(failed));
  } catch {}
}

/* ═══════════════════════════════════════════ */
const PDV = {

  /** 안건 제안 기록 */
  async writePropose({ title='', category='', background='', billId='' }={}) {
    const ipv6 = _getUserIpv6();
    const now  = new Date().toISOString();
    const id   = billId || `RPT-democracy-propose-${Date.now()}`;
    return _sendToPDV({
      svc: SVC_ID, type: 'democracy_propose', id,
      content_hash: await _hash({ id, title, now }),
      who:   { ipv6, role: 'proposer', recipients: ['gopang-pdv'] },
      when:  { generated_at: now, period_start: now, period_end: now },
      where: { svc_url: 'https://democracy.gopang.net', label: '안건 게시판' },
      what:  { summary: `안건 제안: ${title}`, title, category, background: background.slice(0,300) },
      how:   { method: 'K-Democracy 안건 제안 시스템' },
      why:   { goal: '고팡 생태계 개선 제안', triggered: 'democracy_propose' },
    });
  },

  /** 동의 기록 */
  async writeAgree({ billId='', billTitle='', voteWeight=1 }={}) {
    const ipv6 = _getUserIpv6();
    const now  = new Date().toISOString();
    const id   = `RPT-democracy-agree-${Date.now()}`;
    return _sendToPDV({
      svc: SVC_ID, type: 'democracy_agree', id,
      content_hash: await _hash({ id, billId, voteWeight, now }),
      who:   { ipv6, role: 'citizen', recipients: ['gopang-pdv'] },
      when:  { generated_at: now, period_start: now, period_end: now },
      where: { svc_url: 'https://democracy.gopang.net', label: '동의 확보 게시판' },
      what:  { summary: `동의: ${billTitle}`, bill_id: billId, bill_title: billTitle, vote_weight: voteWeight },
      how:   { method: 'GDC 기반 동의 투표' },
      why:   { goal: '안건 심사 상정 동의', triggered: 'democracy_agree' },
    });
  },

  /** 하원 의결 투표 기록 */
  async writeVote({ billId='', billTitle='', side='', voteWeight=1 }={}) {
    const ipv6 = _getUserIpv6();
    const now  = new Date().toISOString();
    const id   = `RPT-democracy-vote-${Date.now()}`;
    return _sendToPDV({
      svc: SVC_ID, type: 'democracy_vote', id,
      content_hash: await _hash({ id, billId, side, voteWeight, now }),
      who:   { ipv6, role: 'voter', recipients: ['gopang-pdv'] },
      when:  { generated_at: now, period_start: now, period_end: now },
      where: { svc_url: 'https://democracy.gopang.net', label: '하원 의결' },
      what:  { summary: `하원 투표: ${side} (${voteWeight}표) — ${billTitle}`, bill_id: billId, side, vote_weight: voteWeight },
      how:   { method: 'GDC 가중 하원 의결 투표 (최대 1,000표)' },
      why:   { goal: '고팡 운영 규칙 의결', triggered: 'democracy_vote' },
      analysis: { risk_level: 'high' },
    });
  },

  /** 상원 거부권 행사 기록 */
  async writeVeto({ billId='', billTitle='', reason='' }={}) {
    const ipv6 = _getUserIpv6();
    const now  = new Date().toISOString();
    const id   = `RPT-democracy-veto-${Date.now()}`;
    return _sendToPDV({
      svc: SVC_ID, type: 'democracy_veto', id,
      content_hash: await _hash({ id, billId, reason, now }),
      who:   { ipv6, role: 'senator', recipients: ['gopang-pdv'] },
      when:  { generated_at: now, period_start: now, period_end: now },
      where: { svc_url: 'https://democracy.gopang.net', label: '상원 검토' },
      what:  { summary: `상원 거부권: ${billTitle}`, bill_id: billId, reason },
      how:   { method: '1인 1표 상원 거부권 행사' },
      why:   { goal: '대자본 독주 견제 및 평행 헌법 수호', triggered: 'democracy_veto' },
      analysis: { risk_level: 'high' },
    });
  },

  /** 의결 결과 확정 기록 */
  async writeResult({ billId='', billTitle='', result='', forPct=0, againstPct=0 }={}) {
    const ipv6 = _getUserIpv6();
    const now  = new Date().toISOString();
    const id   = `RPT-democracy-result-${Date.now()}`;
    return _sendToPDV({
      svc: SVC_ID, type: 'democracy_result', id,
      content_hash: await _hash({ id, billId, result, now }),
      who:   { ipv6, role: 'system', recipients: ['gopang-pdv'] },
      when:  { generated_at: now, period_start: now, period_end: now },
      where: { svc_url: 'https://democracy.gopang.net', label: '의결 결과' },
      what:  { summary: `의결 ${result}: ${billTitle} (찬성 ${forPct}% / 반대 ${againstPct}%)`, bill_id: billId, result, for_pct: forPct, against_pct: againstPct },
      how:   { method: '무작위 배심 의결 → 상원 검토 → 최종 확정' },
      why:   { goal: '고팡 운영 규칙 갱신', triggered: 'democracy_result' },
      analysis: { risk_level: 'high' },
    });
  },

  /** AI 상담 기록 */
  async writeConsult({ userMsg='', aiMsg='' }={}) {
    const ipv6 = _getUserIpv6();
    const now  = new Date().toISOString();
    const id   = `RPT-democracy-consult-${Date.now()}`;
    return _sendToPDV({
      svc: SVC_ID, type: 'democracy_consult', id,
      content_hash: await _hash({ id, userMsg, now }),
      who:   { ipv6, role: 'citizen', recipients: ['gopang-pdv'] },
      when:  { generated_at: now, period_start: now, period_end: now },
      where: { svc_url: 'https://democracy.gopang.net', label: 'AI 민주주의 상담' },
      what:  { summary: userMsg.slice(0,200), ai_response: aiMsg.slice(0,300) },
      how:   { method: 'K-Democracy AI 상담' },
      why:   { goal: '민주주의 참여 지원', triggered: 'democracy_consult' },
    });
  },

  flushPending: _flush,
};

window.addEventListener('load', () => setTimeout(_flush, 2000));
window.PDV = PDV;
export { PDV };
