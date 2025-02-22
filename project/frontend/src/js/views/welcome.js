const buttons = document.getElementsByClassName('ft-btn');

for (let i = 0; i < buttons.length; i += 1) {
    const btn = buttons[i];
    if (!btn.id.startsWith('btn-')){
        continue;
    }
    const target = btn.id.replace('btn-', '');
    btn.addEventListener('click', router);
}