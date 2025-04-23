document.addEventListener('DOMContentLoaded', function() {
  const img = document.getElementById('responsiveImg');

  function setOrientationClass() {
    if (img.naturalWidth >= img.naturalHeight) {
      img.classList.add('landscape');
      img.classList.remove('portrait');
    } else {
      img.classList.add('portrait');
      img.classList.remove('landscape');
    }
  }

  if (img.complete) {
    setOrientationClass();
  } else {
    img.onload = setOrientationClass;
  }
});