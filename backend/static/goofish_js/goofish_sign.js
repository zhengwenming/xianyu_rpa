// 闲鱼 (goofish) mtop x-sign 签名算法
// 淘系标准 h5 签名: sign = md5(token + "&" + t + "&" + appKey + "&" + data)
//   - token : Cookie 中 _m_h5_tk 的前半段（'_' 之前的 token）
//   - t     : 毫秒时间戳
//   - appKey: goofish web 固定值 34839810
//   - data  : mtop 请求体（字符串形式的 JSON）
//
// 输入 (stdin, 一行 JSON):
//   {
//     "params": { "t": "<毫秒时间戳>", "appKey": "34839810", "data": "<data字符串>" },
//     "cookie": "..._m_h5_tk=xxxxx_yyyyy; ..."
//   }
// 输出 (stdout, 一行 JSON):
//   { "sign": "...", "t": "...", "appKey": "..." }
//
// 仅使用 Node.js 内置模块 (crypto)，无需 npm 依赖。

const crypto = require('crypto');
const readline = require('readline');

// goofish web 默认 appKey
const DEFAULT_APP_KEY = '34839810';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false,
});

rl.on('line', (line) => {
    try {
        const input = JSON.parse(line);
        const params = input.params || {};
        const cookie = input.cookie || '';

        const result = generateSign(params, cookie);
        process.stdout.write(JSON.stringify(result) + '\n');
    } catch (e) {
        process.stderr.write('Error: ' + e.message + '\n');
        process.exit(1);
    }
    rl.close();
});

/**
 * 从 Cookie 字符串中提取 _m_h5_tk 的 token 部分（'_' 前的一段）。
 * _m_h5_tk 形如 "<token>_<expireTime>"，签名只用 token 部分。
 */
function extractToken(cookie) {
    const match = /_m_h5_tk=([^;]+)/.exec(cookie || '');
    if (!match) return '';
    return match[1].split('_')[0];
}

function md5(str) {
    return crypto.createHash('md5').update(str, 'utf8').digest('hex');
}

function generateSign(params, cookie) {
    const token = extractToken(cookie);
    const t = String(params.t || params.ts || Date.now());
    const appKey = String(params.appKey || DEFAULT_APP_KEY);

    // data 必须是字符串；若调用方传了对象则序列化
    let data = params.data;
    if (data === undefined || data === null) {
        data = '';
    } else if (typeof data !== 'string') {
        data = JSON.stringify(data);
    }

    // 淘系 h5 签名规则: md5(token&t&appKey&data)
    const raw = token + '&' + t + '&' + appKey + '&' + data;
    const sign = md5(raw);

    return { sign, t, appKey };
}