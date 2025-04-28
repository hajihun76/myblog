document.addEventListener('DOMContentLoaded', function() {
  const img = document.getElementById('responsiveImg');
  if (!img) return;

  function setOrientationClass() {
    if (img.naturalWidth >= img.naturalHeight) {
      img.style.width = '100%';
      img.style.height = 'auto';
    } else {
      img.style.width = 'auto';
      img.style.height = '80vh';
    }
  }

  if (img.complete) {
    setOrientationClass();
  } else {
    img.onload = setOrientationClass;
  }
});
