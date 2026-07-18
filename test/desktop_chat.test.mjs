import { test, describe, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { JSDOM } from 'jsdom';
import fs from 'node:fs';

// desktop.html의 AI 채팅(chatSend)이 이전엔 api.anthropic.com을 키 없이
// 직접 호출해서 항상 실패하는 죽은 코드였다. 이 저장소 안에서 이미
// 검증된 DEEPSEEK_PROXY+'/chat/completions' 패턴으로 교체한 뒤,
// 실제로 그 엔드포인트가 호출되고 응답이 올바르게 파싱되는지 확인한다.

describe('democracy/desktop.html — chatSend() 프록시 경유 수정 확인', () => {
  let dom, requests;

  before(() => {
    requests = [];
    dom = new JSDOM(`<!doctype html><html><body>
      <div id="chat-body"></div>
      <input id="chat-input">
      <button id="chat-send-btn"></button>
    </body></html>`, { runScripts: 'outside-only', url: 'https://kdemocracy.hondi.net/desktop.html' });

    dom.window.fetch = async (url, opts) => {
      requests.push({ url: String(url), body: opts?.body ? JSON.parse(opts.body) : null });
      return {
        ok: true,
        json: async () => ({ choices: [{ message: { content: '민주주의 관련 답변입니다.' } }] }),
      };
    };
    dom.window.PDV = { writeConsult: () => {} };

    const html = fs.readFileSync(new URL('../desktop.html', import.meta.url), 'utf-8');
    const lines = html.split('\n');
    // SYS 선언(1310)부터 addBubble 끝(1373 부근)까지 + DEEPSEEK_PROXY/MODEL(1398-1399)만
    // 추출한다 — 같은 <script> 블록의 나머지 코드(페이지 전반 UI 배선)는
    // 이 테스트가 만든 최소 DOM에 없는 요소를 참조해 무관하게 실패한다.
    const chatSendStart = lines.findIndex(l => l.startsWith('const SYS ='));
    const addBubbleEnd  = lines.findIndex((l, i) => i > chatSendStart && l.trim() === '}' && lines[i-1]?.includes('return id;'));
    const proxyLine     = lines.findIndex(l => l.startsWith('const DEEPSEEK_PROXY'));
    const modelLine     = lines.findIndex(l => l.startsWith('const DEEPSEEK_MODEL'));
    if (chatSendStart < 0 || addBubbleEnd < 0 || proxyLine < 0) {
      throw new Error('desktop.html 구조가 바뀌어 대상 코드를 못 찾음 — 테스트 갱신 필요');
    }
    const snippet = [
      lines[proxyLine], lines[modelLine],
      ...lines.slice(chatSendStart, addBubbleEnd + 1),
    ].join('\n');
    dom.window.eval(snippet);
  });

  after(() => { dom.window.close(); });

  test('취약점 수정 확인: api.anthropic.com을 실제로 호출하는 코드가 없다(설명 주석 속 언급은 무관)', () => {
    const html = fs.readFileSync(new URL('../desktop.html', import.meta.url), 'utf-8');
    assert.equal(/fetch\(\s*['"]https:\/\/api\.anthropic\.com/.test(html), false);
  });

  test('chatSend()가 DEEPSEEK_PROXY/chat/completions를 올바른 페이로드로 호출한다', async () => {
    dom.window.document.getElementById('chat-input').value = '안건 제안은 어떻게 하나요?';
    await dom.window.chatSend();

    assert.equal(requests.length, 1);
    assert.equal(requests[0].url, 'https://hondi-proxy.tensor-city.workers.dev/chat/completions');
    assert.equal(requests[0].body.service_id, 'kdemocracy');
    assert.equal(requests[0].body.messages[0].role, 'system');
    assert.equal(requests[0].body.messages.at(-1).content, '안건 제안은 어떻게 하나요?');
  });

  test('응답(choices[0].message.content)이 채팅창에 정상 렌더링된다', () => {
    const body = dom.window.document.getElementById('chat-body').innerHTML;
    assert.match(body, /민주주의 관련 답변입니다/);
  });
});
