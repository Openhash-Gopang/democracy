#!/usr/bin/env python3
"""
fix_desktop_dawn_live_bulletin.py

대상 저장소: democracy
목적: desktop.html(K-Democracy 메인 UI)의 "안건 제안·동의·투표"가 지금까지
      제안자 개인의 PDV에만 기록되고 다른 사용자에게 전혀 보이지 않았는데,
      UI는 "게재됐다"·"동의하였다"고 안내하며 안건 목록도 전부 하드코딩된
      샘플 데이터였다. 이 패치는:
        1) 안건 목록을 worker.js(/democracy/proposals)에서 실제로 fetch해
           렌더링하도록 바꾼다(하드코딩 샘플 5건 제거).
        2) "안건 게재하기"가 /democracy/proposal에 실제로 POST하도록 바꾼다
           (PDV 기록은 개인 감사 로그로 계속 병행 — 제거하지 않음).
        3) "동의하기"가 /democracy/endorse에 실제로 POST하도록 바꾼다
           (동의 수 합산은 서버가 하고, 임계치 도달 시 서버가 자동으로
           status='voting'으로 전환한다).
        4) "찬성/반대"가 /democracy/vote에 실제로 POST하도록 바꾼다.
        5) "의결 참여" 패널의 가짜 배심원·247표 시나리오(AI 산정 가중
           투표권·무작위 배심원 선정은 이번 구현 범위 밖 — 백엔드 쪽
           worker.js 패치 주석과 동일 고지)를 정직한 안내문으로 교체한다.
        6) "심사 중" 필터를 제거한다 — 이번 파이프라인은 동의 임계치
           달성 시 곧바로 투표로 넘어가고 별도 심사 단계가 없다.

선행 조건: gopang 저장소에 worker.js DAWN 엔드포인트 패치
          (fix_worker_dawn_public_bulletin.py)와 pb_migrations 3종이
          먼저 배포돼 있어야 한다.

실행 위치: democracy 저장소 루트 (desktop.html이 있는 폴더)
"""
import sys

TARGET = "desktop.html"


def replace_unique(content, old, new, label):
    count = content.count(old)
    if count == 0:
        if new in content:
            print(f"[{label}] 이미 적용된 상태로 보입니다. 건너뜁니다.")
            return content, True
        print(f"오류[{label}]: 대상 문자열을 찾지 못했습니다. desktop.html이 예상과 다르게 변경됐을 수 있습니다.")
        sys.exit(1)
    if count != 1:
        print(f"오류[{label}]: 대상 문자열이 {count}번 발견됐습니다(1번이어야 안전). 수동 확인이 필요합니다.")
        sys.exit(1)
    return content.replace(old, new, 1), False


# ── 패치 1: 필터바에서 "심사 중" 버튼 제거 ───────────────────────
P1_OLD = """        <button class="f-btn" onclick="filterBills('petition',this)">동의 확보 중</button>
        <button class="f-btn" onclick="filterBills('review',this)">심사 중</button>
        <button class="f-btn" onclick="filterBills('vote',this)">의결 중</button>"""
P1_NEW = """        <button class="f-btn" onclick="filterBills('petition',this)">동의 확보 중</button>
        <button class="f-btn" onclick="filterBills('vote',this)">의결 중</button>"""


# ── 패치 2: 하드코딩 샘플 안건 5건을 로딩 안내로 교체 ─────────────
P2_OLD = """      <div id="bills-list">

        <div class="bill-card" data-status="vote">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div class="bill-title">고팡 거래 수수료를 0.2%에서 0.15%로 인하 제안</div>
            <span class="badge b-proc">🗳️ 의결 중</span>
          </div>
          <div class="bill-meta">
            <span>경제</span><span>·</span><span>제안자: 김○○</span><span>·</span><span>2026.05.28</span>
          </div>
          <div style="font-size:12px;color:var(--txt3);margin-bottom:10px">찬성 62% · 반대 38% · 잔여 3일</div>
          <div class="vote-bar"><div class="vote-for" style="width:62%"></div><div class="vote-against" style="width:38%"></div></div>
          <div class="bill-actions">
            <button class="b-btn b-btn-for" onclick="castVote(this,'찬성')">✓ 찬성</button>
            <button class="b-btn b-btn-against" onclick="castVote(this,'반대')">✗ 반대</button>
            <button class="b-btn-detail" onclick="showBillDetail('수수료 인하')">상세</button>
          </div>
        </div>

        <div class="bill-card" data-status="vote">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div class="bill-title">AI 서버 주요 칩 H200 → 화웨이 어센드 910C 변경 제안</div>
            <span class="badge b-proc">🗳️ 의결 중</span>
          </div>
          <div class="bill-meta"><span>인프라</span><span>·</span><span>제안자: 이○○</span><span>·</span><span>2026.05.25</span></div>
          <div style="font-size:12px;color:var(--txt3);margin-bottom:10px">찬성 44% · 반대 56% · 잔여 5일</div>
          <div class="vote-bar"><div class="vote-for" style="width:44%"></div><div class="vote-against" style="width:56%"></div></div>
          <div class="bill-actions">
            <button class="b-btn b-btn-for" onclick="castVote(this,'찬성')">✓ 찬성</button>
            <button class="b-btn b-btn-against" onclick="castVote(this,'반대')">✗ 반대</button>
            <button class="b-btn-detail" onclick="showBillDetail('칩 교체')">상세</button>
          </div>
        </div>

        <div class="bill-card" data-status="review">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div class="bill-title">각 지역별 소규모 서버 클러스터 설립 제안</div>
            <span class="badge b-blue">📋 심사 중</span>
          </div>
          <div class="bill-meta"><span>인프라</span><span>·</span><span>제안자: 박○○</span><span>·</span><span>2026.05.20</span></div>
          <div style="font-size:12px;color:var(--txt3);margin-bottom:10px">찬반 공방 진행 중 · 댓글 48개</div>
          <div class="bill-actions">
            <button class="b-btn b-btn-for" style="flex:2" onclick="toast('💬 토론 게시판으로 이동합니다.')">💬 토론 참여</button>
            <button class="b-btn-detail" onclick="showBillDetail('서버 클러스터')">상세</button>
          </div>
        </div>

        <div class="bill-card" data-status="petition">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div class="bill-title">형사규칙 제3조 개정 — 디지털 사기 처벌 강화</div>
            <span class="badge b-wait">📣 동의 확보 중</span>
          </div>
          <div class="bill-meta"><span>규칙</span><span>·</span><span>제안자: 최○○</span><span>·</span><span>2026.05.31</span></div>
          <div style="font-size:12px;color:var(--txt3);margin-bottom:6px">340 / 1,000표 동의 확보</div>
          <div class="bill-progress"><div class="bill-fill" style="width:34%;background:var(--vi)"></div></div>
          <div class="bill-actions">
            <button class="b-btn b-btn-for" style="flex:2" onclick="if(window.PDV)PDV.writeAgree({billId:'bill-003',billTitle:'형사규칙 제3조 개정',voteWeight:247});toast('✅ 동의하였습니다. PDV에 기록됩니다.')">👍 동의하기</button>
            <button class="b-btn-detail" onclick="showBillDetail('형사규칙 개정')">상세</button>
          </div>
        </div>

        <div class="bill-card" data-status="passed">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div class="bill-title">GDC 스테이킹 연 이자율 3% → 4% 상향 조정</div>
            <span class="badge b-ok">✅ 가결 · 시행 중</span>
          </div>
          <div class="bill-meta"><span>경제</span><span>·</span><span>2026.04.15 의결</span><span>·</span><span>찬성 71%</span></div>
          <div style="font-size:12px;color:var(--txt3)">집행부 통과 · 2026.05.01부터 시행 · PDV 기록 완료</div>
        </div>

      </div>"""
P2_NEW = """      <div id="bills-list">
        <div style="padding:24px;text-align:center;color:var(--txt3);font-size:13px">안건을 불러오는 중…</div>
      </div>"""


# ── 패치 3: "의결 참여" 패널의 가짜 배심원·247표 시나리오를 정직한 안내로 교체 ──
P3_OLD = """  <!-- ════ 의결 참여 ════ -->
  <div class="panel" id="p-vote">
    <div class="ph">
      <div class="ph-badge">의결 참여</div>
      <div class="ph-title">현재 의결 진행 중인 안건</div>
      <div class="ph-sub">무작위 배심원으로 선정된 경우 아래에서 투표합니다. AI 산정 투표권 비례로 행사됩니다.</div>
    </div>
    <div class="panel-body">
      <div class="card" style="border:1.5px solid var(--vi);margin-bottom:14px">
        <div class="card-hd"><span class="card-hd-t">🗳️ 배심원 선정 안내</span><span class="badge b-proc">선정됨</span></div>
        <div class="card-bd">
          <div style="font-size:13px;color:var(--txt2);line-height:1.8;margin-bottom:12px">
            안건 <strong>「고팡 거래 수수료 0.2% → 0.15% 인하」</strong>의 배심원으로 무작위 선정됐습니다.<br>
            귀하의 현재 투표권: <strong style="color:var(--vi)">247표</strong> (GDC 사용 120 + 코드 공헌 80 + 준법 47)
          </div>
          <div style="background:#f8f9fa;border-radius:9px;padding:14px;margin-bottom:14px">
            <div style="font-size:11px;font-weight:700;color:var(--txt3);text-transform:uppercase;letter-spacing:.4px;margin-bottom:10px">찬성 측 핵심 논거</div>
            <div style="font-size:13px;color:#374151;margin-bottom:10px">① 수수료 0.05%p 인하 시 연간 거래량 약 8% 증가 예상 (탄력성 분석)<br>② GDC 생태계 확장으로 장기적 수익 구조 강화<br>③ 경쟁 플랫폼 대비 수수료 경쟁력 확보</div>
            <div style="font-size:11px;font-weight:700;color:var(--txt3);text-transform:uppercase;letter-spacing:.4px;margin-bottom:10px">반대 측 핵심 논거</div>
            <div style="font-size:13px;color:#374151">① 인프라 운영비 충당에 차질 발생 우려<br>② 현 시점 유동성 비율 고려 시 시기상조<br>③ 추가 분석 후 재논의 필요</div>
          </div>
          <div style="display:flex;gap:10px">
            <button style="flex:3;padding:12px;border-radius:9px;background:var(--vi);color:#fff;font-size:14px;font-weight:800;border:none;cursor:pointer" onclick="submitVote('찬성')">✓ 찬성 (247표 행사)</button>
            <button style="flex:2;padding:12px;border-radius:9px;background:transparent;border:1.5px solid var(--border);color:#374151;font-size:14px;font-weight:700;cursor:pointer" onclick="submitVote('반대')">✗ 반대</button>
            <button style="flex:1;padding:12px;border-radius:9px;background:transparent;border:1.5px solid var(--border);color:var(--txt3);font-size:14px;cursor:pointer" onclick="submitVote('기권')">— 기권</button>
          </div>
        </div>
      </div>
    </div>
  </div>"""
P3_NEW = """  <!-- ════ 의결 참여 ════ -->
  <div class="panel" id="p-vote">
    <div class="ph">
      <div class="ph-badge">의결 참여</div>
      <div class="ph-title">현재 의결 진행 중인 안건</div>
      <div class="ph-sub">동의 임계치를 확보해 정식 회부된 안건은 누구나 찬반 투표에 참여할 수 있습니다.</div>
    </div>
    <div class="panel-body">
      <!-- 2026-07-26 정정: 무작위 배심원 선정·AI 산정 가중 투표권(GDC
           사용량·코드 공헌·K-Law 준법 등)은 아직 구현되지 않았다. 이전엔
           "247표 배심원으로 선정됐다"는 고정 문구가 항상 표시돼 실제
           동작하지 않는 기능을 동작하는 것처럼 보여줬다 — 정직하게
           고친다. 실제 투표는 "안건 목록" 탭의 의결 중(voting) 안건에서
           1인 1표로 이뤄진다. -->
      <div class="card" style="margin-bottom:14px">
        <div class="card-hd"><span class="card-hd-t">🗳️ 투표 방법 안내</span></div>
        <div class="card-bd">
          <div style="font-size:13px;color:var(--txt2);line-height:1.8;margin-bottom:14px">
            동의 1,000표를 확보해 정식 회부된 안건은 <strong>「안건 목록」</strong> 탭에
            "🗳️ 의결 중"으로 표시됩니다. 해당 안건 카드에서 직접 찬성·반대를
            선택하면 투표가 집계됩니다(1인 1표, 1안건당 1회).<br><br>
            무작위 배심원 선정과 AI 산정 가중 투표권(GDC 사용량·코드 공헌·K-Law
            준법 수준 등 다각도 반영, 최대 1,000표) 시스템은 아직 개발되지
            않았습니다 — 지금은 참여하는 모든 시민이 동일하게 1표씩 행사합니다.
          </div>
          <button style="padding:12px 20px;border-radius:9px;background:var(--vi);color:#fff;font-size:14px;font-weight:800;border:none;cursor:pointer" onclick="show('bills',document.querySelector('.sb-item[onclick*=bills]'))">안건 목록에서 투표하기 →</button>
        </div>
      </div>
    </div>
  </div>"""


# ── 패치 4: submitBill()을 실제 백엔드 POST로 교체 ────────────────
P4_OLD = """function submitBill() {
  const idea = document.getElementById('bill-idea-input')?.value?.trim();
  const category = generatedBill?.category_tag || '';
  const title = generatedBill?.title || idea || '(제목 없음)';
  if (!idea) { toast('⚠️ 제안 내용을 먼저 입력해 주세요.'); return; }
  if (window.PDV) PDV.writePropose({
    title,
    category,
    background: generatedBill?.background || idea,
    summary: generatedBill?.summary || '',
    rationality: generatedBill?.rationality_score || ''
  });
  toast('✅ 안건이 게재됐습니다. 1,000표 동의를 확보하면 심사 게시판에 상정됩니다. PDV에 기록됩니다.');
  resetPropose();
  document.getElementById('bill-idea-input').value = '';
  attachedFiles = [];
  renderAttachPreview();
}"""
P4_NEW = """async function submitBill() {
  const idea = document.getElementById('bill-idea-input')?.value?.trim();
  const category = generatedBill?.category_tag || '';
  const title = generatedBill?.title || idea || '(제목 없음)';
  if (!idea) { toast('⚠️ 제안 내용을 먼저 입력해 주세요.'); return; }

  const btn = document.querySelector('.ai-foot-go');
  if (btn) { btn.disabled = true; btn.textContent = '게재 중…'; }

  // 2026-07-26: 실제 공중 게시판(worker.js /democracy/proposal)에 게재한다.
  // PDV 개인 기록은 감사용으로 계속 병행한다(제거하지 않음) — 다만 이제는
  // 이게 "유일한 기록"이 아니라 "본인용 사본"이라는 게 명확해졌다.
  const result = await _dawnFetch('/democracy/proposal', {
    method: 'POST',
    body: JSON.stringify({
      guid: _dawnGuid(),
      title,
      category,
      background: generatedBill?.background || idea,
      summary: generatedBill?.summary || '',
    }),
  });

  if (window.PDV) PDV.writePropose({
    title,
    category,
    background: generatedBill?.background || idea,
    summary: generatedBill?.summary || '',
    rationality: generatedBill?.rationality_score || ''
  });

  if (btn) { btn.disabled = false; btn.textContent = '안건 게재하기'; }

  if (!result) {
    toast('⚠️ 게재에 실패했습니다(네트워크 오류). PDV에는 기록됐습니다. 잠시 후 다시 시도해 주세요.');
    return;
  }

  toast('✅ 안건이 공개 게시판에 게재됐습니다. 1,000표 동의를 확보하면 투표 단계로 회부됩니다.');
  resetPropose();
  document.getElementById('bill-idea-input').value = '';
  attachedFiles = [];
  renderAttachPreview();
  loadDawnProposals();
}"""


# ── 패치 5: filterBills 함수 뒤에 DAWN 실시간 연동 코드 블록 삽입 ──
P5_OLD = """function filterBills(status, btn) {
  document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  document.querySelectorAll('#bills-list .bill-card').forEach(c => {
    c.style.display = (status === 'all' || c.dataset.status === status) ? '' : 'none';
  });
}"""
P5_NEW = P5_OLD + """

// ═══════════════════════════════════════════════════════════
// DAWN 안건 공중 게시판 — 실시간 연동 (2026-07-26 신설)
// worker.js(/democracy/*)가 실제 저장소(dawn_proposals 등)를 관리한다.
// 자세한 스코프 축소 고지는 gopang/worker.js의 동일 섹션 주석 참고
// (AI 배심원 심의·가중 투표권 미구현, 1인 1가중치 고정, 투표기간 7일).
// ═══════════════════════════════════════════════════════════
const DAWN_API = DEEPSEEK_PROXY; // 같은 worker.js를 쓴다(별도 배포 아님)

function _escHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function _dawnGuid() {
  // pdv.js의 _getUserIpv6()와 동일한 세션 식별자를 재사용한다(이 파일은
  // pdv.js를 <script> 태그로만 포함하고 있어 내부 private 함수를 직접
  // import할 수 없어 동일 로직을 그대로 둔다).
  try {
    const s = JSON.parse(sessionStorage.getItem('gopang_sso_token') || 'null');
    return s?.ipv6 || 'anonymous';
  } catch { return 'anonymous'; }
}

async function _dawnFetch(path, opts = {}) {
  try {
    const res = await fetch(DAWN_API + path, {
      headers: { 'Content-Type': 'application/json' },
      ...opts,
    });
    const data = await res.json().catch(() => null);
    if (!res.ok) {
      console.warn('[DAWN]', path, res.status, data);
      return { __error: true, status: res.status, data };
    }
    return data;
  } catch (e) {
    console.warn('[DAWN] 네트워크 오류:', path, e.message);
    return null;
  }
}

function _dawnDaysLeft(closesAt) {
  if (!closesAt) return null;
  const ms = new Date(closesAt).getTime() - Date.now();
  return Math.max(0, Math.ceil(ms / 86400000));
}

function _dawnStatusBadge(p) {
  if (p.status === 'pending_endorsement') return '<span class="badge b-wait">📣 동의 확보 중</span>';
  if (p.status === 'voting') return '<span class="badge b-proc">🗳️ 의결 중</span>';
  if (p.status === 'passed') return '<span class="badge b-ok">✅ 가결</span>';
  if (p.status === 'rejected') return '<span class="badge b-wait">❌ 부결</span>';
  return '';
}

function _dawnFilterKey(status) {
  // filterBills()의 data-status 값과 매핑(petition/vote/passed/rejected)
  if (status === 'pending_endorsement') return 'petition';
  if (status === 'voting') return 'vote';
  return status; // passed, rejected는 그대로
}

function renderBillsList(proposals) {
  const wrap = document.getElementById('bills-list');
  if (!proposals || proposals.length === 0) {
    wrap.innerHTML = '<div style="padding:24px;text-align:center;color:var(--txt3);font-size:13px">아직 게재된 안건이 없습니다. 「안건 제안」에서 첫 안건을 올려보세요.</div>';
    return;
  }
  wrap.innerHTML = proposals.map((p) => {
    const created = p.created_at ? new Date(p.created_at).toLocaleDateString('ko-KR') : '';
    let body = '';
    if (p.status === 'pending_endorsement') {
      const pct = Math.min(100, Math.round(((p.endorsement_weight_total || 0) / (p.endorsement_threshold || 1000)) * 100));
      body = `
        <div style="font-size:12px;color:var(--txt3);margin-bottom:6px">${p.endorsement_weight_total || 0} / ${p.endorsement_threshold || 1000}표 동의 확보</div>
        <div class="bill-progress"><div class="bill-fill" style="width:${pct}%;background:var(--vi)"></div></div>
        <div class="bill-actions">
          <button class="b-btn b-btn-for" style="flex:2" data-dawn-endorse="${p.id}">👍 동의하기</button>
          <button class="b-btn-detail" data-dawn-detail="${p.id}">상세</button>
        </div>`;
    } else if (p.status === 'voting') {
      const total = (p.vote_for_weight || 0) + (p.vote_against_weight || 0);
      const forPct = total > 0 ? Math.round((p.vote_for_weight / total) * 100) : 50;
      const againstPct = 100 - forPct;
      const daysLeft = _dawnDaysLeft(p.vote_closes_at);
      body = `
        <div style="font-size:12px;color:var(--txt3);margin-bottom:10px">찬성 ${forPct}% · 반대 ${againstPct}%${daysLeft != null ? ' · 잔여 ' + daysLeft + '일' : ''}</div>
        <div class="vote-bar"><div class="vote-for" style="width:${forPct}%"></div><div class="vote-against" style="width:${againstPct}%"></div></div>
        <div class="bill-actions">
          <button class="b-btn b-btn-for" data-dawn-vote="${p.id}" data-dawn-side="for">✓ 찬성</button>
          <button class="b-btn b-btn-against" data-dawn-vote="${p.id}" data-dawn-side="against">✗ 반대</button>
          <button class="b-btn-detail" data-dawn-detail="${p.id}">상세</button>
        </div>`;
    } else {
      const total = (p.vote_for_weight || 0) + (p.vote_against_weight || 0);
      const forPct = total > 0 ? Math.round((p.vote_for_weight / total) * 100) : 0;
      body = `<div style="font-size:12px;color:var(--txt3)">찬성 ${forPct}% · ${p.decided_at ? new Date(p.decided_at).toLocaleDateString('ko-KR') + ' 확정' : ''}</div>`;
    }
    return `
        <div class="bill-card" data-status="${_dawnFilterKey(p.status)}" data-dawn-id="${p.id}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
            <div class="bill-title">${_escHtml(p.title)}</div>
            ${_dawnStatusBadge(p)}
          </div>
          <div class="bill-meta"><span>${_escHtml(p.category || '기타')}</span><span>·</span><span>${created}</span></div>
          ${body}
        </div>`;
  }).join('');
}

async function loadDawnProposals() {
  const data = await _dawnFetch('/democracy/proposals');
  if (!data || data.__error) {
    document.getElementById('bills-list').innerHTML = '<div style="padding:24px;text-align:center;color:var(--txt3);font-size:13px">안건을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div>';
    return;
  }
  renderBillsList(data.proposals || []);
}

// 안건 목록 패널 안의 동의/투표/상세 버튼은 매번 새로 렌더링되므로
// 이벤트 위임(delegation)으로 한 번만 리스너를 건다.
document.getElementById('bills-list')?.addEventListener('click', async (e) => {
  const endorseBtn = e.target.closest('[data-dawn-endorse]');
  if (endorseBtn) {
    endorseBtn.disabled = true;
    const result = await _dawnFetch('/democracy/endorse', {
      method: 'POST',
      body: JSON.stringify({ guid: _dawnGuid(), proposal_id: endorseBtn.dataset.dawnEndorse }),
    });
    if (!result || result.__error) {
      toast('⚠️ 동의 처리에 실패했습니다. 잠시 후 다시 시도해 주세요.');
      endorseBtn.disabled = false;
      return;
    }
    if (result.status === 'already_endorsed') {
      toast('이미 동의하신 안건입니다.');
    } else if (result.status === 'advanced_to_voting') {
      toast('✅ 동의하였습니다. 1,000표를 달성해 투표 단계로 회부됐습니다!');
    } else {
      toast('✅ 동의하였습니다.');
    }
    loadDawnProposals();
    return;
  }

  const voteBtn = e.target.closest('[data-dawn-vote]');
  if (voteBtn) {
    voteBtn.disabled = true;
    const result = await _dawnFetch('/democracy/vote', {
      method: 'POST',
      body: JSON.stringify({ guid: _dawnGuid(), proposal_id: voteBtn.dataset.dawnVote, side: voteBtn.dataset.dawnSide }),
    });
    if (!result || result.__error) {
      toast('⚠️ 투표 처리에 실패했습니다. 잠시 후 다시 시도해 주세요.');
      voteBtn.disabled = false;
      return;
    }
    if (result.status === 'already_voted') {
      toast('이미 투표하신 안건입니다.');
    } else {
      toast(`🗳️ ${voteBtn.dataset.dawnSide === 'for' ? '찬성' : '반대'} 투표 완료.`);
    }
    loadDawnProposals();
    return;
  }

  const detailBtn = e.target.closest('[data-dawn-detail]');
  if (detailBtn) showBillDetail(detailBtn.dataset.dawnDetail);
});"""


# ── 패치 6: show('bills') 진입 시 실시간 데이터 로드 ───────────────
P6_OLD = """function show(id, btn) {
  document.querySelectorAll('.panel,.chat-panel').forEach(p => p.classList.remove('active'));
  const el = document.getElementById('p-' + id);
  if (el) el.classList.add('active');
  document.querySelectorAll('.sb-item').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  document.getElementById('topbar-title').textContent = TITLES[id] || '';
}"""
P6_NEW = """function show(id, btn) {
  document.querySelectorAll('.panel,.chat-panel').forEach(p => p.classList.remove('active'));
  const el = document.getElementById('p-' + id);
  if (el) el.classList.add('active');
  document.querySelectorAll('.sb-item').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  document.getElementById('topbar-title').textContent = TITLES[id] || '';
  if ((id === 'bills' || id === 'vote') && typeof loadDawnProposals === 'function') loadDawnProposals();
}"""


# ── 패치 7: showBillDetail을 실제 안건 id로 상세를 보여주도록 개선 ──
P7_OLD = """function showBillDetail(name) {
  document.getElementById('modal-ttl').textContent = '안건 상세 — ' + name;
  document.getElementById('modal-body').innerHTML = `<div style="font-size:13px;color:var(--txt2);line-height:1.8">
    <div style="font-weight:700;margin-bottom:8px">안건 전문</div>
    <p style="margin-bottom:12px">「${name}」에 관한 상세 내용이 여기에 표시됩니다. 제안 배경, 찬반 공방 내역, 현재 투표 현황, PDV 기록 링크 등을 확인할 수 있습니다.</p>
    <div style="background:var(--vi-bg);border-radius:8px;padding:10px;font-size:12px;color:var(--vi-dk);border:1px solid var(--vi-bd)">🔐 이 안건의 모든 처리 기록은 PDV에 저장되고 OpenHash로 앵커링됩니다.</div>
  </div>`;
  document.getElementById('modal').classList.add('open');
}"""
P7_NEW = """async function showBillDetail(id) {
  document.getElementById('modal-ttl').textContent = '안건 상세';
  document.getElementById('modal-body').innerHTML = '<div style="padding:12px;color:var(--txt3);font-size:13px">불러오는 중…</div>';
  document.getElementById('modal').classList.add('open');
  const data = await _dawnFetch('/democracy/proposal/' + encodeURIComponent(id));
  const p = data && !data.__error ? data.proposal : null;
  if (!p) {
    document.getElementById('modal-body').innerHTML = '<div style="padding:12px;color:var(--txt3);font-size:13px">안건을 불러오지 못했습니다.</div>';
    return;
  }
  document.getElementById('modal-ttl').textContent = '안건 상세 — ' + p.title;
  document.getElementById('modal-body').innerHTML = `<div style="font-size:13px;color:var(--txt2);line-height:1.8">
    <div style="font-weight:700;margin-bottom:8px">배경·근거</div>
    <p style="margin-bottom:12px;white-space:pre-wrap">${_escHtml(p.background || p.summary || '(작성된 배경 없음)')}</p>
    <div style="background:var(--vi-bg);border-radius:8px;padding:10px;font-size:12px;color:var(--vi-dk);border:1px solid var(--vi-bd)">
      상태: ${_escHtml(p.status)} · 동의 ${p.endorsement_weight_total || 0}/${p.endorsement_threshold || 1000}표
      ${p.status === 'voting' || p.status === 'passed' || p.status === 'rejected' ? ' · 찬성 ' + (p.vote_for_weight || 0) + ' / 반대 ' + (p.vote_against_weight || 0) : ''}
    </div>
  </div>`;
}"""


def main():
    try:
        with open(TARGET, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"오류: {TARGET} 파일을 찾을 수 없습니다. democracy 저장소 루트에서 실행하세요.")
        sys.exit(1)

    steps = [
        (P1_OLD, P1_NEW, "필터바에서 심사 중 제거"),
        (P2_OLD, P2_NEW, "하드코딩 샘플 안건 제거"),
        (P3_OLD, P3_NEW, "의결 참여 패널 정직화"),
        (P4_OLD, P4_NEW, "submitBill 실제 백엔드 연동"),
        (P5_OLD, P5_NEW, "DAWN 실시간 연동 코드 삽입"),
        (P6_OLD, P6_NEW, "show() 진입시 실시간 로드"),
        (P7_OLD, P7_NEW, "안건 상세 실데이터 연동"),
    ]

    all_skipped = True
    for old, new, label in steps:
        content, skipped = replace_unique(content, old, new, label)
        all_skipped = all_skipped and skipped

    if all_skipped:
        print("변경 사항이 없어 파일을 다시 쓰지 않습니다.")
        sys.exit(0)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"완료: {TARGET}이 실제 공중 게시판(worker.js /democracy/*)과 연동되도록 갱신했습니다.")
    print("주의: gopang의 worker.js DAWN 패치 + pb_migrations 3종이 먼저 배포돼 있어야 정상 동작합니다.")


if __name__ == "__main__":
    main()
