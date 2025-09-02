// /config.js
(function (w) {
    // w.WEB_BASE = location.origin;          // 协议 + 域名 + 端口
    w.WEB_BASE = "http://10.250.101.238:5000" ||"http://localhost:5000"
    w.API_BASE = w.WEB_BASE + '/api';      // API 前缀
})(window);
