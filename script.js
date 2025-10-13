window.addEventListener('load', () => {
  const splash = document.getElementById('splash');
  const main = document.getElementById('main-content');

  // 2秒後にスプラッシュをフェードアウト
  setTimeout(() => {
    splash.style.opacity = '0';
    setTimeout(() => {
      splash.style.display = 'none';
      main.classList.remove('hidden');
      main.style.opacity = '1';
    }, 1000); // スプラッシュが完全に消えるまで1秒待つ
  }, 2000);
});
