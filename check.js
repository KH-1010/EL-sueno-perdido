const fs = require('fs');
const html = fs.readFileSync('C:/Users/KH/Downloads/files/index.html', 'utf8');
const start = html.indexOf('// CLASSIC GAMES LIBRARY');
const end = html.indexOf('</script>', start);
const script = html.substring(start, end);
try {
    new Function(script);
    console.log('Script syntax OK');
} catch(e) {
    console.log('SYNTAX ERROR:', e.message);
}
