document.addEventListener('DOMContentLoaded', function() {
  const fileInput = document.getElementById('id_thumb') || document.getElementById('id_image');
  const previewWrapper = document.getElementById('preview-wrapper');
  const previewImg = document.getElementById('image-preview');

  if (!fileInput || !previewImg) {
    console.error('fileInput 또는 previewImg를 찾지 못했습니다.');
    return;
  }

  fileInput.addEventListener('change', function() {
    const file = this.files[0];
    if (!file) {
      if (previewWrapper) previewWrapper.style.display = 'none';
      previewImg.src = '';
      return;
    }
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    if (previewWrapper) previewWrapper.style.display = 'block';
    previewImg.onload = () => URL.revokeObjectURL(url);
  });
});
