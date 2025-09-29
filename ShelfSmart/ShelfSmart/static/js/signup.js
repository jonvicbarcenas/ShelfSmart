// Simple submit handler and shared focus animation
(function(){
  const form = document.getElementById('signupForm');
  if (form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      const submitBtn = document.querySelector('.btn-primary-wide');
      const original = submitBtn.textContent;
      submitBtn.textContent = 'SIGNING UP...';
      submitBtn.disabled = true;

      fetch(window.location.href, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(r=>r.json())
      .then(data=>{
        if(data.success){
          window.location.href = data.redirect_url || '../login/';
        } else {
          alert(data.error || 'Signup failed. Please try again.');
        }
      })
      .catch(err=>{ console.error(err); alert('An error occurred.'); })
      .finally(()=>{ submitBtn.textContent = original; submitBtn.disabled = false; });
    });
  }

  // Input focus animations
  document.querySelectorAll('.form-input').forEach(input=>{
    input.addEventListener('focus', function(){
      this.style.transform = 'translateY(-2px)';
      this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    });
    input.addEventListener('blur', function(){
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = 'none';
    });
  });

  // Animate panels on page load (right -> left emphasis)
  const rightPanel = document.querySelector('.right-panel');
  const leftPanel = document.querySelector('.left-panel');
  if (rightPanel) rightPanel.classList.add('animate__animated','animate__fadeInLeft');
  if (leftPanel) leftPanel.classList.add('animate__animated','animate__fadeInRight');

  // Back to login with panel-based animation
  const back = document.querySelector('.btn-signin-outline');
  if(back){
    back.addEventListener('click', function(e){
      e.preventDefault();
      if (rightPanel) rightPanel.classList.add('animate__animated','animate__fadeOutRight');
      if (leftPanel) leftPanel.classList.add('animate__animated','animate__fadeOutLeft');
      setTimeout(()=>{ window.location.href = '../login/'; }, 450);
    });
  }
})();
