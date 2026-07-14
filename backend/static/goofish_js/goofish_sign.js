// 闲鱼 sign 签名算法 - 逆向 JS 占位文件
// 实际使用时需要替换为真实的逆向 JS 代码
// 输入: JSON {params: {...}, cookie: "..."}
// 输出: JSON {sign: "..."}

const readline = require('readline');

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

        // TODO: 替换为真实的闲鱼 sign 签名算法
        // 这里生成一个模拟签名用于开发和测试
        const mockSign = generateMockSign(params, cookie);

        console.log(JSON.stringify({sign: mockSign}));
    } catch (e) {
        console.error('Error:', e.message);
        process.exit(1);
    }
    rl.close();
});

function generateMockSign(params, cookie) {
    // 模拟签名生成 - 实际使用时替换为真实的逆向算法
    const ts = params.ts || Date.now().toString();
    const data = ts + cookie.substring(0, 20);
    // 简单的哈希模拟
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
        const char = data.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return 'mock_sign_' + Math.abs(hash).toString(16) + '_' + ts;
}