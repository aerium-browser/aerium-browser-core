const IDENTITY_HEADINGS = [
  'Environment',
  'Aerium version',
  'Device and Android version',
];

const NARRATIVE_HEADINGS = [
  'Description',
  'Steps to reproduce',
  'What you expected, and what happened instead',
  'What problem does this solve?',
  'What should Aerium do?',
];

const FEATURE_HEADINGS = [
  'What problem does this solve?',
  'What should Aerium do?',
];

const FEATURE_LABELS = ['enhancement', 'documentation'];

const CRASH_WORDS = new RegExp(
  [
    String.raw`\bcrash(?:es|ed|ing)?\b`,
    String.raw`\bforce[- ]?clos(?:e|es|ed|ing)\b`,
    String.raw`\bkeeps? stopping\b`,
    String.raw`\b(?:has|keeps|kept) stopped\b`,
    String.raw`\bclos(?:es|ed|ing) (?:by )?itself\b`,
    'クラッシュ',
    '強制終了',
    '闪退',
    '崩溃',
    'çök',
    'abstürz',
    'stürzt ab',
    'вылет',
  ].join('|'),
  'i',
);

const NEGATED_CRASH = new RegExp(
  String.raw`\b(?:no|not|never|without|nor|doesn['’]?t|does not|don['’]?t|didn['’]?t|won['’]?t|isn['’]?t|wasn['’]?t)\s+(?:\w+\s+){0,2}crash\w*`,
  'gi',
);

const STACK_TRACE = new RegExp(
  [
    'FATAL EXCEPTION',
    'AndroidRuntime',
    String.raw`Fatal signal \d+`,
    String.raw`signal \d+ \(SIG[A-Z]+\)`,
    'Abort message',
    String.raw`\*\*\* \*\*\* \*\*\*`,
    String.raw`^\s*#\d{2,} pc [0-9a-f]+`,
    String.raw`^\s*at [\w$.<>]+\([^)]*\)`,
    String.raw`Caused by: [\w$.]+`,
    'beginning of crash',
  ].join('|'),
  'im',
);

const ATTACHED_LOG = new RegExp(
  String.raw`https://github\.com/(?:user-attachments/files|[\w.-]+/[\w.-]+/files)/\d+/\S+\.(?:txt|log|zip|gz)\b`,
  'i',
);

function claimsCrash(title, body) {
  const text = `${title} ${strip(body)}`.replace(NEGATED_CRASH, ' ');
  return CRASH_WORDS.test(text);
}

function hasCrashLog(body) {
  return STACK_TRACE.test(String(body)) || ATTACHED_LOG.test(String(body));
}

function parseSections(body) {
  const sections = new Map();
  let heading = null;
  let buffer = [];
  const flush = () => {
    if (heading !== null) {
      sections.set(heading, buffer.join('\n'));
    }
  };
  for (const line of String(body).split(/\r?\n/)) {
    const match = /^#{2,4}\s+(.+?)\s*$/.exec(line);
    if (match) {
      flush();
      heading = match[1];
      buffer = [];
    } else if (heading !== null) {
      buffer.push(line);
    }
  }
  flush();
  return sections;
}

function strip(text) {
  return String(text)
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/^\s*[-*]\s*\[[xX ]\]\s.*$/gm, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/<img[^>]*>/gi, ' ')
    .replace(/<\/?[a-z][^>]*>/gi, ' ')
    .replace(/https?:\/\/\S+/g, ' ')
    .replace(/^#{1,6}\s.*$/gm, ' ')
    .replace(/_No response_/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function codeVolume(body) {
  return (String(body).match(/```[\s\S]*?```/g) || []).join(' ').trim().length;
}

function evaluate({ title = '', body = '', labels = [], strict = false } = {}) {
  const sections = parseSections(body);
  const names = new Set(sections.keys());

  const isFeature =
    FEATURE_HEADINGS.some((h) => names.has(h)) ||
    labels.some((l) => FEATURE_LABELS.includes(l));

  const required = isFeature
    ? NARRATIVE_HEADINGS
    : IDENTITY_HEADINGS.concat(NARRATIVE_HEADINGS);

  const blank = required.filter(
    (h) => names.has(h) && strip(sections.get(h)).length === 0,
  );
  if (blank.length > 0) {
    return { sufficient: false, reason: 'blank-required-field', blank };
  }

  if (!isFeature && claimsCrash(title, body) && !hasCrashLog(body)) {
    return { sufficient: false, reason: 'crash-without-log', blank: [] };
  }

  const prose = strip(body).length;
  const code = codeVolume(body);

  if (code >= 120) {
    return { sufficient: true, reason: 'ok', blank: [] };
  }

  if (strict && names.size === 0) {
    return { sufficient: false, reason: 'no-template', blank: [] };
  }

  if (prose >= 60) {
    return { sufficient: true, reason: 'ok', blank: [] };
  }

  return { sufficient: false, reason: 'too-thin', blank: [] };
}

module.exports = { evaluate, parseSections, strip, codeVolume, claimsCrash, hasCrashLog };
