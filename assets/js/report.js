/* 지역별 요약 리포트 */
(function () {
  'use strict';

  var SCHOOLS = window.SCHOOLS || [];
  var DATA_META = window.DATA_META || {};

  var KIND_ORDER = ['공립', '사립', '국립'];
  var REGION_ORDER = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
    '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주'];

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function count(list, pred) {
    return list.filter(pred).length;
  }

  /* ---------- 핵심 지표 타일 ---------- */
  var priv = count(SCHOOLS, function (f) { return f.kind === '사립'; });
  var branch = count(SCHOOLS, function (f) { return f.isBranch; });
  var regionCount = {};
  SCHOOLS.forEach(function (f) { regionCount[f.region] = true; });
  var tiles = [
    { num: SCHOOLS.length, lbl: '전체 학교' },
    { num: Object.keys(regionCount).length, lbl: '지역' },
    { num: priv, lbl: '사립' },
    { num: branch, lbl: '분교' }
  ];
  document.getElementById('statTiles').innerHTML = tiles.map(function (t) {
    return '<div class="stat-tile"><div class="num">' + t.num + '</div><div class="lbl">' + t.lbl + '</div></div>';
  }).join('');

  /* ---------- 설립 구분 ---------- */
  var kindCounts = {};
  SCHOOLS.forEach(function (f) {
    kindCounts[f.kind] = (kindCounts[f.kind] || 0) + 1;
  });
  document.getElementById('kindChips').innerHTML = KIND_ORDER
    .filter(function (k) { return kindCounts[k]; })
    .map(function (k) {
      return '<span class="status-chip"><span class="tag">' + esc(k) + '</span>' +
        '<span class="chip-num">' + kindCounts[k] + '곳</span></span>';
    }).join('');

  /* ---------- 지역별 막대 차트 ---------- */
  var byRegion = {};
  SCHOOLS.forEach(function (f) {
    (byRegion[f.region] = byRegion[f.region] || []).push(f);
  });
  var entries = REGION_ORDER
    .filter(function (r) { return byRegion[r]; })
    .map(function (r) { return [r, byRegion[r].length]; });
  entries.sort(function (a, b) { return b[1] - a[1]; });
  var max = entries.length ? entries[0][1] : 1;
  document.getElementById('regionBars').innerHTML = entries.map(function (e) {
    return (
      '<button class="dbar" data-region="' + esc(e[0]) + '" title="지도에서 ' + esc(e[0]) + ' 보기">' +
        '<span>' + esc(e[0]) + '</span>' +
        '<span class="track"><span class="fill" style="width:' + (e[1] / max * 100) + '%"></span></span>' +
        '<span class="cnt">' + e[1] + '</span>' +
      '</button>'
    );
  }).join('');

  document.getElementById('regionBars').addEventListener('click', function (e) {
    var dbar = e.target.closest('.dbar');
    if (dbar) {
      location.href = 'index.html?region=' + encodeURIComponent(dbar.getAttribute('data-region'));
    }
  });

  /* ---------- 지역별 상세 표 ---------- */
  var tbody = document.querySelector('#reportTable tbody');
  tbody.innerHTML = entries.map(function (e) {
    var r = e[0], list = byRegion[r];
    return (
      '<tr>' +
        '<td>' + esc(r) + '</td>' +
        '<td>' + list.length + '</td>' +
        '<td>' + count(list, function (f) { return f.kind === '공립'; }) + '</td>' +
        '<td>' + count(list, function (f) { return f.kind === '사립'; }) + '</td>' +
        '<td>' + count(list, function (f) { return f.kind === '국립'; }) + '</td>' +
        '<td>' + count(list, function (f) { return f.isBranch; }) + '</td>' +
      '</tr>'
    );
  }).join('');

  /* ---------- 서울 지역 리포트: 학생수 랭킹 ---------- */
  var seoulRanked = SCHOOLS.filter(function (f) { return f.region === '서울' && f.studentCount != null; });
  document.getElementById('seoulRankCount').textContent = seoulRanked.length;

  function renderSeoulRank(order) {
    var sorted = seoulRanked.slice().sort(function (a, b) {
      return order === 'asc' ? a.studentCount - b.studentCount : b.studentCount - a.studentCount;
    });
    var tbody = document.querySelector('#seoulRankTable tbody');
    tbody.innerHTML = sorted.map(function (f, i) {
      return (
        '<tr>' +
          '<td>' + (i + 1) + '</td>' +
          '<td style="text-align:left">' + esc(f.name) + '</td>' +
          '<td>' + esc(f.district) + '</td>' +
          '<td>' + esc(f.kind) + '</td>' +
          '<td>' + f.studentCount + '명</td>' +
          '<td>' + (f.classCount != null ? f.classCount + '학급' : '') + '</td>' +
        '</tr>'
      );
    }).join('');
  }
  renderSeoulRank('desc');

  var sortDescBtn = document.getElementById('sortDescBtn');
  var sortAscBtn = document.getElementById('sortAscBtn');
  [sortDescBtn, sortAscBtn].forEach(function (btn) {
    btn.addEventListener('click', function () {
      sortDescBtn.classList.toggle('active', btn === sortDescBtn);
      sortAscBtn.classList.toggle('active', btn === sortAscBtn);
      renderSeoulRank(btn.getAttribute('data-order'));
    });
  });

  /* ---------- 헤더 ---------- */
  document.getElementById('totalCount').textContent = SCHOOLS.length;
  document.getElementById('surveyDate').textContent = DATA_META.surveyDate || '';

  // PWA: 서비스 워커 등록 (홈 화면 설치 · 오프라인 지원)
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function (err) {
        console.warn('서비스 워커 등록 실패:', err);
      });
    });
  }
})();
