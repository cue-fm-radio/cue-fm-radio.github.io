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

  // ====== 画像モーダルの処理 ======
  const viewer = document.getElementById('image-viewer');
  if (viewer) {
    const viewerImg = viewer.querySelector('img');

    // aタグで囲まれている画像(カードリンク等)とスプラッシュのロゴを除外して全ての画像を取得
    const allImages = document.querySelectorAll('img');
    allImages.forEach(img => {
      // 親にaタグがあるか、logoクラスが付いている場合は除外
      if (img.closest('a') || img.classList.contains('logo')) return;

      img.classList.add('clickable-img');
      img.addEventListener('click', () => {
        viewerImg.src = img.src;
        viewer.showModal();
      });
    });

    // ダイアログ自体（枠外の::backdropなど）または画像をクリックしたら閉じる
    viewer.addEventListener('click', () => {
      viewer.close();
    });
  }
});
