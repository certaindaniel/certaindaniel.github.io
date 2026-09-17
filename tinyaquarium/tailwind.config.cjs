module.exports = {
    content: ['./tinyaquarium/index.html', './tinyaquarium/vault/index.html'],
    theme: {
        extend: {
            colors: {
                deepOcean: '#071626',
                midnightNavy: '#0c2238',
                cyanGlow: '#00F0FF',
                coralPink: '#FF5E7E',
                goldAmber: '#FFB800',
                aquariumTeal: '#0E7490',
                glassBg: 'rgba(12, 34, 56, 0.75)'
            },
            fontFamily: {
                sans: ['"Plus Jakarta Sans"', '"Noto Sans TC"', 'sans-serif'],
                mono: ['"JetBrains Mono"', 'monospace']
            }
        }
    }
};
